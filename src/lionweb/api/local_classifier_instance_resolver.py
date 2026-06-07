from collections.abc import Iterable
from typing import TYPE_CHECKING, Optional, cast

from lionweb.api.classifier_instance_resolver import ClassifierInstanceResolver

if TYPE_CHECKING:
    from lionweb.model import ClassifierInstance


class LocalClassifierInstanceResolver(ClassifierInstanceResolver):
    """A resolver backed by an in-memory dictionary of classifier instances, keyed by ID."""

    def __init__(self, *instances: "ClassifierInstance"):
        self.instances: dict[str, ClassifierInstance] = {
            cast(str, instance.id): instance for instance in instances if instance.id
        }

    def add(self, instance: "ClassifierInstance") -> "LocalClassifierInstanceResolver":
        """Register a single classifier instance, keyed by its ID.

        Args:
            instance: The classifier instance to register.

        Returns:
            LocalClassifierInstanceResolver: This instance, to allow chaining.
        """
        if instance.id is not None:
            self.instances[instance.id] = instance
        return self

    def resolve(self, instance_id: str) -> Optional["ClassifierInstance"]:
        """Look up a classifier instance by ID in the local registry.

        Args:
            instance_id: The ID of the classifier instance to resolve.

        Returns:
            The registered classifier instance, or None if not registered.
        """
        return self.instances.get(instance_id)

    def extend(self, instances: Iterable["ClassifierInstance"]) -> None:
        """Register multiple classifier instances.

        Args:
            instances: The classifier instances to register.
        """
        for instance in instances:
            self.add(instance)

    def add_tree(self, root: "ClassifierInstance") -> None:
        """Register the given instance and all of its descendants, recursively.

        Args:
            root: The root of the tree of classifier instances to register.
        """
        self.add(root)
        for child in root.get_children():
            self.add_tree(child)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({list(self.instances.keys())})"

    __str__ = __repr__
