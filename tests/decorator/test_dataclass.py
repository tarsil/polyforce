from dataclasses import dataclass
from typing import Any, Optional, Union

import pytest

from polyforce import polycheck
from polyforce.exceptions import ValidationError


@polycheck()
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
    with pytest.raises(ValidationError) as raised:
        User(union_values={"a": 1})

    assert raised.value.errors() == [
        {
            "source": "User",
            "value": {"a": 1},
            "input": "union_values",
            "expected": ("int", "str", "float"),
            "message": "Expected '('int', 'str', 'float')' for attribute 'union_values', but received type 'dict'.",
        }
    ]


def test_dict_and_not_str_raise_error_name():
    with pytest.raises(ValidationError) as raised:
        User(name={"a": 1})

    assert raised.value.errors() == [
        {
            "source": "User",
            "value": {"a": 1},
            "input": "name",
            "expected": "str",
            "message": "Expected 'str' for attribute 'name', but received type 'dict'.",
        }
    ]


def test_str_and_not_int_raise_error():
    with pytest.raises(ValidationError) as raised:
        User(int_value="a")

    assert raised.value.errors() == [
        {
            "source": "User",
            "value": "a",
            "input": "int_value",
            "expected": "int",
            "message": "Expected 'int' for attribute 'int_value', but received type 'str'.",
        }
    ]
