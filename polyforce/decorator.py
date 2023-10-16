import inspect
from itertools import islice
from typing import Any, Dict, List, Union, _SpecialForm

from polyforce.constants import CLASS_SPECIAL_WORDS
from polyforce.exceptions import MissingAnnotation, ReturnSignatureMissing, ValidationError
from polyforce.fields import PolyField

from ._internal._errors import ErrorDetail
from ._internal._serializer import json_serializable
from .core._polyforce_core import PolyforceUndefined


class polycheck:
    def __init__(
        self,
        signature: Union[inspect.Signature, None] = None,
        ignore: bool = False,
        ignored_types: Any = None,
    ) -> None:
        """
        Initialize the PolyCheck decorator.

        Args:
            signature (bool): A signature previously generated.
            ignore (bool): If True, type checking is bypassed.
            ignored_types (Union[type, Tuple[type, ...]]): Types to be ignored during type checking.
        """
        self.ignore = ignore
        self.ignored_types = tuple(ignored_types) if ignored_types is not None else ()
        self.args_spec = None
        self.signature = signature
        self.fn_name: str = None
        self.is_class_or_object: bool = False
        self.class_or_object: Any = None
        self.poly_fields: Dict[str, Dict[str, PolyField]] = {}

    def check_signature(self, func: Any) -> Any:
        """
        Validates the signature of a function and corresponding annotations
        of the parameters.

        Args:
            func (Any): The function to validate.
        """
        if inspect.isclass(func):
            return func

        signature: inspect.Signature = self.signature or inspect.signature(func)
        if signature.return_annotation == inspect.Signature.empty:
            raise ReturnSignatureMissing(func=func.__name__)

        for name, parameter in signature.parameters.items():
            if name not in CLASS_SPECIAL_WORDS and parameter.annotation == inspect.Parameter.empty:
                raise MissingAnnotation(name=name)

    def generate_polyfields(self) -> Dict[str, Dict[str, "PolyField"]]:
        """
        For all the fields found in the signature, it will generate
        PolyField type variable.
        """
        for parameter in self.args_spec.parameters.values():
            if not isinstance(parameter.default, PolyField):
                data = {
                    "annotation": parameter.annotation,
                    "name": parameter.name,
                    "default": PolyforceUndefined
                    if parameter.default == inspect.Signature.empty
                    else parameter.default,
                }
                field = PolyField(**data)
            else:
                field = parameter.default
                field.annotation = parameter.annotation
                field.name = parameter.name
                field._validate_default_with_annotation()

            field_data = {parameter.name: field}

            if self.fn_name not in self.poly_fields:
                self.poly_fields[self.fn_name] = {}

            self.poly_fields[self.fn_name].update(field_data)
        return self.poly_fields

    def check_types(self, *args: Any, **kwargs: Any) -> Any:
        """
        Validate the types of function parameters.

        Args:
            *args (Any): Positional arguments.
            **kwargs (Any): Keyword arguments.
        """
        merged_params: Dict[str, PolyField] = {}
        if self.is_class_or_object:
            func_type = inspect.getattr_static(self.class_or_object, self.fn_name)

            # classmethod and staticmethod do not use the "self".
            if not isinstance(func_type, (classmethod, staticmethod)):
                func_params = list(
                    islice(self.poly_fields.get(self.fn_name, {}).values(), 1, None)
                )
                merged_params = {param.name: param for param in func_params}
        else:
            merged_params = self.poly_fields[self.fn_name]

        params = dict(zip(merged_params, args))
        params.update(kwargs)

        for name, value in params.items():
            field: PolyField = self.poly_fields[self.fn_name][name]
            type_hint = field.annotation

            if (
                isinstance(type_hint, _SpecialForm)
                or type_hint is Any
                or type_hint in self.ignored_types
            ):
                continue

            actual_type = self.get_actual_type(type_hint=type_hint)

            if isinstance(actual_type, tuple):
                if any(value == Any for value in actual_type):
                    continue

            if not isinstance(value, actual_type) and not self.ignore:
                expected_value = (
                    tuple(value.__name__ for value in actual_type)
                    if isinstance(actual_type, tuple)
                    else actual_type.__name__
                )
                error_message = (
                    f"Expected '{expected_value}' for attribute '{name}', "
                    f"but received type '{type(value).__name__}'."
                )
                error = ErrorDetail(
                    source=self.fn_name,
                    value=json_serializable(value),
                    input=name,
                    expected=expected_value,
                    message=error_message,
                )
                raise ValidationError.from_exception_data([error])

    def get_actual_type(self, type_hint: Any) -> Any:
        """
        Determine the actual type hint for a given parameter based on its value.

        Args:
            type_hint (Any): The type hint for the parameter.
            value (Any): The parameter's value.

        Returns:
            Any: The actual type hint.
        """
        origin = getattr(type_hint, "__origin__", type_hint)
        if isinstance(origin, _SpecialForm):
            origin = type_hint.__args__
        return origin

    def __call__(self, fn: Any) -> Any:
        """
        Call method to apply the decorator to a function.

        Args:
            fn (Any): The function to decorate.

        Returns:
            Any: The decorated function.
        """
        self.args_spec = self.signature or inspect.signature(fn)  # type: ignore
        self.fn_name = fn.__name__

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """
            The wrapper covers for the decorator as individual as
            well as coming from the classes.

            When a signature is usually provided, the first argument is the class itself and therefore excluded.
            """
            arguments: List[Any] = []

            # For the signature being passed and
            # to cover the decorator inside a class
            if self.signature or len(args) == 1:
                arguments = list(args)
                arguments = arguments[1:]
                self.is_class_or_object = True
                self.class_or_object = args[0]

            self.check_signature(fn)
            self.generate_polyfields()
            self.check_types(*arguments, **kwargs) if self.signature else self.check_types(
                *args, **kwargs
            )
            return fn(*args, **kwargs)

        return wrapper
