from typing import Any, final

from typing_extensions import Self


@final
class PolyforceUndefinedType:
    def __copy__(self) -> Self:
        ...

    def __deepcopy__(self, memo: Any) -> Self:
        ...


PolyforceUndefined = PolyforceUndefinedType
