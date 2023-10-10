from typing_extensions import Any, Dict, Self, Type, Union, cast

from ..config import Config


class ConfigWrapper:
    __slots__ = ("config", "ignore", "ignored_types")
    config: Config
    ignore: bool
    ignored_types: Any

    def __init__(
        self,
        config: Union[Config, Dict[str, Any], Type[Any], None],
        ignore: bool = False,
        ignored_types: Union[Any, None] = None,
    ):
        self.config = cast(Config, config)
        self.ignore = ignore
        self.ignored_types = ignored_types or ()

    @classmethod
    def for_model(cls, bases: Any, attrs: Dict[str, Any]) -> Self:
        config_new = Config()

        for base in bases:
            config = getattr(base, "config", None)
            config_new.update(config.copy())

        config_from_attrs = attrs.get("config")
        if config_from_attrs is not None:
            config_new.update(config_from_attrs)

        return cls(config_new, **config_new)
