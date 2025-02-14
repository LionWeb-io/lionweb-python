from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Optional


class HasFeatureValues(ABC):
    if TYPE_CHECKING:
        from lionwebpython.language.containment import Containment
        from lionwebpython.language.reference import Reference
        from lionwebpython.model.node import Node
        from lionwebpython.model.reference_value import ReferenceValue

    @abstractmethod
    def get_property_value(self, **kwargs) -> Optional[object]:
        pass

    @abstractmethod
    def set_property_value(self, **kwargs) -> None:
        pass

    @abstractmethod
    def get_children(self, containment: Optional["Containment"] = None) -> List:
        pass

    @abstractmethod
    def add_child(self, containment: "Containment", child: "Node") -> None:
        pass

    @abstractmethod
    def remove_child(self, **kwargs) -> None:
        pass

    @abstractmethod
    def get_reference_values(self, reference: "Reference") -> List:
        pass

    @abstractmethod
    def add_reference_value(
        self, reference: "Reference", referred_node: "ReferenceValue"
    ) -> None:
        pass

    @abstractmethod
    def remove_reference_value(
        self, reference: "Reference", reference_value: "ReferenceValue"
    ) -> None:
        pass

    @abstractmethod
    def set_reference_values(self, reference: "Reference", values: List) -> None:
        pass
