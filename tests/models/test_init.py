from polyforce import PolyModel


class Model(PolyModel):
    def __init__(self, name: str, age: int) -> None:
        super().__init__()
        self.name = name
        self.age = age


def test_model():
    model = Model(name="Polyforce", age=1)

    assert repr(model) == "Model(name='Polyforce', age=1)"
