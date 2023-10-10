import inspect
from inspect import Parameter, Signature
from itertools import islice
from typing import TYPE_CHECKING, Any, Dict, List, Set, Type, cast

from polyforce.exceptions import MissingAnnotation, ReturnSignatureMissing

from ._config import ConfigWrapper

if TYPE_CHECKING:
    from ..main import PolyModel


def complete_poly_class(cls: Type["PolyModel"], config: ConfigWrapper) -> bool:
    """
    Completes the polyclass model constrution
    and applies all the fields and configurations.
    """
    methods: List[str] = [
        attr
        for attr in cls.__dict__.keys()
        if not attr.startswith("__") and not attr.endswith("__") and callable(getattr(cls, attr))
    ]

    if "__init__" in cls.__dict__:
        methods.append("__init__")

    signatures: Dict[str, Signature] = {}

    for method in methods:
        signatures[method] = generate_model_signature(cls, method, config)

    cls.__signature__ = signatures
    return True


def ignore_signature(signature: Signature) -> Signature:
    """
    Ignores the signature and assigns the Any to all the fields and return signature.
    """
    merged_params: Dict[str, Parameter] = {}
    for param in islice(signature.parameters.values(), 1, None):
        param = param.replace(annotation=Any)
        merged_params[param.name] = param
    return Signature(parameters=list(merged_params.values()), return_annotation=Any)


def generate_model_signature(
    cls: Type["PolyModel"], value: str, config: ConfigWrapper
) -> Signature:
    """
    Generates a signature for each method of the given class.
    """
    func = getattr(cls, value)
    signature = Signature.from_callable(func)

    if config.ignore:
        return ignore_signature(signature)

    params = signature.parameters.values()
    merged_params: Dict[str, Parameter] = {}
    if signature.return_annotation == inspect.Signature.empty:
        raise ReturnSignatureMissing(func=value)

    for param in islice(params, 1, None):  # skip self arg
        if param.annotation == Signature.empty:
            raise MissingAnnotation(name=param.name)

        if param.annotation == "Any":
            param = param.replace(annotation=Any)
        elif param.annotation in config.ignored_types:
            param = param.replace(annotation=Any)
        if param.kind is param.VAR_KEYWORD:
            continue
        merged_params[param.name] = param

    # Generate the new signatures.
    return Signature(
        parameters=list(merged_params.values()), return_annotation=signature.return_annotation
    )


class PolyMetaclass(type):
    """
    Base metaclass used for the PolyModel objects
    and applies all static type checking needed
    for all the functions and methods of a given class.
    """

    __filtered_functions__: Set[str]

    def __new__(cls, name: str, bases: Any, attrs: Any) -> Any:
        if bases:
            base_class_vars = cls._collect_data_from_bases(bases)
            config_wrapper = ConfigWrapper.for_model(bases, attrs)

            attrs["config"] = config_wrapper.config
            attrs["__class_vars__"] = base_class_vars

            model = super().__new__
            parents = [parent for parent in bases if isinstance(parent, PolyMetaclass)]
            if not parents:
                return model(cls, name, bases, attrs)

            model = cast("Type[PolyModel]", model(cls, name, bases, attrs))  # type: ignore
            complete_poly_class(model, config_wrapper)  # type: ignore
            return model

        else:
            return super().__new__(cls, name, bases, attrs)

    @staticmethod
    def _collect_data_from_bases(bases: Any) -> Set[str]:
        """
        Collects all the data from the bases.
        """
        from ..main import PolyModel

        class_vars: Set[str] = set()

        for base in bases:
            if issubclass(base, PolyModel) and base is not PolyModel:
                class_vars.update(base.__class_vars__)
        return class_vars
