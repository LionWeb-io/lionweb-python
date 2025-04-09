from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lionwebpython.language import Annotation
from lionwebpython.model import ClassifierInstance


class AnnotationInstance(ClassifierInstance, ABC):
    """
    While an AnnotationInstance implements ClassifierInstance, it is forbidden to hold any children,
    as the Annotation should not have any containment link.
    """

    @abstractmethod
    def get_annotation_definition(self) -> "Annotation":
        pass

    def get_classifier(self) -> "Annotation":
        return self.get_annotation_definition()
