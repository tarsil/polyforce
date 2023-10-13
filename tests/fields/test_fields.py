from typing import Any, Dict, List, Mapping, Union

from polyforce import PolyField, PolyModel


class Model(PolyModel):
    def __init__(self, name: str, age: Union[str, int]) -> None:
        ...

    def create_model(self, names: List[str]) -> None:
        ...

    def get_model(self, models: Dict[str, Any]) -> Dict[str, Any]:
        ...

    def set_model(self, models: Mapping[str, PolyModel]) -> None:
        ...


def test_can_create_polyfield():
    field = PolyField(annotation=str, name="field")
    assert field is not None
    assert field.annotation == str
    assert field.name == "field"


def test_poly_fields():
    model = Model(name="PolyModel", age=1)

    assert len(model.poly_fields) == 4

    for value in ["create_model", "get_model", "set_model"]:
        assert value in model.poly_fields

    assert len(model.poly_fields["__init__"]) == 2
    assert len(model.poly_fields["create_model"]) == 1
    assert len(model.poly_fields["get_model"]) == 1
    assert len(model.poly_fields["set_model"]) == 1
