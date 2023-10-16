from polyforce import Field, PolyModel


class User(PolyModel):
    def __init__(self, name: str = Field(), email: str = Field()) -> None:
        ...

    def set_name(self, name: str = Field(default="test")) -> None:
        ...

    def set_email(self, email: str = Field()) -> None:
        ...


def test_is_required():
    user = User(name="Polyforce", email="test@test.com")

    assert user.poly_fields["__init__"]["name"].is_required() is True
    assert user.poly_fields["set_name"]["name"].is_required() is False
