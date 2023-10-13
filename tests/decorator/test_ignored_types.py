from typing import Any

import pytest

from polyforce import polycheck
from polyforce.exceptions import ValidationError


class Dummy:
    ...


@polycheck(ignore=True)
def my_function(
    name: Dummy,
) -> Any:
    ...


def test_polycheck():
    my_function(name="A test")


@polycheck()
def another_function(
    name: Dummy,
) -> Any:
    ...


def test_polycheck_error():
    with pytest.raises(ValidationError) as raised:
        another_function(name="a")

    assert raised.value.errors() == [
        {
            "source": "another_function",
            "value": "a",
            "input": "name",
            "expected": "Dummy",
            "message": "Expected 'Dummy' for attribute 'name', but received type 'str'.",
        }
    ]


@polycheck(ignored_types=(Dummy,))
def ignore_function(
    name: Dummy,
) -> Any:
    ...


def test_polycheck_ignore_types():
    ignore_function(name="a")
