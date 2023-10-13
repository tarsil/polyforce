from typing import Any, Callable, List, Type, TypedDict, Union

from typing_extensions import Self, Unpack, get_args, get_origin

from .core._polyforce_core import PolyforceUndefined


class _FieldInputs(TypedDict, total=False):
    annotation: Union[Type[Any], None]
    default: Any
    default_factory: Union[Callable[[], Any], None]
    title: Union[str, None]
    description: Union[str, None]
    required: bool


_DefaultValues = {
    "default": ...,
    "default_factory": None,
    "title": None,
    "description": None,
    "required": False,
}


class PolyField:
    """
    This class holds the information about a field used in Polyforce.

    The PolyField is used for any field definition regardless if it
    is declared or not.

    You shouldn't be declaring PolyField directly and instead just use the Field(...)
    definition.

    The PolyFields are accessible via PolyModel.poly_fields.

    Attributes:
        annotation: The type annotation of the field.
        default: The default value of the field.
        default_factory: The default function used to build the default for the field.
        title: The title of the field.
        description: The description of the field.
    """

    __slots__ = (
        "annotation",
        "default",
        "default_factory",
        "title",
        "description",
        "required",
        "metadata",
        "_attributes_set",
    )

    annotation: Union[Type[Any], None]
    default: Any
    default_factory: Union[Callable[[], Any], None]
    title: Union[str, None]
    description: Union[str, None]
    required: bool
    metadata: List[Any]

    def __init__(self, **kwargs: Unpack[_FieldInputs]) -> None:
        """
        This class should generally not be initialized directly; instead, use the `polyforce.fields.Field` function.
        """
        self._attributes_set = {k: v for k, v in kwargs.items() if v is not PolyforceUndefined}
        kwargs = {
            k: _DefaultValues.get(k) if v is PolyforceUndefined else v for k, v in kwargs.items()
        }
        self.annotation, metadata = self._extract_annotation(kwargs.get("annotation"))

        default = kwargs.pop("default", PolyforceUndefined)
        if default is Ellipsis:
            self.default = PolyforceUndefined
        else:
            self.default = default

        self.default_factory = kwargs.pop("default_factory", None)

        if self.default is not PolyforceUndefined and self.default_factory is not None:
            raise TypeError("cannot specify both default and default_factory")

        self.title = kwargs.pop("title", None)
        self.description = kwargs.pop("description", None)
        self.required = kwargs.pop("required", False)
        self.metadata = metadata

    @classmethod
    def _extract_annotation(
        cls, annotation: type[Any] | None
    ) -> tuple[type[Any] | None, list[Any]]:
        if annotation is not None:
            if get_origin(annotation):
                first_arg, *extra_args = get_args(annotation)
                return first_arg, list(extra_args)
        return annotation, []

    @classmethod
    def from_field(cls, default: Any = PolyforceUndefined, **kwargs: Unpack[_FieldInputs]) -> Self:
        """
        Generates a new PolyField from the values provided.
        """
        if "annotation" in kwargs:
            raise TypeError('"annotation" is not permitted as a Field keyword argument')
        return cls(default=default, **kwargs)


def Field(
    default: Any = PolyforceUndefined,
    *,
    default_factory: Union[Callable[[], Any], None] = PolyforceUndefined,
    title: Union[str, None] = PolyforceUndefined,
    description: Union[str, None] = PolyforceUndefined,
    required: bool = PolyforceUndefined,
) -> PolyField:
    return PolyField.from_field(
        default=default,
        default_factory=default_factory,
        title=title,
        description=description,
        required=required,
    )
