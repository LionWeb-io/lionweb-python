from typing import TYPE_CHECKING, List, Optional

from lionweb.utils.autoresolve import (LIONCORE_AUTORESOLVE_PREFIX,
                                       LIONCOREBUILTINS_AUTORESOLVE_PREFIX)

if TYPE_CHECKING:
    from lionweb.language.language_entity import LanguageEntity
    from lionweb.language.reference import Reference
    from lionweb.model.classifier_instance import ClassifierInstance
    from lionweb.model.node import Node
    from lionweb.model.reference_value import ReferenceValue


def get_property_value_by_name(
    instance: "ClassifierInstance", property_name: str
) -> Optional[object]:
    property_ = instance.get_classifier().get_property_by_name(
        property_name=property_name
    )
    if property_ is None:
        raise ValueError(
            f"Concept {instance.get_classifier().qualified_name()} does not contain a property named {property_name}"
        )
    return instance.get_property_value(property=property_)


def set_property_value_by_name(
    instance: "ClassifierInstance", property_name: str, value: Optional[object]
) -> None:
    classifier = instance.get_classifier()
    if classifier is None:
        raise ValueError(f"Classifier should not be null for {instance}")
    property_ = classifier.get_property_by_name(property_name=property_name)
    if property_ is None:
        raise ValueError(
            f"Concept {instance.get_classifier().qualified_name()} does not contain a property named {property_name}"
        )
    instance.set_property_value(property=property_, value=value)


def get_children(instance: "ClassifierInstance") -> List["Node"]:
    all_children = []
    for containment in instance.get_classifier().all_containments():
        all_children.extend(instance.get_children(containment))
    return all_children


def get_referred_nodes(
    instance: "ClassifierInstance", reference: Optional["Reference"] = None
) -> List["ClassifierInstance"]:
    return [
        e
        for e in [rv.get_referred() for rv in get_reference_values(instance, reference)]
        if e is not None
    ]


def get_reference_values(
    instance: "ClassifierInstance", reference: Optional["Reference"] = None
) -> List["ReferenceValue"]:
    if reference is None:
        all_referred_values = []
        for reference in instance.get_classifier().all_references():
            all_referred_values.extend(instance.get_reference_values(reference))
        return all_referred_values
    else:
        return instance.get_reference_values(reference)


def reference_to(entity: "LanguageEntity") -> "ReferenceValue":
    language = entity.language
    from lionweb.language.lioncore_builtins import LionCoreBuiltins
    from lionweb.lionweb_version import LionWebVersion
    from lionweb.model.reference_value import ReferenceValue

    if (
        language
        and language.get_name() == "LionCore_M3"
        and entity.get_lionweb_version() == LionWebVersion.V2024_1
    ):
        from lionweb.model.reference_value import ReferenceValue

        return ReferenceValue(
            referred=entity,
            resolve_info=f"{LIONCORE_AUTORESOLVE_PREFIX}{entity.get_name()}",
        )
    elif (
        language
        and isinstance(entity.language, LionCoreBuiltins)
        and entity.get_lionweb_version() == LionWebVersion.V2024_1
    ):
        return ReferenceValue(
            referred=entity,
            resolve_info=f"{LIONCOREBUILTINS_AUTORESOLVE_PREFIX}{entity.get_name()}",
        )
    else:
        return ReferenceValue(referred=entity, resolve_info=entity.get_name())


def is_builtin_element(entity: "Node") -> bool:
    from lionweb.language.language_entity import LanguageEntity

    if isinstance(entity, LanguageEntity):
        return is_builtin_element_language_entity(entity)
    return False


def is_builtin_element_language_entity(entity: "LanguageEntity") -> bool:
    language = entity.language
    from lionweb.language.lioncore_builtins import LionCoreBuiltins
    from lionweb.lionweb_version import LionWebVersion

    if (
        language
        and language.get_name() == "LionCore_M3"
        and entity.get_lionweb_version() == LionWebVersion.V2024_1
    ):
        return True
    elif (
        language
        and isinstance(language, LionCoreBuiltins)
        and entity.get_lionweb_version() == LionWebVersion.V2024_1
    ):
        return True
    return False


def get_reference_value_by_name(
    instance: "ClassifierInstance", reference_name: str
) -> List["ReferenceValue"]:
    if instance is None:
        raise ValueError("_this should not be null")
    if reference_name is None:
        raise ValueError("referenceName should not be null")

    classifier = instance.get_classifier()
    if classifier is None:
        raise ValueError(
            f"Concept should not be null for {instance} (class {type(instance).__name__})"
        )

    reference = classifier.get_reference_by_name(reference_name)
    if reference is None:
        raise ValueError(
            f"Concept {classifier.qualified_name()} does not contain a property named {reference_name}"
        )

    return instance.get_reference_values(reference)


def get_only_reference_value_by_reference_name(
    instance, reference_name: str
) -> Optional["ReferenceValue"]:
    if instance is None:
        raise ValueError("_this should not be null")
    if reference_name is None:
        raise ValueError("referenceName should not be null")

    reference_values: List["ReferenceValue"] = get_reference_value_by_name(
        instance, reference_name
    )
    if len(reference_values) > 1:
        raise RuntimeError("More than one reference value found")
    elif len(reference_values) == 0:
        return None
    else:
        return reference_values[0]
