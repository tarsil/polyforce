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


class Film(Model):
    ...


class Movie(Film):
    def get_film(self, name: str) -> str:
        ...


def test_can_create_polyfield():
    field = PolyField(annotation=str, name="field")
    assert field is not None
    assert field.annotation == str
    assert field.name == "field"


def test_poly_fields():
    model = Film(name="PolyModel", age=1)

    assert len(model.poly_fields) == 4
    assert len(model.__signature__) == 4

    for value in ["create_model", "get_model", "set_model"]:
        assert value in model.poly_fields

    assert len(model.poly_fields["__init__"]) == 2
    assert len(model.poly_fields["create_model"]) == 1
    assert len(model.poly_fields["get_model"]) == 1
    assert len(model.poly_fields["set_model"]) == 1


def test_poly_fields_for_simples_nested_inheritance():
    model = Movie(name="PolyModel", age=1)

    assert len(model.poly_fields) == 5
    assert len(model.__signature__) == 5

    for value in ["create_model", "get_model", "set_model", "get_film"]:
        assert value in model.poly_fields

    assert len(model.poly_fields["__init__"]) == 2
    assert len(model.poly_fields["create_model"]) == 1
    assert len(model.poly_fields["get_model"]) == 1
    assert len(model.poly_fields["set_model"]) == 1
    assert len(model.poly_fields["get_film"]) == 1


class MovieFilm(Movie):
    def __init__(self, movies: List[str]) -> None:
        ...

    def get_movies(self) -> None:
        ...

    def set_model(self) -> None:
        ...


def test_poly_fields_for_simples_nested_inheritance_init():
    model = MovieFilm(movies=["Avengers"])

    assert len(model.poly_fields) == 5
    assert len(model.__signature__) == 6

    for value in ["create_model", "get_model", "set_model", "get_film"]:
        assert value in model.poly_fields

    assert len(model.poly_fields["__init__"]) == 1
    assert len(model.poly_fields["create_model"]) == 1
    assert len(model.poly_fields["get_model"]) == 1
    assert len(model.poly_fields["set_model"]) == 1
    assert len(model.poly_fields["get_film"]) == 1
