from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, List, Optional, TypeVar

from lionwebpython.model.has_feature_values import HasFeatureValues

T = TypeVar("T")


class ClassifierInstance(Generic[T], HasFeatureValues, ABC):
    if TYPE_CHECKING:
        from lionwebpython.language.annotation import Annotation
        from lionwebpython.language.classifier import Classifier
        from lionwebpython.model.annotation_instance import AnnotationInstance

    @abstractmethod
    def get_annotations(self, annotation: Optional["Annotation"] = None) -> List:
        pass

    @abstractmethod
    def add_annotation(self, instance: "AnnotationInstance") -> None:
        pass

    @abstractmethod
    def remove_annotation(self, instance: "AnnotationInstance") -> None:
        pass

    @abstractmethod
    def get_id(self) -> Optional[str]:
        pass

    @abstractmethod
    def get_classifier(self) -> "Classifier":
        pass

    @abstractmethod
    def get_parent(self) -> Optional["ClassifierInstance"]:
        pass

    @staticmethod
    def collect_self_and_descendants(
        self, include_annotations: bool, result: List["ClassifierInstance"]
    ):
        """
        Collects `self` and all its descendants into `result`.
        """
        result.append(self)
        if include_annotations:
            for annotation in self.get_annotations():
                ClassifierInstance.collect_self_and_descendants(
                    annotation, include_annotations, result
                )
        for child in self.get_children():
            ClassifierInstance.collect_self_and_descendants(
                child, include_annotations, result
            )
