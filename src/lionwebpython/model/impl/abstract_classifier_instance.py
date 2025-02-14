from typing import Generic, List, Optional, TypeVar

from lionwebpython.language.annotation import Annotation
from lionwebpython.language.classifier import Classifier
from lionwebpython.language.containment import Containment
from lionwebpython.language.reference import Reference
from lionwebpython.model.annotation_instance import AnnotationInstance
from lionwebpython.model.classifier_instance import ClassifierInstance
from lionwebpython.model.has_settable_parent import HasSettableParent
from lionwebpython.model.impl.dynamic_annotation_instance import \
    DynamicAnnotationInstance
from lionwebpython.model.reference_value import ReferenceValue

T = TypeVar("T", bound=Classifier)


class AbstractClassifierInstance(Generic[T], ClassifierInstance[T]):
    def __init__(self):
        self.annotations: List[AnnotationInstance] = []

    # Public methods for annotations

    def get_annotations(
        self, annotation: Optional[Annotation] = None
    ) -> List[AnnotationInstance]:
        if annotation is None:
            return list(self.annotations)
        return [
            a for a in self.annotations if a.get_annotation_definition() == annotation
        ]

    def add_annotation(self, instance: AnnotationInstance) -> None:
        if instance in self.annotations:
            return
        if isinstance(instance, DynamicAnnotationInstance):
            instance.set_annotated(self)
        if instance not in self.annotations:
            self.annotations.append(instance)

    def remove_annotation(self, instance: AnnotationInstance) -> None:
        if instance not in self.annotations:
            raise ValueError("Annotation instance not found")
        self.annotations.remove(instance)
        if isinstance(instance, DynamicAnnotationInstance):
            instance.set_annotated(None)

    def try_to_remove_annotation(self, instance: AnnotationInstance) -> None:
        if instance in self.annotations:
            self.annotations.remove(instance)
            if isinstance(instance, DynamicAnnotationInstance):
                instance.set_annotated(None)

    # Public methods for containments

    def remove_child(self, **kwargs) -> None:
        child = kwargs["child"]
        for containment in self.get_classifier().all_containments():
            children = self.get_children(containment)
            if child in children:
                children.remove(child)
                if isinstance(child, HasSettableParent):
                    child.set_parent(None)
                return

    def remove_child_by_index(self, containment: Containment, index: int) -> None:
        if containment not in self.get_classifier().all_containments():
            raise ValueError("Containment not belonging to this concept")
        children = self.get_children(containment)
        if index < len(children):
            del children[index]
        else:
            raise ValueError(
                f"Invalid index {index}, children count is {len(children)}"
            )

    # Public methods for references

    def remove_reference_value_by_index(self, reference: Reference, index: int) -> None:
        if reference not in self.get_classifier().all_references():
            raise ValueError("Reference not belonging to this concept")
        del self.get_reference_values(reference)[index]

    def remove_reference_value(
        self, reference: Reference, reference_value: Optional[ReferenceValue]
    ) -> None:
        if reference not in self.get_classifier().all_references():
            raise ValueError("Reference not belonging to this concept")
        if reference_value not in self.get_reference_values(reference):
            raise ValueError(
                f"Reference value not found under reference {reference.get_name()}"
            )
        self.get_reference_values(reference).remove(reference_value)
