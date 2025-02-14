from abc import ABC, abstractmethod
from typing import List, Optional

from lionwebpython.language.concept import Concept
from lionwebpython.language.containment import Containment
from lionwebpython.model.classifier_instance import ClassifierInstance


class Node(ClassifierInstance, ABC):
    """
    A node is an instance of a Concept. It contains all the values associated to that instance.

    @see org.eclipse.emf.ecore.EObject Ecore equivalent <i>EObject</i>
    @see <a href="https://www.jetbrains.com/help/mps/basic-notions.html">MPS equivalent <i>Node</i>
    in documentation</a>
    @see org.modelix.model.api.INode Modelix equivalent <i>INode</i>
    <p>TODO consider if the Model should have a version too
    """

    @abstractmethod
    def get_id(self) -> Optional[str]:
        pass

    def get_root(self) -> "Node":
        raise ValueError("NOT TRANSLATED YET")

    def is_root(self) -> bool:
        raise ValueError("NOT TRANSLATED YET")

    @abstractmethod
    def get_parent(self) -> "Node":
        pass

    @abstractmethod
    def get_classifier(self) -> Concept:
        pass

    @abstractmethod
    def get_containment_feature(self) -> Containment:
        pass

    def this_and_all_descendants(self) -> List:
        raise ValueError("NOT TRANSLATED YET")
