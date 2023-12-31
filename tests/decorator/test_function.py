from typing import Any, Optional, Union

import pytest

from polyforce import polycheck
from polyforce.exceptions import MissingAnnotation, ReturnSignatureMissing, ValidationError


@polycheck()
def my_function(
    union_values: Union[int, str, float],
    value: Any,
    name: str = "",
    int_value: int = 1,
    _not: Optional[bool] = None,
    no_hint: Any = None,
) -> Any:
    ...


def test_polycheck():
    my_function(union_values=2.0, value="A test")


def test_polycheck_all():
    my_function(union_values=2.0, value=["a", "list"], name="function", int_value=2, _not=True)


def test_missing_return_annotation():
    with pytest.raises(ReturnSignatureMissing) as raised:

        @polycheck()
        def test_func(name=None):
            ...

        test_func()

    assert (
        str(raised.value)
        == "Missing return in 'test_func'. A return value of a function should be type annotated. If your function doesn't return a value or returns None, annotate it as returning 'NoReturn' or 'None' respectively."
    )


def test_missing_typing_annotation():
    with pytest.raises(MissingAnnotation) as raised:

        @polycheck()
        def test_func(name=None) -> None:
            ...

        test_func()

    assert (
        str(raised.value)
        == "'name' is not typed. If you are not sure, annotate with 'typing.Any'."
    )


def test_dict_and_not_str_raise_error():
    with pytest.raises(ValidationError) as raised:
        my_function(union_values={"a": 1})

    assert raised.value.errors() == [
        {
            "source": "my_function",
            "value": {"a": 1},
            "input": "union_values",
            "expected": ("int", "str", "float"),
            "message": "Expected '('int', 'str', 'float')' for attribute 'union_values', but received type 'dict'.",
        }
    ]


def test_dict_and_not_str_raise_error_name():
    with pytest.raises(ValidationError) as raised:
        my_function(name={"a": 1})

    assert raised.value.errors() == [
        {
            "source": "my_function",
            "value": {"a": 1},
            "input": "name",
            "expected": "str",
            "message": "Expected 'str' for attribute 'name', but received type 'dict'.",
        }
    ]


def test_str_and_not_int_raise_error():
    with pytest.raises(ValidationError) as raised:
        my_function(int_value="a")

    assert raised.value.errors() == [
        {
            "source": "my_function",
            "value": "a",
            "input": "int_value",
            "expected": "int",
            "message": "Expected 'int' for attribute 'int_value', but received type 'str'.",
        }
    ]
