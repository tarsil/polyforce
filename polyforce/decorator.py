import inspect
import typing
from typing import Any, Union, _SpecialForm

from typing_extensions import get_args, get_origin

from polyforce.constants import CLASS_SPECIAL_WORDS
from polyforce.exceptions import MissingAnnotation, ReturnSignatureMissing


class polycheck:
    def __init__(self, ignore: bool = False, ignored_types: Any = None) -> None:
        self.wrapped: Any
        self.ignore = ignore

        if ignored_types is not None:
            assert isinstance(
                ignored_types, (tuple, list)
            ), "`ignored_types` must be a tuple or a list"

        self.ignored_types = ignored_types or ()
        self.args_spec: Union[inspect.FullArgSpec, None] = None

    def check_signature(self, func: Any) -> Any:
        """
        Validates the signature of a function and corresponding annotations
        of the parameters.
        """
        if inspect.isclass(func):
            return func

        signature: inspect.Signature = inspect.Signature.from_callable(func)
        if signature.return_annotation == inspect.Signature.empty:
            raise ReturnSignatureMissing(func=func.__name__)

        for name, parameter in signature.parameters.items():
            if name not in CLASS_SPECIAL_WORDS and parameter.annotation == inspect.Signature.empty:
                raise MissingAnnotation(name=name)

    def check_types(self, *args: Any, **kwargs: Any) -> Any:
        params = dict(zip(self.args_spec.args, args))
        params.update(kwargs)

        for name, value in params.items():
            type_hint = self.args_spec.annotations.get(name, Any)

            if (
                isinstance(type_hint, _SpecialForm)
                or type_hint == Any
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
        Checks for all the version of python.
        """
        if hasattr(type_hint, "__origin__"):
            actual_type = type_hint.__origin__
        else:
            actual_type = get_origin(type_hint)

        # For versions prior to python 3.10
        if isinstance(actual_type, typing._SpecialForm):
            actual_type = (
                get_args(value) if not hasattr(type_hint, "__origin__") else type_hint.__args__
            )
        return actual_type or type_hint

    def __call__(self, fn: "Any") -> Any:
        self.wrapped = fn
        self.args_spec = inspect.getfullargspec(self.wrapped)

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            self.check_signature(self.wrapped)
            self.check_types(*args, **kwargs)
            return self.wrapped(*args, **kwargs)

        return wrapper
