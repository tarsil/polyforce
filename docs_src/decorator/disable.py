from typing import List, Union

from typing_extensions import Self

from polyforce import polycheck


class Movie:
    def __init__(
        self,
        name: str,
        year: int,
        tags: Union[List[str], None] = None,
    ) -> None:
        self.name = name
        self.year = year
        self.tags = tags

    @polycheck(ignore=True)
    def get_movie(self, name: str) -> Self:
        """
        Returns a movie
        """
        ...

    @polycheck(ignore=True)
    def _set_name(self, name: str) -> None:
        """
        Sets the name of the movie.
        """

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
