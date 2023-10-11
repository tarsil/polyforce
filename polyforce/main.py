from inspect import Signature
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Dict, Set, Type, Union, _SpecialForm

from typing_extensions import get_args

from ._internal import _construction
from .config import Config

# class _PolyModelBase(metaclass=_construction.PolyMetaclass):
#     """
#     Simple base class that uses the metaclass directly
#     avoiding the mectaclass conflicts when used with something else.
#     """


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
    else:
        poly_fields = {}

    __signature__: ClassVar[Dict[str, Signature]] = {}
    config = Config()

    def __getattribute__(self, name: str) -> Any:
        """
        Get an attribute with static type checking.

        Args:
            name (str): The name of the attribute to access.

        Returns:
            Any: The value of the attribute.

        Raises:
            AttributeError: If the attribute does not exist.

        Example:
        ```
        obj = MyObject(42)
        value = obj.value  # Accessing the 'value' attribute
        ```
        """
        # breakpoint()
        # if name in self.__dict__:
        #     return super().__getattribute__(name)

        try:
            func = super().__getattribute__(name)
            signatures = object.__getattribute__(self, "__signature__")
            signature: Signature = signatures[name]

            if signature is not None:
                return self._add_static_type_checking(func, signature)
            else:
                return func
        except (KeyError, AttributeError):
            return object.__getattribute__(self, name)

    def _extract_type_hint(type_hint: Union[Type, tuple]) -> Union[Type, tuple]:
        """
        Extracts the base type from a type hint, considering typing extensions.

        This function checks if the given type hint is a generic type hint and extracts
        the base type. If not, it returns the original type hint.

        Args:
            type_hint (Union[Type, tuple]): The type hint to extract the base type from.

        Returns:
            Union[Type, tuple]: The base type of the type hint or the original type hint.

        Example:
        ```
        from typing import List, Union

        # Extract the base type from a List hint
        base_type = extract_type_hint(List[int])  # Returns int

        # If the hint is not a generic type, it returns the original hint
        original_hint = extract_type_hint(Union[int, str])  # Returns Union[int, str]
        ```
        """
        if hasattr(type_hint, "__origin__"):
            return get_args(type_hint)
        return type_hint

    def _add_static_type_checking(self, func: Any, signature: Signature) -> Callable:
        """
        Add static type checking to a method or function.

        Args:
            func (Any): The method or function to add type checking to.
            signature (Signature): The method's signature for type checking.

        Returns:
            Callable: A wrapped function with type checking.

        Example:
        ```
        def my_method(self, value: int) -> str:
            return str(value)

        obj = MyObject(42)
        obj.__signature__['my_method'] = inspect.signature(my_method)

        # Accessing 'my_method' will now perform type checking
        result = obj.my_method(42)  # This is valid
        result = obj.my_method("42")  # This will raise a TypeError
        ```
        """

        def polycheck(*args: Any, **kwargs: Any) -> Any:
            bound = signature.bind(*args, **kwargs)
            bound.apply_defaults()

            for name, value in bound.arguments.items():
                if name in signature.parameters:
                    expected_type = signature.parameters[name].annotation

                    if expected_type in (_SpecialForm, Any):
                        continue

                    expected_args = self._extract_type_hint(expected_type)
                    if not isinstance(value, expected_args):
                        raise TypeError(
                            f"Expected type '{expected_type}' for attribute '{name}', "
                            f"but received type '{type(value)}' instead."
                        )

            return func(*args, **kwargs)

        return polycheck
