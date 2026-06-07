from typing import TYPE_CHECKING, Optional

from lionweb.utils.autoresolve import (
    LIONCORE_AUTORESOLVE_PREFIX,
    LIONCOREBUILTINS_AUTORESOLVE_PREFIX,
)

if TYPE_CHECKING:
    from lionweb.language.language_entity import LanguageEntity
    from lionweb.language.reference import Reference
    from lionweb.model.classifier_instance import ClassifierInstance
    from lionweb.model.node import Node
    from lionweb.model.reference_value import ReferenceValue


def get_property_value_by_name(instance: "ClassifierInstance", property_name: str) -> object | None:
    """Returns the value of the property with the given name on the given instance.

    Args:
        instance: The classifier instance to query.
        property_name: The name of the property to look up.

    Returns:
        The value of the property, or None.

    Raises:
        ValueError: If the classifier does not have a property with that name.
    """
    property_ = instance.get_classifier().get_property_by_name(property_name=property_name)
    if property_ is None:
        raise ValueError(
            f"Concept {instance.get_classifier().qualified_name()} does not contain a property named {property_name}"
        )
    return instance.get_property_value(property=property_)


def set_property_value_by_name(
    instance: "ClassifierInstance", property_name: str, value: object | None
) -> None:
    """Sets the value of the property with the given name on the given instance.

    Args:
        instance: The classifier instance to modify.
        property_name: The name of the property to set.
        value: The value to assign to the property.

    Raises:
        ValueError: If the classifier is None or does not have a property with that name.
    """
    classifier = instance.get_classifier()
    if classifier is None:
        raise ValueError(f"Classifier should not be null for {instance}")
    property_ = classifier.get_property_by_name(property_name=property_name)
    if property_ is None:
        raise ValueError(
            f"Concept {instance.get_classifier().qualified_name()} does not contain a property named {property_name}"
        )
    instance.set_property_value(property=property_, value=value)


def get_children(instance: "ClassifierInstance") -> list["Node"]:
    """Returns all children of the given instance, across all its containments.

    Args:
        instance: The classifier instance whose children should be collected.

    Returns:
        A list of all child nodes.
    """
    all_children = []
    for containment in instance.get_classifier().all_containments():
        all_children.extend(instance.get_children(containment))
    return all_children


def get_referred_nodes(
    instance: "ClassifierInstance", reference: Optional["Reference"] = None
) -> list["ClassifierInstance"]:
    """Returns the nodes referred to by the given instance through the given reference
    (or all references, if None is given), excluding unresolved reference values.

    Args:
        instance: The classifier instance to query.
        reference: The reference to consider, or None to consider all references.

    Returns:
        A list of the resolved referred classifier instances.
    """
    return [
        e
        for e in [rv.get_referred() for rv in get_reference_values(instance, reference)]
        if e is not None
    ]


def get_reference_values(
    instance: "ClassifierInstance", reference: Optional["Reference"] = None
) -> list["ReferenceValue"]:
    """Returns the reference values held by the given instance for the given reference
    (or for all references, if None is given).

    Args:
        instance: The classifier instance to query.
        reference: The reference to consider, or None to consider all references.

    Returns:
        A list of reference values.
    """
    if reference is None:
        all_referred_values = []
        for reference in instance.get_classifier().all_references():
            all_referred_values.extend(instance.get_reference_values(reference))
        return all_referred_values
    else:
        return instance.get_reference_values(reference)


def reference_to(entity: "LanguageEntity") -> "ReferenceValue":
    """Builds a ReferenceValue pointing to the given language entity, computing an
    appropriate `resolve_info` (using auto-resolve prefixes for LionCore_M3 / builtins
    entities when applicable).

    Args:
        entity: The language entity to build a reference to.

    Returns:
        A ReferenceValue referring to the given entity.
    """
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
    """Checks whether the given node is a builtin element of LionCore_M3 or LionCoreBuiltins.

    Args:
        entity: The node to check.

    Returns:
        True if the entity is a LanguageEntity that is a builtin element, False otherwise.
    """
    from lionweb.language.language_entity import LanguageEntity

    if isinstance(entity, LanguageEntity):
        return is_builtin_element_language_entity(entity)
    return False


def is_builtin_element_language_entity(entity: "LanguageEntity") -> bool:
    """Checks whether the given language entity is a builtin element of
    LionCore_M3 or LionCoreBuiltins (for the LionWeb 2024.1 version).

    Args:
        entity: The language entity to check.

    Returns:
        True if the entity is a builtin element, False otherwise.
    """
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
) -> list["ReferenceValue"]:
    """Returns the reference values held by the given instance for the reference
    with the given name.

    Args:
        instance: The classifier instance to query.
        reference_name: The name of the reference to look up.

    Returns:
        A list of reference values.

    Raises:
        ValueError: If `instance` or `reference_name` is None, the classifier is
            None, or the classifier does not have a reference with that name.
    """
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
    """Returns the single reference value held by the given instance for the
    reference with the given name, or None if there is none.

    Args:
        instance: The classifier instance to query.
        reference_name: The name of the reference to look up.

    Returns:
        The single reference value found, or None if there is none.

    Raises:
        ValueError: If `instance` or `reference_name` is None.
        RuntimeError: If more than one reference value is found.
    """
    if instance is None:
        raise ValueError("_this should not be null")
    if reference_name is None:
        raise ValueError("reference_name should not be null")

    reference_values: list[ReferenceValue] = get_reference_value_by_name(instance, reference_name)
    if len(reference_values) > 1:
        raise RuntimeError("More than one reference value found")
    elif len(reference_values) == 0:
        return None
    else:
        return reference_values[0]


def get_only_child_by_reference_name(instance, containment_name: str) -> Optional["Node"]:
    """Returns the single child held by the given instance for the containment
    with the given name, or None if there is none.

    Args:
        instance: The classifier instance to query.
        containment_name: The name of the containment to look up.

    Returns:
        The single child found, or None if there is none.

    Raises:
        ValueError: If `instance` or `containment_name` is None.
        RuntimeError: If more than one child is found.
    """
    if instance is None:
        raise ValueError("_this should not be null")
    if containment_name is None:
        raise ValueError("containment_name should not be null")

    children: list[Node] = instance.get_children(containment_name)
    if len(children) > 1:
        raise RuntimeError("More than one child found")
    elif len(children) == 0:
        return None
    else:
        return children[0]


def get_root(nodes: list["Node"]) -> "Node":
    """Returns the single root among the given nodes (i.e. the node without a parent).

    Args:
        nodes: The list of nodes to search.

    Returns:
        The single root node found.

    Raises:
        ValueError: If `nodes` is empty, or if there isn't exactly one root.
    """
    if len(nodes) == 0:
        raise ValueError("No nodes found")
    roots = [n for n in nodes if n.get_parent() is None]
    if len(roots) != 1:
        raise ValueError(f"Expected one root, but found {len(roots)}")
    return roots[0]
