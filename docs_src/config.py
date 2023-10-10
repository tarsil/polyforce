from polyforce import Config, PolyModel


class Movie(PolyModel):
    config: Config = Config(ignore=..., ignored_types=...)
    ...
