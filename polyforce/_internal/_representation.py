"""
The MIT License (MIT)

Copyright (c) 2017 to present Pydantic Services Inc. and individual contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

This file contains the object representation used by Pydantic with minor
changes.
"""
from __future__ import annotations as _annotations

import sys
import types
import typing
from typing import Any

import typing_extensions

try:
    from typing import _TypingBase  # type: ignore[attr-defined]
except ImportError:
    from typing import _Final as _TypingBase  # type: ignore[attr-defined]

if typing.TYPE_CHECKING:
    ReprArgs: typing_extensions.TypeAlias = "typing.Iterable[tuple[str | None, Any]]"
    RichReprResult: typing_extensions.TypeAlias = (
        "typing.Iterable[Any | tuple[Any] | tuple[str, Any] | tuple[str, Any, Any]]"
    )

if sys.version_info < (3, 9):
    # python < 3.9 does not have GenericAlias (list[int], tuple[str, ...] and so on)
    TypingGenericAlias = ()
else:
    from typing import GenericAlias as TypingGenericAlias  # type: ignore


if sys.version_info < (3, 11):
    from typing_extensions import NotRequired, Required
else:
    from typing import NotRequired, Required  # noqa: F401


if sys.version_info < (3, 10):

    def origin_is_union(tp: type[Any] | None) -> bool:
        return tp is typing.Union

    WithArgsTypes = (TypingGenericAlias,)

else:

    def origin_is_union(tp: type[Any] | None) -> bool:
        return tp is typing.Union or tp is types.UnionType

    WithArgsTypes = typing._GenericAlias, types.GenericAlias, types.UnionType  # type: ignore[attr-defined]


if sys.version_info < (3, 10):
    NoneType = type(None)
    EllipsisType = type(Ellipsis)
else:
    pass


class PlainRepresentation(str):
    """String class where repr doesn't include quotes. Useful with Representation when you want to return a string representation of something that is valid (or pseudo-valid) python."""

    def __repr__(self) -> str:
        return str(self)


class Representation:
    """
    Misin that provides representation of everything
    Polyforce.
    """

    __slots__ = ()  # type: typing.Collection[str]

    def __repr_args__(self) -> ReprArgs:
        """Returns the attributes to show in __str__, __repr__, and __pretty__ this is generally overridden."""
        attrs_names = self.__slots__
        if not attrs_names and hasattr(self, "__dict__"):
            attrs_names = self.__dict__.keys()
        attrs = ((s, getattr(self, s)) for s in attrs_names)
        return [(a, v) for a, v in attrs if v is not None]

    def __repr_name__(self) -> str:
        """Name of the instance's class, used in __repr__."""
        return self.__class__.__name__

    def __repr_str__(self, join_str: str) -> str:
        return join_str.join(
            repr(v) if a is None else f"{a}={v!r}" for a, v in self.__repr_args__()
        )

    def __pretty__(
        self, fmt: typing.Callable[[Any], Any], **kwargs: Any
    ) -> typing.Generator[Any, None, None]:
        """Used by devtools (https://python-devtools.helpmanual.io/) to pretty print objects."""
        yield self.__repr_name__() + "("
        yield 1
        for name, value in self.__repr_args__():
            if name is not None:
                yield name + "="
            yield fmt(value)
            yield ","
            yield 0
        yield -1
        yield ")"

    def __rich_repr__(self) -> RichReprResult:
        """Used by Rich (https://rich.readthedocs.io/en/stable/pretty.html) to pretty print objects."""
        for name, field_repr in self.__repr_args__():
            if name is None:
                yield field_repr
            else:
                yield name, field_repr

    def __str__(self) -> str:
        return self.__repr_str__(" ")

    def __repr__(self) -> str:
        return f'{self.__repr_name__()}({self.__repr_str__(", ")})'


def display_as_type(obj: Any) -> str:
    """Pretty representation of a type, should be as close as possible to the original type definition string.

    Takes some logic from `typing._type_repr`.
    """
    if isinstance(obj, types.FunctionType):
        return obj.__name__
    elif obj is ...:
        return "..."
    elif isinstance(obj, Representation):
        return repr(obj)

    if not isinstance(obj, (_TypingBase, WithArgsTypes, type)):
        obj = obj.__class__  # type: ignore

    if origin_is_union(typing_extensions.get_origin(obj)):
        args = ", ".join(map(display_as_type, typing_extensions.get_args(obj)))
        return f"Union[{args}]"
    elif isinstance(obj, WithArgsTypes):
        if typing_extensions.get_origin(obj) == typing_extensions.Literal:
            args = ", ".join(map(repr, typing_extensions.get_args(obj)))
        else:
            args = ", ".join(map(display_as_type, typing_extensions.get_args(obj)))
        return f"{obj.__qualname__}[{args}]"
    elif isinstance(obj, type):  # type: ignore
        return obj.__qualname__
    else:
        return repr(obj).replace("typing.", "").replace("typing_extensions.", "")
