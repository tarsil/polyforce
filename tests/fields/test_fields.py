from typing import Any, Dict, List, Mapping, Union

import pytest

from polyforce import Field, PolyField, PolyModel


class Model(PolyModel):
    def __init__(self, name: str = Field(), age: Union[str, int] = Field()) -> None:
        ...

    def create_model(self, names: List[str] = Field()) -> None:
        return names

    def get_model(self, models: Dict[str, Any] = Field()) -> Dict[str, Any]:
        return models

    def set_model(self, models: Mapping[str, PolyModel] = Field()) -> None:
        return models


def test_field():
    model = Model(name="Polyforce", age=1)

    assert len(model.poly_fields) == 4
    assert model.poly_fields["create_model"]["names"].annotation == List[str]
    assert model.poly_fields["get_model"]["models"].annotation == Dict[str, Any]
    assert model.poly_fields["set_model"]["models"].annotation == Mapping[str, PolyModel]


def test_no_annotation():
    field: PolyField = Field(default=2, name="name")

    assert field.annotation is None


def test_raise_type_error_on_default_field():
    with pytest.raises(TypeError):

        class NotherModel(PolyModel):
            def __init__(self, name: str = Field(default=2)) -> None:
                ...
