from polyforce import Field, PolyModel


class User(PolyModel):
    def __init__(self, name: str = Field(), email: str = Field()) -> None:
        ...

    def set_name(self, name: str = Field()) -> None:
        ...

    def set_email(self, email: str = Field()) -> None:
        ...
