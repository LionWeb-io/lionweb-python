from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Optional, cast

if TYPE_CHECKING:
    from lionwebpython.language.concept import Concept
    from lionwebpython.language.containment import Containment

from lionwebpython.model.classifier_instance import ClassifierInstance


class Node(ClassifierInstance["Concept"], ABC):
    """
    A node is an instance of a Concept. It contains all the values associated with that instance.
    """

    @abstractmethod
    def get_id(self) -> Optional[str]:
        """
        Returns the Node ID.
        A valid Node ID should not be None, but this method can return None in case the Node is in an invalid state.
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
