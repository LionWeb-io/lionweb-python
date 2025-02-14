from typing import List

from lionwebpython.language.annotation import Annotation
from lionwebpython.language.reference import Reference
from lionwebpython.model.annotation_instance import AnnotationInstance
from lionwebpython.model.classifier_instance import ClassifierInstance
from lionwebpython.model.reference_value import ReferenceValue


class AbstractClassifierInstance(ClassifierInstance):

    def get_annotations(self, annotation: Annotation) -> List:
        raise ValueError("NOT TRANSLATED YET")

    def add_annotation(self, instance: AnnotationInstance) -> None:
        raise ValueError("NOT TRANSLATED YET")

    def remove_annotation(self, instance: AnnotationInstance) -> None:
        raise ValueError("NOT TRANSLATED YET")

    def try_to_remove_annotation(self, instance: AnnotationInstance) -> None:
        raise ValueError("NOT TRANSLATED YET")

    def remove_child(self, **kwargs) -> None:
        raise ValueError("NOT TRANSLATED YET")

    def remove_reference_value(
        self, reference: Reference, reference_value: ReferenceValue
    ) -> None:
        raise ValueError("NOT TRANSLATED YET")
