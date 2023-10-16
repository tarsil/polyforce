from typing import List, Union

import pytest
from typing_extensions import Self

from polyforce import Field, PolyModel
from polyforce.exceptions import ValidationError


class Movie(PolyModel):
    def __init__(
        self,
        name: str,
        year: int,
        tags: Union[List[str], None] = None,
    ) -> None:
        self.name = name
        self.year = year
        self.tags = tags

    def get_movie(self, name: str) -> Self:
        """
        Returns a movie
        """
        ...

    def _set_name(self, name: str) -> None:
        """
        Sets the name of the movie.
        """
        self.name = name

    @classmethod
    def create_movie(cls, name: str, year: int) -> Self:
        """
        Creates a movie object
        """
        return cls(name=name, year=year)

    @staticmethod
    def evaluate_movie(name: str, tags: List[str]) -> bool:
        """
        Evaluates a movie in good (true) or bad (false)
        """
        ...


class Serie(Movie):
    def __init__(
        self,
        name: str = Field(default="24"),
        season: int = Field(default=1),
        year: int = Field(default=2023),
    ) -> None:
        super().__init__(name=name, year=year)
        self.season = season
        self._name = None

    def _set_name(self, name: Union[str, int]) -> None:
        if isinstance(name, str):
            super()._set_name(name)
        self._name = name


def test_can_create_movie():
    movie = Movie(name="Avengers", year=2023)

    assert movie.name == "Avengers"


def test_can_create_serie():
    serie = Serie(year=2023)

    assert serie.name == "24"


def test_can_set_name_inheritance():
    serie = Serie(year=2023)
    serie._set_name(name="overriden")
    assert serie.name == "overriden"

    serie._set_name(name=1)
    assert serie._name == 1


@pytest.mark.parametrize(
    "value", [{"a": 1}, 1.2, {3}, [4, 5, 3]], ids=["dict", "float", "set", "list"]
)
def test_cannot_set_name_inheritance_raises_error(value):
    serie = Serie(year=2023)

    with pytest.raises(ValidationError):
        serie._set_name(name=value)
