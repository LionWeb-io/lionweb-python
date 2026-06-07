from typing import TYPE_CHECKING, Optional, cast

if TYPE_CHECKING:
    from lionweb.language.concept import Concept

from lionweb.language.containment import Containment
from lionweb.model.classifier_instance import ClassifierInstance
from lionweb.model.has_settable_parent import HasSettableParent
from lionweb.model.impl.dynamic_classifier_instance import DynamicClassifierInstance
from lionweb.model.node import Node


class ContainmentFeatureNotFoundError(RuntimeError):
    """Raised when the containment feature used to hold a node within its parent
    cannot be located among the parent's containments.

    Args:
        node: The node whose containment feature could not be found.
    """

    def __init__(self, node: Node):
        super().__init__("Unable to find the containment feature")
        self.node = node


class DynamicNode(DynamicClassifierInstance, Node, HasSettableParent):
    """A generic, reflective implementation of Node backed by a
    DynamicClassifierInstance, suitable for any Concept definition.
    """

    def __init__(self, id: str | None = None, concept: Optional["Concept"] = None) -> None:
        self._id = id
        self.concept = concept
        self.parent: Node | None = None
        self.property_values: dict[str, object | None] = {}
        self.containment_values: dict[str, list[Node]] = {}
        from lionweb.model.reference_value import ReferenceValue

        self.reference_values: dict[str, list[ReferenceValue]] = {}
        from lionweb.model.annotation_instance import AnnotationInstance

        self.annotations: list[AnnotationInstance] = []

    def get_id(self) -> str | None:
        return self._id

    def set_concept(self, concept: "Concept") -> None:
        self.concept = concept

    def get_parent(self) -> Node | None:
        return self.parent

    def get_classifier(self) -> "Concept":
        from lionweb.language.concept import Concept

        return cast(Concept, self.concept)

    def get_containment_feature(self) -> Containment | None:
        if self.parent is None:
            return None
        for containment in self.parent.get_classifier().all_containments():
            if any(child == self for child in self.parent.get_children(containment)):
                return containment
        raise ContainmentFeatureNotFoundError(self)

    def set_parent(self, parent: Optional["ClassifierInstance"]) -> None:
        self.parent = cast(Node | None, parent)

    def __eq__(self, other):
        if not isinstance(other, DynamicNode):
            return False
        return (
            self.id == other.id
            and self._shallow_node_equality(self.parent, other.parent)
            and self._shallow_node_equality(self.concept, other.concept)
            and self.property_values == other.property_values
            and self._shallow_containments_equality(
                self.containment_values, other.containment_values
            )
            and self.reference_values == other.reference_values
            and len(self.annotations) == len(other.annotations)
            and {node.id for node in self.annotations} == {node.id for node in other.annotations}
        )

    @staticmethod
    def _shallow_containments_equality(
        containments1: dict[str, list[Node]], containments2: dict[str, list[Node]]
    ) -> bool:
        if containments1.keys() != containments2.keys():
            return False
        return all(
            len(containments1[name]) == len(containments2[name])
            and all(
                DynamicNode._shallow_node_equality(n1, n2)
                for n1, n2 in zip(containments1[name], containments2[name])
            )
            for name in containments1
        )

    @staticmethod
    def _shallow_node_equality(node1: Node | None, node2: Node | None) -> bool:
        if node1 is None and node2 is None:
            return True
        if node1 is not None and node2 is not None and node1.id is not None:
            return node1.id == node2.id
        return node1 == node2

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        try:
            qualified_name = self.concept.qualified_name() if self.concept else "<None>"
        except RuntimeError:
            qualified_name = "<cannot be calculated>"

        return (
            f"DynamicNode{{ id='{self.id}', parent='{self.parent.id if self.parent else 'null'}', "
            f"concept='{qualified_name}', propertyValues={self.property_values}, "
            f"containmentValues={{"
            + ", ".join(
                f"{k}=[{', '.join(c.id for c in v)}]" for k, v in self.containment_values.items()
            )
            + "}, referenceValues={"
            + ", ".join(f"{k}={v}" for k, v in self.reference_values.items())
            + "}, annotations={"
            + str(self.annotations)
            + "} }"
        )
