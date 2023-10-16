from typing import Any, Dict, List, Mapping, Union

import pytest

from polyforce import PolyField, PolyModel
from polyforce.exceptions import ValidationError


class Model(PolyModel):
    def __init__(self, name: str, age: Union[str, int]) -> None:
        ...

    def create_model(self, names: List[str]) -> None:
        return names

    def get_model(self, models: Dict[str, Any]) -> Dict[str, Any]:
        return models

    def set_model(self, models: Mapping[str, PolyModel]) -> None:
        return models


def test_can_create_polyfield():
    field = PolyField(annotation=str, name="field")
    assert field is not None
    assert field.annotation == str
    assert field.name == "field"
    assert field.is_required() is True


def test_raise_type_error_on_default_field():
    with pytest.raises(TypeError) as raised:
        PolyField(annotation=str, default=2, name="name")

    assert (
        raised.value.args[0]
        == "default 'int' for field 'name' is not valid for the field type annotation, it must be type 'str'"
    )


def test_default_field():
    default = "john"

    def get_default():
        nonlocal default
        return default

    field = PolyField(annotation=str, default=get_default, name="name")
    assert field.default == default


def test_functions():
    model = Model(name="PolyModel", age=1)

    names = model.create_model(names=["poly"])
    assert names == ["poly"]

    models = model.get_model(models={"name": "poly"})
    assert models == {"name": "poly"}

    models = model.set_model(models={"name": "poly"})
    assert models == {"name": "poly"}


@pytest.mark.parametrize("func", ["get_model", "set_model"])
def test_functions_raises_validation_error(func):
    model = Model(name="PolyModel", age=1)

    with pytest.raises(ValidationError):
        model.create_model(names="a")

    with pytest.raises(ValidationError):
        getattr(model, func)(models="a")


def test_poly_fields():
    model = Model(name="PolyModel", age=1)

    assert len(model.poly_fields) == 4

    for value in ["create_model", "get_model", "set_model"]:
        assert value in model.poly_fields

    assert len(model.poly_fields["__init__"]) == 2
    assert len(model.poly_fields["create_model"]) == 1
    assert len(model.poly_fields["get_model"]) == 1
    assert len(model.poly_fields["set_model"]) == 1
