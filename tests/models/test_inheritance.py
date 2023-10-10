from polyforce import PolyModel


class User(PolyModel):
    ...


class Profile(User):
    def __init__(self) -> None:
        super().__init__()

    def get_name(self, name: str) -> str:
        return name


def test_can_inherit():
    profile = Profile()
    name = profile.get_name("poly")

    assert name == "poly"


def test_ignores_checks():
    class NewUser(PolyModel):
        config = {"ignore": True}

    class NewProfile(NewUser):
        def __init__(self):
            super().__init__()

        def get_name(self, name):
            return name

    profile = NewProfile()
    name = profile.get_name(1)
    assert name == 1
