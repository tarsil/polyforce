from typing import Any

import pytest

from polyforce import polycheck


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
    with pytest.raises(TypeError):
        another_function(name="a")


@polycheck(ignored_types=(Dummy,))
def ignore_function(
    name: Dummy,
) -> Any:
    ...


def test_polycheck_ignore_types():
    ignore_function(name="a")
