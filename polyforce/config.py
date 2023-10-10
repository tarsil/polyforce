from typing_extensions import Any, TypedDict


class Config(TypedDict, total=False):
    ignore: bool
    """
    Ignores the type checking for the object.
    """
    ignored_types: Any
    """
    Ignores the types for static validation.
    """
