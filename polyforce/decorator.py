import inspect
import typing
from typing import Any, _SpecialForm

from typing_extensions import get_args

from polyforce.constants import CLASS_SPECIAL_WORDS
from polyforce.exceptions import MissingAnnotation, ReturnSignatureMissing


class polycheck:
    def __init__(self, ignore: bool = False, ignored_types: Any = None) -> None:
        """
        Initialize the PolyCheck decorator.

        Args:
            ignore (bool): If True, type checking is bypassed.
            ignored_types (Union[type, Tuple[type, ...]]): Types to be ignored during type checking.
        """
        self.ignore = ignore
        self.ignored_types = tuple(ignored_types) if ignored_types is not None else ()
        self.args_spec = None

    def check_signature(self, func: Any) -> Any:
        """
        Validates the signature of a function and corresponding annotations
        of the parameters.

        Args:
            func (Any): The function to validate.
        """
        if inspect.isclass(func):
            return func

        signature: inspect.Signature = inspect.signature(func)
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
        params = dict(zip(self.args_spec.parameters, args))  # type: ignore
        params.update(kwargs)

        for name, value in params.items():
            type_hint = self.args_spec.parameters[name].annotation  # type: ignore

            if (
                isinstance(type_hint, _SpecialForm)
                or type_hint is Any
                or type_hint in self.ignored_types
            ):
                continue

            actual_type = self.get_actual_type(type_hint=type_hint, value=value)
            if not isinstance(value, actual_type) and not self.ignore:
                raise TypeError(
                    f"Expected type '{type_hint}' for attribute '{name}'"
                    f" but received type '{type(value)}' instead."
                )

    def get_actual_type(self, type_hint: Any, value: Any) -> Any:
        """
        Determine the actual type hint for a given parameter based on its value.

        Args:
            type_hint (Any): The type hint for the parameter.
            value (Any): The parameter's value.

        Returns:
            Any: The actual type hint.
        """
        actual_type = type_hint

        if hasattr(type_hint, "__origin__"):
            actual_type = type_hint.__origin__

        if isinstance(actual_type, typing._SpecialForm):
            actual_type = (
                get_args(type_hint) if hasattr(type_hint, "__origin__") else type_hint.__args__
            )

        return actual_type

    def __call__(self, fn: Any) -> Any:
        """
        Call method to apply the decorator to a function.

        Args:
            fn (Any): The function to decorate.

        Returns:
            Any: The decorated function.
        """
        self.args_spec = inspect.signature(fn)  # type: ignore

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            self.check_signature(fn)
            self.check_types(*args, **kwargs)
            return fn(*args, **kwargs)

        return wrapper
