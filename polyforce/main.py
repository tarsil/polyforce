from typing import TYPE_CHECKING, Any, ClassVar, Dict, Set

from ._internal import _construction
from .config import Config

_object_setattr = _construction.object_setattr


class PolyModel(metaclass=_construction.PolyMetaclass):
    """
    The base class for applying static type checking to attribute access.

    This class is meant to be subclassed for adding static type checking to attributes and methods.

    Example:
    ```
    from polyforce import PolyModel

    class MyObject(PolyModel):
        def __init__(self, value: int):
            self.value = value
    ```

    Attributes:
        __signature__ (ClassVar[Dict[str, Signature]]): Dictionary containing method signatures.
    """

    if TYPE_CHECKING:
        config: ClassVar[Config]
        poly_fields: ClassVar[Dict[str, Any]]
        __class_vars__: ClassVar[Set[str]]
        __polymodel_custom_init__: ClassVar[bool]
    else:
        poly_fields = {}

    config = Config()

    def __init__(__polymodel_self__, **data: Any) -> None:
        __tracebackhide__ = True

    __init__.__polymodel_base_init__ = True

    def __setattr__(self, name: str, value: Any) -> None:
        if name in self.__class_vars__:
            raise AttributeError(
                f"{name!r} is a ClassVar of `{self.__class__.__name__}` and cannot be set on an instance. "
                f"If you want to set a value on the class, use `{self.__class__.__name__}.{name} = value`."
            )
        _object_setattr(self, name, value)

    # def __getattribute__(self, name: str) -> Any:
    #     if name == "my_func":
    #         breakpoint()
    #         print(name)
    #     return super().__getattribute__(name)
