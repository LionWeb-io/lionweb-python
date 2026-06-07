from abc import ABC, abstractmethod

from lionweb.model.classifier_instance import ClassifierInstance


class HasSettableParent(ABC):
    """Mixin for classifier instances whose parent can be changed after creation."""

    @abstractmethod
    def set_parent(self, parent: ClassifierInstance | None) -> None:
        """Sets the parent of this instance.

        Args:
            parent: The new parent, or None to detach this instance from its parent.
        """
        ...
