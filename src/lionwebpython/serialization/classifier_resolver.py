from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from lionwebpython.language import Concept, Language
    from lionwebpython.language import Classifier, Annotation

from lionwebpython.serialization.data.metapointer import MetaPointer


class ClassifierResolver:
    def __init__(self):
        self.registered_concepts: Dict[MetaPointer, "Concept"] = {}
        self.registered_annotations: Dict[MetaPointer, "Annotation"] = {}

    def resolve_classifier(self, concept_meta_pointer: MetaPointer) -> "Classifier":
        if concept_meta_pointer in self.registered_concepts:
            return self.registered_concepts[concept_meta_pointer]
        elif concept_meta_pointer in self.registered_annotations:
            return self.registered_annotations[concept_meta_pointer]
        else:
            raise RuntimeError(
                f"Unable to resolve classifier with metaPointer {concept_meta_pointer}"
            )

    def resolve_concept(self, concept_meta_pointer: MetaPointer) -> "Concept":
        if concept_meta_pointer in self.registered_concepts:
            return self.registered_concepts[concept_meta_pointer]
        else:
            raise RuntimeError(
                f"Unable to resolve concept with metaPointer {concept_meta_pointer}"
            )

    def resolve_annotation(self, meta_pointer: MetaPointer) -> "Annotation":
        if meta_pointer in self.registered_annotations:
            return self.registered_annotations[meta_pointer]
        else:
            raise RuntimeError(
                f"Unable to resolve annotation with metaPointer {meta_pointer}"
            )

    def register_language(self, language: "Language") -> "ClassifierResolver":
        from lionwebpython.language import Annotation, Concept

        for element in language.get_elements():
            if isinstance(element, Concept):
                self.register_concept(element)
            elif isinstance(element, Annotation):
                self.register_annotation(element)
        return self

    def register_concept(self, concept: "Concept"):
        meta_pointer = MetaPointer.from_language_entity(concept)
        self.registered_concepts[meta_pointer] = concept

    def register_annotation(self, annotation: "Annotation"):
        meta_pointer = MetaPointer.from_language_entity(annotation)
        self.registered_annotations[meta_pointer] = annotation
