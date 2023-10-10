from typing import Any, Union


class PolyException(Exception):
    """
    Base exception for all Asyncz thrown error exceptions.
    """

    detail: Union[str, None] = None

    def __init__(self, *args: Any, detail: str = "") -> None:
        if detail:
            self.detail = detail
        super().__init__(*(str(arg) for arg in args if arg), detail)

    def __repr__(self) -> str:
        if self.detail:
            return f"{self.__class__.__name__} - {self.detail}"
        return self.__class__.__name__

    def __str__(self) -> str:
        return "".join(self.args).strip()


class ReturnSignatureMissing(PolyException):
    detail: Union[str, None] = (
        "Missing return in '{func}'. A return value of a function should be type annotated. "
        "If your function doesn't return a value or returns None, annotate it as returning 'NoReturn' or 'None' respectively."
    )

    def __init__(self, func: str) -> None:
        detail = self.detail.format(func=func)
        super().__init__(detail=detail)


class MissingAnnotation(PolyException):
    detail: Union[
        str, None
    ] = "'{name}' is not typed. If you are not sure, annotate with 'typing.Any'."

    def __init__(self, name: str) -> None:
        detail = self.detail.format(name=name)
        super().__init__(detail=detail)
