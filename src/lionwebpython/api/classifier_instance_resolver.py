from abc import ABC, abstractmethod
from typing import Any, Optional

from lionwebpython.api.unresolved_classifier_instance_exception import \
    UnresolvedClassifierInstanceException
from lionwebpython.model.impl.proxy_node import ProxyNode


class ClassifierInstanceResolver(ABC):

    @abstractmethod
    def resolve(self, instance_id: str) -> Optional[Any]:
        """Return the classifier instance or None if not found."""
        pass

    def can_resolve(self, instance_id: str) -> bool:
        """Return True if the instance can be resolved, False otherwise."""
        return self.resolve(instance_id) is not None

    def strictly_resolve(self, instance_id: str) -> Any:
        """Return the classifier instance or raise an exception if not found."""
        instance = self.resolve(instance_id)
        if instance is None:
            raise UnresolvedClassifierInstanceException(instance_id)
        return instance

    def resolve_or_proxy(self, instance_id: str) -> Any:
        """Return the classifier instance or a ProxyNode if not found."""
        instance = self.resolve(instance_id)
        return instance if instance is not None else ProxyNode(instance_id)
