from typing import List, Union

from polyforce import polycheck


class Actor:
    ...


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
        self.actors: List[Actor] = []

    @polycheck(ignored_types=(Actor,))
    def add_actor(self, actor: Actor) -> None:
        """
        Returns a movie
        """
        self.actors.append(actor)
