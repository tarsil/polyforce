from typing import List, Union

import pytest
from pydantic import BaseModel

from polyforce import polycheck
from polyforce.exceptions import ReturnSignatureMissing, ValidationError


class Dummy:
    ...


class Actor:
    ...


class Movie(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    name: str
    year: int
    actors: Union[List[Actor], None] = None

    @polycheck()
    def add_actor(self, actor: Actor) -> None:
        self.actors.append(actor)

    @polycheck()
    def set_actor(self, actor: Actor):
        ...


def test_add_value():
    movie = Movie(name="Avengers", year="2023")

    with pytest.raises(ValidationError) as raised:
        movie.add_actor(actor=Dummy())

    assert raised.value.errors() == [
        {
            "source": "add_actor",
            "value": {},
            "input": "actor",
            "expected": "Actor",
            "message": "Expected 'Actor' for attribute 'actor', but received type 'Dummy'.",
        }
    ]


def test_missing_return():
    movie = Movie(name="Avengers", year="2023")

    with pytest.raises(ReturnSignatureMissing):
        movie.set_actor(actor=Dummy())
