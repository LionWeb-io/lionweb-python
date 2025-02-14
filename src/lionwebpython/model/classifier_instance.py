from abc import ABC, abstractmethod
from typing import Collection, List, Optional

from lionwebpython.language.annotation import Annotation
from lionwebpython.language.classifier import Classifier
from lionwebpython.model.annotation_instance import AnnotationInstance
from lionwebpython.model.has_feature_values import HasFeatureValues


class ClassifierInstance(HasFeatureValues, ABC):

    @abstractmethod
    def get_annotations(self, annotation: Annotation) -> List:
        pass

    @abstractmethod
    def add_annotation(self, instance: AnnotationInstance) -> None:
        pass

    @abstractmethod
    def remove_annotation(self, instance: AnnotationInstance) -> None:
        pass

    @abstractmethod
    def get_id(self) -> Optional[str]:
        pass

    @abstractmethod
    def get_classifier(self) -> Classifier:
        pass

    @abstractmethod
    def get_parent(self) -> "ClassifierInstance":
        pass

    @staticmethod
    @abstractmethod
    def collect_self_and_descendants(
        self: "ClassifierInstance", include_annotations: bool, result: Collection
    ) -> None:
        pass
