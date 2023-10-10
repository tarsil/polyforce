import inspect
import typing
from functools import wraps
from typing import Any, _SpecialForm

from typing_extensions import get_args, get_origin

from polyforce.constants import CLASS_SPECIAL_WORDS
from polyforce.exceptions import MissingAnnotation, ReturnSignatureMissing


def polycheck(wrapped: Any) -> Any:
    """
    Special decorator that enforces the
    static typing.

    Checks if all the fields are typed and if the functions have return
    annotations.
    """
    args_spec: inspect.FullArgSpec = inspect.getfullargspec(wrapped)

    def check_signature(func: Any) -> Any:
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

    def check_types(*args: Any, **kwargs: Any) -> Any:
        params = dict(zip(args_spec.args, args))
        params.update(kwargs)

        for name, value in params.items():
            type_hint = args_spec.annotations.get(name, Any)

            if isinstance(type_hint, _SpecialForm) or type_hint == Any:
                continue

            actual_type = get_actual_type(type_hint=type_hint, value=value)
            if not isinstance(value, actual_type):
                raise TypeError(
                    f"Expected type '{type_hint}' for attribute '{name}'"
                    f" but received type '{type(value)}' instead."
                )

    def get_actual_type(type_hint: Any, value: Any) -> Any:
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

    def decorate(func: Any) -> Any:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            check_signature(func)
            check_types(*args, **kwargs)
            return func(*args, **kwargs)

        return wrapper

    if inspect.isclass(wrapped):
        wrapped.__init__ = decorate(wrapped.__init__)
        return wrapped

    return decorate(wrapped)
