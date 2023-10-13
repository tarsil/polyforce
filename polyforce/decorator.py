import inspect
from itertools import islice
from typing import Any, Dict, List, Union, _SpecialForm

from typing_extensions import get_args

from polyforce.constants import CLASS_SPECIAL_WORDS
from polyforce.exceptions import MissingAnnotation, ReturnSignatureMissing, ValidationError

from ._internal._errors import ErrorDetail
from ._internal._serializer import json_serializable


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
        self.fn_name = None
        self.is_class_or_object: bool = False
        self.class_or_object: Any = None

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

    def check_types(self, *args: Any, **kwargs: Any) -> Any:
        """
        Validate the types of function parameters.

        Args:
            *args (Any): Positional arguments.
            **kwargs (Any): Keyword arguments.
        """
        merged_params: Dict[str, inspect.Signature] = {}
        arg_params = (
            self.args_spec.parameters if not self.signature else self.signature.parameters.values()
        )
        if self.is_class_or_object:
            func_type = inspect.getattr_static(self.class_or_object, self.fn_name)

            # classmethod and staticmethod do not use the "self".
            if not isinstance(func_type, (classmethod, staticmethod)):
                func_params = (
                    list(islice(arg_params.values(), 1, None))
                    if not self.signature
                    else list(arg_params)
                )
                merged_params = {param.name: param for param in func_params}
        else:
            merged_params = arg_params

        params = dict(zip(merged_params, args))
        params.update(kwargs)

        for name, value in params.items():
            type_hint = self.args_spec.parameters[name].annotation  # type: ignore

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
                error_message: str = (
                    f"Expected '{expected_value}' for attribute '{name}', "
                    f"but received type '{type(value).__name__}'."
                )
                error: ErrorDetail = ErrorDetail(
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
        if hasattr(type_hint, "__origin__"):
            return get_args(type_hint)
        return type_hint

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
            self.check_types(*arguments, **kwargs) if self.signature else self.check_types(
                *args, **kwargs
            )
            return fn(*args, **kwargs)

        return wrapper
