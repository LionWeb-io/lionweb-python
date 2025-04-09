from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Collection, Generic, List, Optional, TypeVar

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

    @property
    def id(self) -> Optional[str]:
        """The unique identifier of this classifier instance."""
        return self.get_id()

    @abstractmethod
    def get_id(self) -> Optional[str]:
        """Deprecated: the id property should be used instead."""
        pass

    @abstractmethod
    def get_classifier(self) -> "Classifier":
        pass

    @abstractmethod
    def get_parent(self) -> Optional["ClassifierInstance"]:
        pass

    @staticmethod
    def collect_self_and_descendants(
        self: "ClassifierInstance",
        include_annotations: bool,
        result: Collection["ClassifierInstance"],
    ):
        """
        Collects `self` and all its descendants into `result`.
        """
        if not isinstance(self, ClassifierInstance):
            raise ValueError(f"Expecting a ClassifierInstance but got {self}")
        if isinstance(result, list):
            result.append(self)
        elif isinstance(result, set):
            result.add(self)
        else:
            raise ValueError()
        if include_annotations:
            for annotation in self.get_annotations():
                ClassifierInstance.collect_self_and_descendants(
                    annotation, include_annotations, result
                )
        for child in self.get_children():
            ClassifierInstance.collect_self_and_descendants(
                child, include_annotations, result
            )

    def __hash__(self):
        return hash(self.id)
