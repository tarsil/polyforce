from typing import Any, Tuple, Union

from typing_extensions import TypedDict


class ErrorDetail(TypedDict):
    """
    The base of an error with details to be exposed.
    """

    source: str
    """From which source the error occurred."""
    value: Tuple[Union[str, int], ...]
    """Tuple of strings and ints identiying where the error occurred."""
    input: Any
    """The input data from the 'value'. Commonly known as type."""
    expected: Any
    """The expected input that caused the error."""
    message: str
    """Human readable error message."""
