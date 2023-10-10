from typing import Any, List, Union

from polyforce import Config, PolyModel


class Dummy:
    ...


class Actor:
    ...


class Movie(PolyModel):
    config = Config(ignored_types=(Actor,))

    def __init__(
        self, name: str, year: int, tags: Union[List[str], None] = None, **kwargs: Any
    ) -> None:
        self.name = name
        self.year = year
        self.tags = tags
        self.actors: List[Actor] = []

    def add_actor(self, actor: Actor) -> None:
        """
        Returns a movie
        """
        self.actors.append(actor)


def test_add_value():
    movie = Movie(name="Avengers", year="2023")
    movie.add_actor(actor=Dummy())

    assert len(movie.actors) == 1
