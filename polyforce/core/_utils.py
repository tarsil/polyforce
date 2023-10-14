from typing import Any

from typing_extensions import Annotated, get_origin

from .._internal._representation import WithArgsTypes


def is_annotated(ann_type: Any) -> bool:
    origin = get_origin(ann_type)
    return origin is not None and lenient_issubclass(origin, Annotated)


def lenient_issubclass(cls: Any, class_or_tuple: Any) -> bool:  # pragma: no cover
    try:
        return isinstance(cls, type) and issubclass(cls, class_or_tuple)
    except TypeError:
        if isinstance(cls, WithArgsTypes):
            return False
        raise  # pragma: no cover
