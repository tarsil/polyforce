from polyforce import PolyModel


class User(PolyModel):
    def __init__(self, name: str, email: str) -> None:
        ...

    def set_name(self, name: str) -> None:
        ...

    def set_email(self, email: str) -> None:
        ...
