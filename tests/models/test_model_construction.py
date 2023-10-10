from typing import Any, Optional, Union

import pytest

from polyforce import Config, PolyModel
from polyforce.exceptions import MissingAnnotation, ReturnSignatureMissing


class User(PolyModel):
    config = Config(ignore=False)

    def __init__(self, name: str, age: int) -> None:
        super().__init__()
        self.name = name
        self.age = age


class Poly(PolyModel):
    def __init__(
        self,
        union_values: Union[int, str, float],
        value: Any,
        name: str = "",
        int_value: int = 1,
        _not: Optional[bool] = None,
    ) -> None:
        self.union_values = union_values
        self.value = value
        self.name = name
        self.int_value = int_value
        self._not = _not

    @classmethod
    def my_function(
        cls,
        union_values: Union[int, str, float],
        value: Any,
        name: str = "",
        int_value: int = 1,
        _not: Optional[bool] = None,
        no_hint: Any = None,
    ) -> Any:
        ...

    @staticmethod
    def my_function_static(
        union_values: Union[int, str, float],
        value: Any,
        name: str = "",
        int_value: int = 1,
        _not: Optional[bool] = None,
        no_hint: Any = None,
    ) -> Any:
        ...

    def my_func(
        self,
        union_values: Union[int, str, float],
        value: Any,
        name: str = "",
        int_value: int = 1,
        _not: Optional[bool] = None,
        no_hint: Any = None,
        **kwargs: Any,
    ) -> Any:
        ...


def test_create_user():
    user = User(name="polyforce", age=50)

    assert user.name == "polyforce"
    assert user.age == 50


def test_raises_missing_return_signature():
    with pytest.raises(ReturnSignatureMissing):

        class Movie(PolyModel):
            def __init__(self, name: str):
                ...


def test_raises_missing_annotation():
    with pytest.raises(MissingAnnotation):

        class Movie(PolyModel):
            def __init__(self, name) -> None:
                ...


def test_ignore_checks():
    class Movie(PolyModel):
        config = Config(ignore=True)

        def __init__(self, name):
            self.name = name

    movie = Movie(name="Avengers")
    assert movie.name == "Avengers"


def test_polycheck():
    user = Poly(union_values=2.0, value="A test")
    assert isinstance(user.union_values, float)
    assert isinstance(user.value, str)
    assert isinstance(user.name, str)
    assert isinstance(user.int_value, int)
    assert user._not is None


def test_enforce_other_types():
    user = Poly(union_values="user", value=["a", "list"], _not=True)
    assert isinstance(user.union_values, str)
    assert isinstance(user.value, list)
    assert len(user.value) == 2
    assert isinstance(user.name, str)
    assert isinstance(user.int_value, int)
    assert user._not is True


def test_dict_and_not_str_raise_error():
    with pytest.raises(TypeError):
        Poly(union_values={"a": 1})


def test_dict_and_not_str_raise_error_name():
    with pytest.raises(TypeError):
        Poly(name={"a": 1})


def test_str_and_not_int_raise_error():
    with pytest.raises(TypeError):
        Poly(int_value="a")


def test_polycheck_function():
    poly = Poly(union_values=2.0, value=["a", "list"], name="function", int_value=2, _not=True)
    poly.my_func(union_values=2.0, value="A test", coise=3)


def test_polycheck_all_function():
    poly = Poly(union_values=2.0, value=["a", "list"], name="function", int_value=2, _not=True)
    poly.my_func(union_values=2.0, value=["a", "list"], name="function", int_value=2, _not=True)


def test_dict_and_not_str_raise_error_function():
    poly = Poly(union_values=2.0, value=["a", "list"], name="function", int_value=2, _not=True)
    with pytest.raises(TypeError):
        poly.my_func(union_values={"a": 1})


def test_dict_and_not_str_raise_error_name_function():
    poly = Poly(union_values=2.0, value=["a", "list"], name="function", int_value=2, _not=True)
    with pytest.raises(TypeError):
        poly.my_func(name={"a": 1})


def test_str_and_not_int_raise_error_function():
    poly = Poly(union_values=2.0, value=["a", "list"], name="function", int_value=2, _not=True)
    with pytest.raises(TypeError):
        poly.my_func(int_value="a")


def test_polycheck_function_class():
    Poly.my_function(union_values=2.0, value="A test")


def test_polycheck_all_function_class():
    Poly.my_function(
        union_values=2.0, value=["a", "list"], name="function", int_value=2, _not=True
    )


def test_dict_and_not_str_raise_error_function_class():
    with pytest.raises(TypeError):
        Poly.my_function(union_values={"a": 1})


def test_dict_and_not_str_raise_error_name_function_class():
    with pytest.raises(TypeError):
        Poly.my_function(name={"a": 1})


def test_str_and_not_int_raise_error_function_class():
    with pytest.raises(TypeError):
        Poly.my_function(int_value="a")


def test_polycheck_function_static():
    Poly.my_function_static(union_values=2.0, value="A test")


def test_polycheck_all_function_static():
    Poly.my_function_static(
        union_values=2.0, value=["a", "list"], name="function", int_value=2, _not=True
    )


def test_dict_and_not_str_raise_error_function_static():
    with pytest.raises(TypeError):
        Poly.my_function_static(union_values={"a": 1})


def test_dict_and_not_str_raise_error_name_function_static():
    with pytest.raises(TypeError):
        Poly.my_function_static(name={"a": 1})


def test_str_and_not_int_raise_error_function_static():
    with pytest.raises(TypeError):
        Poly.my_function_static(int_value="a")


def test_double_underscore():
    with pytest.raises(ReturnSignatureMissing):

        class Double(PolyModel):
            def __test(self, name: str):
                ...
