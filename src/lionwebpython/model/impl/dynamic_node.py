from typing import TYPE_CHECKING, Dict, List, Optional, cast

if TYPE_CHECKING:
    from lionwebpython.language.concept import Concept

from lionwebpython.language.containment import Containment
from lionwebpython.model.classifier_instance import ClassifierInstance
from lionwebpython.model.has_settable_parent import HasSettableParent
from lionwebpython.model.impl.dynamic_classifier_instance import \
    DynamicClassifierInstance
from lionwebpython.model.node import Node


class DynamicNode(DynamicClassifierInstance, Node, HasSettableParent):
    def __init__(self, id: Optional[str] = None, concept: Optional["Concept"] = None):
        self._id = id
        self.concept = concept
        self.parent: Optional[Node] = None
        self.property_values: Dict[str, Optional[object]] = {}
        self.containment_values: Dict[str, List[Node]] = {}
        from lionwebpython.model.reference_value import ReferenceValue

        self.reference_values: Dict[str, List[ReferenceValue]] = {}
        from lionwebpython.model.annotation_instance import AnnotationInstance

        self.annotations: List[AnnotationInstance] = []

    def get_id(self) -> Optional[str]:
        return self._id

    def set_concept(self, concept: "Concept"):
        self.concept = concept

    def get_parent(self) -> Optional[Node]:
        return self.parent

    def get_classifier(self) -> "Concept":
        from lionwebpython.language.concept import Concept

        return cast(Concept, self.concept)

    def get_containment_feature(self) -> Optional[Containment]:
        if self.parent is None:
            return None
        for containment in self.parent.get_classifier().all_containments():
            if any(child == self for child in self.parent.get_children(containment)):
                return containment
        raise RuntimeError("Unable to find the containment feature")

    def set_parent(self, parent: Optional["ClassifierInstance"]):
        self.parent = cast(Optional[Node], parent)

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
            and {node.id for node in self.annotations}
            == {node.id for node in other.annotations}
        )

    @staticmethod
    def _shallow_containments_equality(
        containments1: Dict[str, List[Node]], containments2: Dict[str, List[Node]]
    ) -> bool:
        if containments1.keys() != containments2.keys():
            return False
        return all(
            len(containments1[name]) == len(containments2[name])
            and all(
                DynamicNode._shallow_node_equality(
                    containments1[name][i], containments2[name][i]
                )
                for i in range(len(containments1[name]))
            )
            for name in containments1.keys()
        )

    @staticmethod
    def _shallow_node_equality(node1: Optional[Node], node2: Optional[Node]) -> bool:
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
                f"{k}=[{', '.join(c.id for c in v)}]"
                for k, v in self.containment_values.items()
            )
            + "}, referenceValues={"
            + ", ".join(f"{k}={v}" for k, v in self.reference_values.items())
            + "}, annotations={"
            + str(self.annotations)
            + "} }"
        )
