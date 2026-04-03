from abc import ABC, abstractmethod

from lionweb.model.classifier_instance import ClassifierInstance


class HasSettableParent(ABC):
    @abstractmethod
    def set_parent(self, parent: ClassifierInstance | None) -> None: ...
