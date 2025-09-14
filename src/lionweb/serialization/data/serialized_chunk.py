from dataclasses import dataclass, field
from typing import Dict, List

from lionweb.serialization.data.language_version import LanguageVersion
from lionweb.serialization.data.serialized_classifier_instance import \
    SerializedClassifierInstance


@dataclass
class SerializationChunk:
    serialization_format_version: str = ""
    languages: List[LanguageVersion] = field(default_factory=list)
    classifier_instances: List[SerializedClassifierInstance] = field(
        default_factory=list
    )
    classifier_instances_by_id: Dict[str, SerializedClassifierInstance] = field(
        default_factory=dict
    )

    def add_classifier_instance(self, instance):
        self.classifier_instances_by_id[instance.id] = instance
        self.classifier_instances.append(instance)

    def get_instance_by_id(self, instance_id: str) -> SerializedClassifierInstance:
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

    def get_classifier_instances(self) -> List[SerializedClassifierInstance]:
        return list(self.classifier_instances)

    def get_classifier_instances_by_id(self) -> Dict[str, object]:
        return dict(self.classifier_instances_by_id)

    def get_languages(self) -> List:
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

    def _consider_meta_pointer(self, meta_pointer):
        used_language = LanguageVersion.from_meta_pointer(meta_pointer)
        if used_language not in self.languages:
            self.languages.append(used_language)
