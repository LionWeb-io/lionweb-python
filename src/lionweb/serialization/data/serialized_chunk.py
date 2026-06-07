from dataclasses import dataclass, field

from lionweb.serialization.data.language_version import LanguageVersion
from lionweb.serialization.data.serialized_classifier_instance import SerializedClassifierInstance


@dataclass
class SerializationChunk:
    """An in-memory representation of a serialized chunk of a model.

    Holds the serialization format version, the languages used, and the
    serialized classifier instances (nodes) contained in the chunk.
    """

    serialization_format_version: str = ""
    languages: list[LanguageVersion] = field(default_factory=list)
    classifier_instances: list[SerializedClassifierInstance] = field(default_factory=list)
    classifier_instances_by_id: dict[str, SerializedClassifierInstance] = field(
        default_factory=dict
    )

    def add_classifier_instance(self, instance: SerializedClassifierInstance) -> None:
        """Add a classifier instance to the chunk, indexing it by its ID.

        Args:
            instance: The serialized classifier instance to add.
        """
        self.classifier_instances_by_id[instance.id] = instance
        self.classifier_instances.append(instance)

    def get_instance_by_id(self, instance_id: str) -> SerializedClassifierInstance:
        """Look up a classifier instance by its ID.

        Args:
            instance_id: The ID of the instance to look up.

        Returns:
            The serialized classifier instance with the given ID.

        Raises:
            ValueError: If no instance with the given ID exists in this chunk.
        """
        instance = self.classifier_instances_by_id.get(instance_id)
        if instance is None:
            raise ValueError(f"Cannot find instance with ID {instance_id}")
        return instance

    def add_language(self, language: LanguageVersion) -> None:
        self.languages.append(language)

    def __str__(self):
        return (
            f"SerializationBlock{{serialization_format_version='{self.serialization_format_version}', "
            f"languages={self.languages}, classifier_instances={self.classifier_instances}}}"
        )

    def __eq__(self, other):
        if not isinstance(other, SerializationChunk):
            return False
        return (
            self.serialization_format_version == other.serialization_format_version
            and self.languages == other.languages
            and self.classifier_instances == other.classifier_instances
        )

    def __hash__(self):
        return hash(
            (
                self.serialization_format_version,
                tuple(self.languages),
                tuple(self.classifier_instances),
            )
        )

    def get_classifier_instances(self) -> list[SerializedClassifierInstance]:
        return list(self.classifier_instances)

    def get_classifier_instances_by_id(self) -> dict[str, SerializedClassifierInstance]:
        return dict(self.classifier_instances_by_id)

    def get_languages(self) -> list[LanguageVersion]:
        return list(self.languages)

    def populate_used_languages(self) -> None:
        """
        Traverse the SerializedChunk, collecting all the metapointers
        and populating the used languages accordingly.
        """
        for classifier_instance in self.classifier_instances:
            self._consider_meta_pointer(classifier_instance.get_classifier())

            for containment_value in classifier_instance.containments:
                self._consider_meta_pointer(containment_value.get_meta_pointer())

            for reference_value in classifier_instance.references:
                self._consider_meta_pointer(reference_value.get_meta_pointer())

            for property_value in classifier_instance.properties:
                self._consider_meta_pointer(property_value.get_meta_pointer())

    def _consider_meta_pointer(self, meta_pointer: object) -> None:
        used_language = LanguageVersion.from_meta_pointer(meta_pointer)
        if used_language not in self.languages:
            self.languages.append(used_language)
