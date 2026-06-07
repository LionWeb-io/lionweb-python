from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lionweb.language import Annotation, Classifier, Concept, Language

from lionweb.serialization.data.metapointer import MetaPointer


class UnresolvedClassifierError(RuntimeError):
    """Raised when a classifier, concept, or annotation cannot be resolved from a MetaPointer.

    Args:
        kind: The kind of element that could not be resolved (e.g. "classifier", "concept").
        meta_pointer: The :class:`MetaPointer` that could not be resolved.
    """

    def __init__(self, kind: str, meta_pointer: MetaPointer):
        super().__init__(f"Unable to resolve {kind} with metaPointer {meta_pointer}")
        self.kind = kind
        self.meta_pointer = meta_pointer


class ClassifierResolver:
    """Resolves classifiers, concepts, and annotations by their :class:`MetaPointer`.

    Concepts and annotations must be registered (directly or via
    :meth:`register_language`) before they can be resolved.
    """

    def __init__(self) -> None:
        self.registered_concepts: dict[MetaPointer, Concept] = {}
        self.registered_annotations: dict[MetaPointer, Annotation] = {}

    def resolve_classifier(self, concept_meta_pointer: MetaPointer) -> "Classifier":
        """Resolve a classifier (concept or annotation) by its meta-pointer.

        Args:
            concept_meta_pointer: The meta-pointer identifying the classifier.

        Returns:
            Classifier: The resolved concept or annotation.

        Raises:
            UnresolvedClassifierError: If no classifier is registered for the meta-pointer.
        """
        if concept_meta_pointer in self.registered_concepts:
            return self.registered_concepts[concept_meta_pointer]
        elif concept_meta_pointer in self.registered_annotations:
            return self.registered_annotations[concept_meta_pointer]
        else:
            raise UnresolvedClassifierError("classifier", concept_meta_pointer)

    def resolve_concept(self, concept_meta_pointer: MetaPointer) -> "Concept":
        """Resolve a concept by its meta-pointer.

        Args:
            concept_meta_pointer: The meta-pointer identifying the concept.

        Returns:
            Concept: The resolved concept.

        Raises:
            UnresolvedClassifierError: If no concept is registered for the meta-pointer.
        """
        if concept_meta_pointer in self.registered_concepts:
            return self.registered_concepts[concept_meta_pointer]
        else:
            raise UnresolvedClassifierError("concept", concept_meta_pointer)

    def resolve_annotation(self, meta_pointer: MetaPointer) -> "Annotation":
        """Resolve an annotation by its meta-pointer.

        Args:
            meta_pointer: The meta-pointer identifying the annotation.

        Returns:
            Annotation: The resolved annotation.

        Raises:
            UnresolvedClassifierError: If no annotation is registered for the meta-pointer.
        """
        if meta_pointer in self.registered_annotations:
            return self.registered_annotations[meta_pointer]
        else:
            raise UnresolvedClassifierError("annotation", meta_pointer)

    def register_language(self, language: "Language") -> "ClassifierResolver":
        from lionweb.language import Annotation, Concept

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
