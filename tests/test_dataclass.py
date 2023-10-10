from dataclasses import dataclass
from typing import Any, Optional, Union

import pytest

from polyforce import polycheck


@polycheck
@dataclass(frozen=True)
class User:
    union_values: Union[int, str, float]
    value: Any
    name: str = ""
    int_value: int = 1
    _not: Optional[bool] = None


def test_polycheck():
    user = User(union_values=2.0, value="A test")
    assert isinstance(user.union_values, float)
    assert isinstance(user.value, str)
    assert isinstance(user.name, str)
    assert isinstance(user.int_value, int)
    assert user._not is None


def test_enforce_other_types():
    user = User(union_values="user", value=["a", "list"], _not=True)
    assert isinstance(user.union_values, str)
    assert isinstance(user.value, list)
    assert len(user.value) == 2
    assert isinstance(user.name, str)
    assert isinstance(user.int_value, int)
    assert user._not is True


def test_dict_and_not_str_raise_error():
    with pytest.raises(TypeError):
        User(union_values={"a": 1})


def test_dict_and_not_str_raise_error_name():
    with pytest.raises(TypeError):
        User(name={"a": 1})


def test_str_and_not_int_raise_error():
    with pytest.raises(TypeError):
        User(int_value="a")
