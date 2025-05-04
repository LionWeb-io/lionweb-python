from typing import TYPE_CHECKING, Optional, cast

if TYPE_CHECKING:
    from lionweb.language import Annotation

from lionweb.model.annotation_instance import AnnotationInstance
from lionweb.model.classifier_instance import ClassifierInstance
from lionweb.model.impl.abstract_classifier_instance import \
    AbstractClassifierInstance
from lionweb.model.impl.dynamic_classifier_instance import \
    DynamicClassifierInstance


class DynamicAnnotationInstance(DynamicClassifierInstance, AnnotationInstance):
    def __init__(
        self,
        id: str,
        annotation: Optional["Annotation"] = None,
        annotated: Optional[ClassifierInstance] = None,
    ):
        super().__init__()
        self._id = id
        self.annotation = annotation
        self.annotated: Optional[ClassifierInstance] = None
        if annotated:
            self.set_annotated(annotated)

    def get_id(self) -> Optional[str]:
        return self._id

    def set_annotation(self, annotation: "Annotation"):
        self.annotation = annotation

    def set_annotated(self, annotated: Optional[ClassifierInstance]):
        from lionweb.model.impl.dynamic_node import DynamicNode

        if annotated == self.annotated:
            # Necessary to avoid infinite loops
            return
        if self.annotated and isinstance(self.annotated, DynamicNode):
            self.annotated.try_to_remove_annotation(self)

        self.annotated = annotated

        if self.annotated and isinstance(self.annotated, AbstractClassifierInstance):
            self.annotated.add_annotation(self)

    def get_annotation_definition(self) -> "Annotation":
        from lionweb.language import Annotation

        return cast(Annotation, self.annotation)

    def get_parent(self) -> Optional[ClassifierInstance]:
        return self.annotated

    def __eq__(self, other):
        if not isinstance(other, DynamicAnnotationInstance):
            return False
        return (
            self.annotation == other.annotation
            and self.id == other.id
            and self.annotated == other.annotated
            and self.property_values == other.property_values
            and self.containment_values == other.containment_values
            and self.reference_values == other.reference_values
            and self.annotations == other.annotations
        )

    def __hash__(self):
        return hash((self.id, self.annotation, self.annotated))

    def __str__(self):
        annotated_desc = self.annotated.id if self.annotated else None
        return f"DynamicAnnotationInstance{{annotation={self.annotation}, annotated={annotated_desc}}}"
