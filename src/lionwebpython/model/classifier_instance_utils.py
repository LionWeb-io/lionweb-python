from typing import List, Optional

from lionwebpython.language.language_entity import LanguageEntity
from lionwebpython.language.lioncore_builtins import LionCoreBuiltins
from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.model.classifier_instance import ClassifierInstance
from lionwebpython.model.node import Node
from lionwebpython.model.reference_value import ReferenceValue


class ClassifierInstanceUtils:
    @staticmethod
    def get_property_value_by_name(
        instance: ClassifierInstance, property_name: str
    ) -> Optional[object]:
        property_ = instance.get_classifier().get_property_value(
            property_name=property_name
        )
        if property_ is None:
            raise ValueError(
                f"Concept {instance.get_classifier().qualified_name()} does not contain a property named {property_name}"
            )
        return instance.get_property_value(property=property_)

    @staticmethod
    def set_property_value_by_name(
        instance: ClassifierInstance, property_name: str, value: Optional[object]
    ) -> None:
        classifier = instance.get_classifier()
        if classifier is None:
            raise ValueError(f"Classifier should not be null for {instance}")
        property_ = classifier.get_property_value(property_name=property_name)
        if property_ is None:
            raise ValueError(
                f"Concept {instance.get_classifier().qualified_name()} does not contain a property named {property_name}"
            )
        instance.set_property_value(property=property_, value=value)

    @staticmethod
    def get_children(instance: ClassifierInstance) -> List[Node]:
        all_children = []
        for containment in instance.get_classifier().all_containments():
            all_children.extend(instance.get_children(containment))
        return all_children

    @staticmethod
    def get_referred_nodes(instance: ClassifierInstance) -> List[Node]:
        return [
            e
            for e in [
                rv.get_referred()
                for rv in ClassifierInstanceUtils.get_reference_values(instance)
            ]
            if e is not None
        ]

    @staticmethod
    def get_reference_values(instance: ClassifierInstance) -> List[ReferenceValue]:
        all_referred_values = []
        for reference in instance.get_classifier().all_references():
            all_referred_values.extend(instance.get_reference_values(reference))
        return all_referred_values

    @staticmethod
    def reference_to(entity: LanguageEntity) -> ReferenceValue:
        language = entity.get_language()
        if (
            language
            and language.get_name() == "LionCore_M3"
            and entity.get_lion_web_version() == LionWebVersion.V2024_1
        ):
            return ReferenceValue(
                entity, f"LIONCORE_AUTORESOLVE_PREFIX{entity.get_name()}"
            )
        elif (
            language
            and isinstance(entity.get_language(), LionCoreBuiltins)
            and entity.get_lion_web_version() == LionWebVersion.V2024_1
        ):
            return ReferenceValue(
                entity, f"LIONCOREBUILTINS_AUTORESOLVE_PREFIX{entity.get_name()}"
            )
        else:
            return ReferenceValue(entity, entity.get_name())

    @staticmethod
    def is_builtin_element(entity: Node) -> bool:
        if isinstance(entity, LanguageEntity):
            return ClassifierInstanceUtils.is_builtin_element_language_entity(entity)
        return False

    @staticmethod
    def is_builtin_element_language_entity(entity: LanguageEntity) -> bool:
        language = entity.get_language()
        if (
            language
            and language.get_name() == "LionCore_M3"
            and entity.get_lion_web_version() == LionWebVersion.v2024_1
        ):
            return True
        elif (
            language
            and isinstance(language, LionCoreBuiltins)
            and entity.get_lion_web_version() == LionWebVersion.v2024_1
        ):
            return True
        return False
