from dataclasses import dataclass, field
from typing import Dict, List

from lionweb.serialization.data.serialized_classifier_instance import \
    SerializedClassifierInstance
from lionweb.serialization.data.used_language import UsedLanguage


@dataclass
class SerializedChunk:
    serialization_format_version: str = ""
    languages: List[UsedLanguage] = field(default_factory=list)
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

    def add_language(self, language):
        self.languages.append(language)

    def __str__(self):
        return (
            f"SerializationBlock{{serialization_format_version='{self.serialization_format_version}', "
            f"languages={self.languages}, classifier_instances={self.classifier_instances}}}"
        )

    def __eq__(self, other):
        if not isinstance(other, SerializedChunk):
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
