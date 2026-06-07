from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional, Union


class HasFeatureValues(ABC):
    """Interface for objects exposing property, containment, and reference values
    associated with the features of their classifier.
    """

    if TYPE_CHECKING:
        from lionweb.language import Containment, Property, Reference
        from lionweb.model import Node, ReferenceValue

    @abstractmethod
    def get_property_value(self, property: Union[str, "Property"]) -> object | None: ...

    @abstractmethod
    def set_property_value(self, property: Union[str, "Property"], value: Any | None) -> None: ...

    @abstractmethod
    def get_children(self, containment: Optional["Containment"] = None) -> list: ...

    @abstractmethod
    def add_child(self, containment: "Containment", child: "Node") -> None: ...

    @abstractmethod
    def remove_child(self, **kwargs) -> None: ...

    @abstractmethod
    def get_reference_values(self, reference: "Reference") -> list: ...

    @abstractmethod
    def add_reference_value(
        self, reference: "Reference", referred_node: "ReferenceValue"
    ) -> None: ...

    @abstractmethod
    def remove_reference_value(
        self, reference: "Reference", reference_value: "ReferenceValue"
    ) -> None: ...

    @abstractmethod
    def set_reference_values(self, reference: "Reference", values: list) -> None: ...
