from abc import ABC, abstractmethod
from typing import List, Optional


class Node(ClassifierInstance[Concept]):
    """
    A node is an instance of a Concept. It contains all the values associated with that instance.

    Equivalent to EObject in Ecore, Node in MPS, and INode in Modelix.
    """

    @abstractmethod
    def get_id(self) -> Optional[str]:
        """
        Returns the Node ID.

        A valid Node ID should not be None, but this method can return None if the Node
        is in an invalid state.
        """
        pass

    def get_root(self) -> Optional['Node']:
        """
        If a Node is a root node in a Model, this method returns the node itself.
        Otherwise, it returns the ancestor which is a root node. Returns None if the Node is
        not inserted in a Model and is therefore considered a dangling Node.
        """
        ancestors = []
        curr = self
        while curr is not None:
            if curr not in ancestors:
                ancestors.append(curr)
                curr = curr.get_parent()
            else:
                raise RuntimeError("A circular hierarchy has been identified")
        return ancestors[-1] if ancestors else None

    def is_root(self) -> bool:
        """
        Returns True if this Node has no parent (i.e., it is a root node).
        """
        return self.get_parent() is None

    @abstractmethod
    def get_parent(self) -> Optional['Node']:
        """
        Returns the parent Node.
        """
        pass

    @abstractmethod
    def get_classifier(self):
        """
        Returns the Concept of which this Node is an instance. The Concept should not be abstract.
        """
        pass

    @abstractmethod
    def get_containment_feature(self):
        """
        Returns the Containment feature used to hold this Node within its parent.
        Will be None only for root nodes or dangling nodes.
        """
        pass

    def this_and_all_descendants(self) -> List['Node']:
        """
        Returns a list containing this node and all its descendants.
        Does not include annotations.
        """
        result = []
        self.collect_self_and_descendants(False, result)
        return result

    @abstractmethod
    def collect_self_and_descendants(self, include_annotations: bool, result: List['Node']):
        """
        Collects this Node and all its descendants into the given result list.
        """
        pass
