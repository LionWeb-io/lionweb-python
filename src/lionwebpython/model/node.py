from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Optional, cast

if TYPE_CHECKING:
    from lionwebpython.language.concept import Concept
    from lionwebpython.language.containment import Containment

from typing_extensions import TypeGuard

from lionwebpython.model.classifier_instance import ClassifierInstance


def _properties_equality(node1, node2) -> bool:
    for property in node1.get_classifier().all_properties():
        if node1.get_property_value(property=property) != node2.get_property_value(
            property=property
        ):
            return False
    return True


def _shallow_references_equality(node1, node2) -> bool:
    for reference in node1.get_classifier().all_references():
        references1 = node1.get_reference_values(reference=reference)
        references2 = node2.get_reference_values(reference=reference)
        if len(references1) != len(references2):
            return False
        for i in range(len(references1)):
            ref1 = references1[i]
            ref2 = references2[i]
            referred_id1 = ref1.get_referred_id()
            referred_id2 = ref2.get_referred_id()
            resolve_info1 = ref1.get_resolve_info()
            resolve_info2 = ref2.get_resolve_info()

            if referred_id1 is None and referred_id2 is None:
                if resolve_info1 != resolve_info2:
                    return False
            else:
                if referred_id1 != referred_id2:
                    return False
    return True


def _shallow_classifier_instance_equality(
    classifier_instance_1, classifier_instance_2
) -> bool:
    if classifier_instance_1 is None and classifier_instance_2 is None:
        return True
    if classifier_instance_1 is not None and classifier_instance_2 is not None:
        id1 = classifier_instance_1.id
        id2 = classifier_instance_2.id
        if id1 is not None:
            return id1 == id2
        return False
    return False


def _shallow_containments_equality(
    classifier_instance_1, classifier_instance_2
) -> bool:
    for containment in classifier_instance_1.get_classifier().all_containments():
        nodes1 = classifier_instance_1.get_children(containment=containment)
        nodes2 = classifier_instance_2.get_children(containment=containment)
        if len(nodes1) != len(nodes2):
            return False
        for i in range(len(nodes1)):
            if not _shallow_classifier_instance_equality(nodes1[i], nodes2[i]):
                return False
    return True


def _shallow_annotations_equality(annotations1: list, annotations2: list) -> bool:
    if len(annotations1) != len(annotations2):
        return False
    for i in range(len(annotations1)):
        if not _shallow_classifier_instance_equality(annotations1[i], annotations2[i]):
            return False
    return True


class Node(ClassifierInstance["Concept"], ABC):
    """
    A node is an instance of a Concept. It contains all the values associated with that instance.


    Attributes:
        id: The unique identifier of this node. A valid Node should have a proper ID
            but this property can return None if the Node is in an invalid state.
    """

    @property
    def id(self) -> Optional[str]:
        """The unique identifier of this node."""
        return self.get_id()

    @abstractmethod
    def get_id(self) -> Optional[str]:
        """
        Returns the Node ID.
        A valid Node ID should not be None, but this method can return None in case the Node is in an invalid state.

        Deprecated: the id property should be used instead.
        """
        pass

    def get_root(self) -> "Node":
        """
        If a Node is a root node in a Model, this method returns the node itself.
        Otherwise, it returns the ancestor which is a root node.
        This method should return None only if the Node is not inserted in a Model.
        """
        ancestors = []
        curr: Optional["Node"] = self
        while curr is not None:
            if curr not in ancestors:
                ancestors.append(curr)
                curr = curr.get_parent()
            else:
                raise RuntimeError("A circular hierarchy has been identified")
        return ancestors[-1]

    def is_root(self) -> bool:
        """
        Checks if this node is a root node.
        """
        return self.get_parent() is None

    @abstractmethod
    def get_parent(self) -> Optional["Node"]:
        """
        Returns the parent of this node.
        """
        pass

    @abstractmethod
    def get_classifier(self) -> "Concept":
        """
        Returns the concept of which this Node is an instance. The Concept should not be abstract.
        """
        pass

    @abstractmethod
    def get_containment_feature(self) -> Optional["Containment"]:
        """
        Returns the Containment feature used to hold this Node within its parent.
        This will be None only for root nodes or dangling nodes.
        """
        pass

    def this_and_all_descendants(self) -> List["Node"]:
        """
        Returns a list containing this node and all its descendants. Does not include annotations.
        """
        result: List["Node"] = []
        ClassifierInstance.collect_self_and_descendants(
            self, False, cast(List[ClassifierInstance], result)
        )
        return result

    def __eq__(self, other):
        if self is other:
            return True
        if not is_node(other):
            return False
        return (
            self.id == other.id
            and _shallow_classifier_instance_equality(
                self.get_parent(), other.get_parent()
            )
            and _shallow_classifier_instance_equality(
                self.get_classifier(), other.get_classifier()
            )
            and _properties_equality(self, other)
            and _shallow_containments_equality(self, other)
            and _shallow_references_equality(self, other)
            and _shallow_annotations_equality(self, other)
        )


def is_node(obj: object) -> TypeGuard[Node]:
    """
    Returns True if the given object behaves like a Node.
    This check is used instead of isinstance(..., Node) to avoid issues
    with complex inheritance involving generics and ABCs, which may cause
    infinite recursion or unreliable type checks in Python's runtime.
    It verifies the presence of key methods that identify Node-like behavior.
    """
    return hasattr(obj, "get_id") and hasattr(obj, "get_root")
