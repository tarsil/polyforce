from enum import Enum


class ErrorType(str, Enum):
    CLASS = "class"
    FUNCTION = "function"

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return str(self)
