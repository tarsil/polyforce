import inspect
from abc import ABCMeta
from inspect import Parameter, Signature
from itertools import islice
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Dict,
    List,
    Set,
    Tuple,
    Type,
    Union,
    _SpecialForm,
    cast,
)

from typing_extensions import dataclass_transform

from polyforce.exceptions import MissingAnnotation, ReturnSignatureMissing, ValidationError

from ..constants import INIT_FUNCTION, SPECIAL_CHECK
from ..core._polyforce_core import PolyforceUndefined
from ..decorator import polycheck
from ..fields import Field, PolyField
from ._config import ConfigWrapper
from ._errors import ErrorDetail
from ._serializer import json_serializable

if TYPE_CHECKING:
    from ..main import PolyModel


object_setattr = object.__setattr__


@dataclass_transform(kw_only_default=True, field_specifiers=(Field,))
class PolyMetaclass(ABCMeta):
    """
    Base metaclass used for the PolyModel objects
    and applies all static type checking needed
    for all the functions and methods of a given class.
    """

    __filtered_functions__: Set[str]
    __signature__: ClassVar[Dict[str, Signature]] = {}

    def __new__(
        cls: Type["PolyMetaclass"],
        name: str,
        bases: Tuple[Type],
        attrs: Dict[str, Any],
        **kwargs: Any,
    ) -> Type["PolyModel"]:
        """
        Create a new class using the PolyMetaclass.

        Args:
            cls (Type["PolyMetaclass"]): The metaclass.
            name (str): The name of the class.
            bases (Tuple[Type]): The base classes.
            attrs (Dict[str, Any]): The class attributes.

        Returns:
            Type["PolyModel"]: The new class.

        This method creates a new class using the PolyMetaclass and applies static type checking.
        """
        if bases:
            base_class_vars = cls._collect_data_from_bases(bases)
            config_wrapper = ConfigWrapper.for_model(bases, attrs)

            attrs["config"] = config_wrapper.config
            attrs["__class_vars__"] = base_class_vars

            model = cast("Type[PolyModel]", super().__new__(cls, name, bases, attrs))
            parents = [parent for parent in bases if isinstance(parent, PolyMetaclass)]
            if not parents:
                return model

            model.__polymodel_custom_init__ = not getattr(
                model.__init__, "__polymodel_base_init__", False
            )
            # Making sure the PolyFields are only from this class object.
            model.poly_fields = {}
            model.__signature__ = {}
            complete_poly_class(model, bases, config_wrapper)
            return model
        return cast("Type[PolyModel]", super().__new__(cls, name, bases, attrs))

    @staticmethod
    def _collect_data_from_bases(bases: Tuple[Type]) -> Set[str]:
        """
        Collect class variables from base classes.

        Args:
            bases (Tuple[Type]): Base classes.

        Returns:
            Set[str]: Set of class variables.

        This method collects class variables from the base classes.
        """
        from ..main import PolyModel

        class_vars: Set[str] = set()

        for base in bases:
            if issubclass(base, PolyModel) and base is not PolyModel:
                class_vars.update(base.__class_vars__)
        return class_vars

    def __getattribute__(self, name: str) -> Any:
        """
        Get an attribute with static type checking.

        Args:
            name (str): The name of the attribute to access.

        Returns:
            Any: The value of the attribute.

        Raises:
            AttributeError: If the attribute does not exist.

        Example:
        ```
        obj = MyObject(42)
        value = obj.value  # Accessing the 'value' attribute
        ```
        """
        try:
            func = super().__getattribute__(name)
            __signature__: Dict[str, Any] = super().__getattribute__("__signature__")
            signature: Union[Signature, None] = __signature__.get(name, None)

            if signature is not None and name not in SPECIAL_CHECK:
                return self._add_static_type_checking(func, signature)
            else:
                return func
        except (KeyError, AttributeError):
            return object.__getattribute__(self, name)

    def _extract_type_hint(self, type_hint: Union[Type, tuple]) -> Any:
        """
        Extracts the base type from a type hint, considering typing extensions.

        This function checks if the given type hint is a generic type hint and extracts
        the base type. If not, it returns the original type hint.

        Args:
            type_hint (Union[Type, tuple]): The type hint to extract the base type from.

        Returns:
            Union[Type, tuple]: The base type of the type hint or the original type hint.

        Example:
        ```
        from typing import List, Union

        # Extract the base type from a List hint
        base_type = extract_type_hint(List[int])  # Returns int

        # If the hint is not a generic type, it returns the original hint
        original_hint = extract_type_hint(Union[int, str])  # Returns Union[int, str]
        ```
        """

        origin = getattr(type_hint, "__origin__", type_hint)
        if isinstance(origin, _SpecialForm):
            origin = type_hint.__args__  # type: ignore
        return origin

    def _add_static_type_checking(
        self: Type["PolyModel"], func: Any, signature: Signature
    ) -> Callable:
        """
        Add static type checking to a method or function.

        Args:
            func (Any): The method or function to add type checking to.
            signature (Signature): The method's signature for type checking.

        Returns:
            Callable: A wrapped function with type checking.

        Example:
        ```
        def my_method(self, value: int) -> str:
            return str(value)

        obj = MyObject(42)
        obj.__signature__['my_method'] = inspect.signature(my_method)

        # Accessing 'my_method' will now perform type checking
        result = obj.my_method(42)  # This is valid
        result = obj.my_method("42")  # This will raise a TypeError
        ```
        """

        def polycheck(*args: Any, **kwargs: Any) -> Any:
            bound = signature.bind(*args, **kwargs)
            bound.apply_defaults()

            for name, value in bound.arguments.items():
                if name in self.poly_fields[func.__name__]:
                    field: PolyField = self.poly_fields[func.__name__][name]
                    expected_type = field.annotation

                    if expected_type in (_SpecialForm, Any):
                        continue

                    expected_args = self._extract_type_hint(expected_type)

                    if isinstance(expected_args, tuple):
                        if any(value == Any for value in expected_args):
                            continue

                    if not isinstance(value, expected_args):
                        expected_value = (
                            tuple(value.__name__ for value in expected_args)
                            if isinstance(expected_args, tuple)
                            else expected_args.__name__
                        )
                        error_message: str = (
                            f"Expected '{expected_value}' for attribute '{name}', "
                            f"but received type '{type(value).__name__}'."
                        )
                        error: ErrorDetail = ErrorDetail(
                            source=self.__name__,
                            value=json_serializable(value),
                            input=name,
                            expected=expected_value,
                            message=error_message,
                        )
                        raise ValidationError.from_exception_data([error])

            return func(*args, **kwargs)

        return polycheck


def complete_poly_class(cls: Type["PolyModel"], bases: Tuple[Type], config: ConfigWrapper) -> bool:
    """
    Completes the polyclass model construction and applies all the fields and configurations.

    Args:
        cls (Type[PolyModel]): The PolyModel class to complete.
        config (ConfigWrapper): Configuration wrapper.

    Returns:
        bool: True if the completion was successful.

    This function completes the PolyModel class construction and applies fields and configurations.
    """
    methods: List[str] = [
        attr
        for attr in cls.__dict__.keys()
        if not attr.startswith("__")
        and not attr.endswith("__")
        and inspect.isroutine(getattr(cls, attr))
    ]

    for base in bases:
        if hasattr(base, "__signature__"):
            cls.__signature__.update(base.__signature__)

    if INIT_FUNCTION in cls.__dict__ or (
        INIT_FUNCTION not in cls.__dict__ and INIT_FUNCTION not in cls.__signature__
    ):
        methods.append(INIT_FUNCTION)

    signatures: Dict[str, Signature] = {}

    for method in methods:
        signatures[method] = generate_model_signature(cls, method, config)

    cls.__signature__.update(signatures)

    # Special decorator for the __init__ since it is not manipulated by the
    # __getattribute__ functionality
    if INIT_FUNCTION in cls.__dict__ or (
        INIT_FUNCTION not in cls.__dict__ and INIT_FUNCTION not in cls.__signature__
    ):
        decorate_function(cls, config)

    # Generate the PolyFields
    for value, signature in cls.__signature__.items():
        for param in signature.parameters.values():
            # Generate the PolyField for each function.
            generate_polyfields(cls, value, param)
    return True


def decorate_function(cls: Type["PolyModel"], config: ConfigWrapper) -> None:
    """
    Decorates the __init__ function to make sure it can apply
    the validations upon instantiation.

    The `__init__` is not called inside the `__getattribute__` and therefore
    the polycheck decorator is applied.
    """
    signature: Signature = cls.__signature__["__init__"]
    decorator = polycheck(signature=signature, **config.config)
    init_func = decorator(cls.__init__)
    cls.__init__ = init_func  # type: ignore[method-assign]


def ignore_signature(signature: Signature) -> Signature:
    """
    Ignores the signature and assigns the Any type to all the fields and the return signature.

    Args:
        signature (Signature): The signature to ignore.

    Returns:
        Signature: The modified signature with Any types.

    This function ignores the signature and assigns the Any type to all the fields and the return signature.
    """
    merged_params: Dict[str, Parameter] = {}
    for param in islice(signature.parameters.values(), 1, None):
        param = param.replace(annotation=Any)
        merged_params[param.name] = param
    return Signature(parameters=list(merged_params.values()), return_annotation=Any)


def generate_polyfields(
    cls: Type["PolyModel"], method: str, parameter: Parameter
) -> Dict[str, Dict[str, PolyField]]:
    """
    For all the fields found in the signature, it will generate
    PolyField type variable.

    When generating PolyFields, it matches if there is already a
    PolyField generated by the Field() type.
    """
    if not isinstance(parameter.default, PolyField):
        data = {
            "annotation": parameter.annotation,
            "name": parameter.name,
            "default": PolyforceUndefined
            if parameter.default == Signature.empty
            else parameter.default,
        }

        field = PolyField(**data)
    else:
        field = parameter.default
        field.annotation = parameter.annotation
        field.name = parameter.name
        field._validate_default_with_annotation()

    field_data = {parameter.name: field}

    if method not in cls.poly_fields:
        cls.poly_fields[method] = {}

    cls.poly_fields[method].update(field_data)
    return cls.poly_fields


def generate_model_signature(
    cls: Type["PolyModel"], value: str, config: ConfigWrapper
) -> Signature:
    """
    Generates a signature for each method of the given class.

    Args:
        cls (Type[PolyModel]): The PolyModel class.
        value (str): The method name.
        config (ConfigWrapper): Configuration wrapper.

    Returns:
        Signature: The generated signature.

    This function generates a signature for each method of the given class.
    """
    func = getattr(cls, value)
    func_type = inspect.getattr_static(cls, value)

    signature = Signature.from_callable(func)
    if config.ignore:
        return ignore_signature(signature)

    params = signature.parameters.values()
    merged_params: Dict[str, Parameter] = {}
    if signature.return_annotation == inspect.Signature.empty:
        raise ReturnSignatureMissing(func=value)

    # classmethod and staticmethod do not use the "self".
    if not isinstance(func_type, (classmethod, staticmethod)):
        params = list(islice(params, 1, None))  # type: ignore[assignment]

    for param in params:  # Skip self argument
        if param.annotation == Signature.empty:
            raise MissingAnnotation(name=param.name)

        if param.annotation == Any:
            param = param.replace(annotation=Any)
        elif param.annotation in config.ignored_types:
            param = param.replace(annotation=Any)
        merged_params[param.name] = param

    # Generate the new signature.
    return Signature(
        parameters=list(merged_params.values()), return_annotation=signature.return_annotation
    )
