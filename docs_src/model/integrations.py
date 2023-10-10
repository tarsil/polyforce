from typing import List, Union

from pydantic import BaseModel, ConfigDict

from polyforce import polycheck


class Actor:
    ...


class Movie(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: str
    year: int
    actors: Union[List[Actor], None] = None

    @polycheck
    def add_actor(self, actor: Actor) -> None:
        self.actors.append(actor)

    @polycheck
    def set_actor(self, actor: Actor) -> None:
        ...
