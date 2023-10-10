from typing import List, Union

from polyforce import Config, PolyModel


class Actor:
    ...


class Movie(PolyModel):
    config: Config(ignored_types=(Actor,))

    def __init__(
        self,
        name: str,
        year: int,
        tags: Union[List[str], None] = None,
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
