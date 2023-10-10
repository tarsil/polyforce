from inspect import Signature
from typing import TYPE_CHECKING, Any, ClassVar, Dict, Set, _SpecialForm

from typing_extensions import get_args, get_origin

from ._internal import _construction
from .config import Config


class PolyModel(metaclass=_construction.PolyMetaclass):
    """
    The class object used to be subclassed and apply
    the static checking on the top of any python object
    and function across the codebase.

    Example:
        from polyforce import PolyModel

        class MyObject(PolyModel):
            ...
    """

    if TYPE_CHECKING:
        config: ClassVar[Config]
        poly_fields: ClassVar[Dict[str, Any]]
        __class_vars__: ClassVar[Set[str]]
    else:
        poly_fields = {}

    __slots__ = "__dict__"
    __signature__: ClassVar[Dict[str, Signature]]
    config = Config()

    def __getattribute__(self, __name: str) -> Any:
        try:
            func = object.__getattribute__(self, __name)
            signatures = object.__getattribute__(self, "__signature__")
            signature: Signature = signatures[__name]

            def polycheck(*args: Any, **kwargs: Any) -> Any:
                nonlocal signature
                nonlocal func
                params = dict(zip(signature.parameters.values(), args))
                params_from_kwargs = {
                    signature.parameters.get(key, type(value)): value
                    for key, value in kwargs.items()
                }
                params.update(params_from_kwargs)  # type: ignore

                for parameter, value in params.items():
                    type_hint = parameter.annotation

                    if isinstance(type_hint, _SpecialForm) or type_hint == Any:
                        continue

                    if hasattr(type_hint, "__origin__"):
                        actual_type = type_hint.__origin__
                    else:
                        actual_type = get_origin(type_hint)

                    actual_type = actual_type or type_hint

                    # For versions prior to python 3.10
                    if isinstance(actual_type, _SpecialForm):
                        actual_type = (
                            get_args(value)
                            if not hasattr(type_hint, "__origin__")
                            else type_hint.__args__
                        )

                    if not isinstance(value, actual_type):
                        raise TypeError(
                            f"Expected type '{type_hint}' for attribute '{parameter.name}'"
                            f" but received type '{type(value)}' instead."
                        )

                    return func(*args, **kwargs)

            return polycheck

        except (KeyError, AttributeError):
            return object.__getattribute__(self, __name)
