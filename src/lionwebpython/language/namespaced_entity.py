from abc import ABC, abstractmethod
from typing import Optional

from lionwebpython.language.inamed import INamed
from lionwebpython.language.namespace_provider import NamespaceProvider


class NamespacedEntity(INamed, ABC):
    """
    Something with a name and contained in a Namespace.

    <p>A Concept Invoice, contained in a Language com.foo.Accounting. Therefore, Invoice will have
    the qualifiedName com.foo.Accounting.Invoice.
    """

    @abstractmethod
    def get_name(self) -> Optional[str]:
        pass

    def qualified_name(self) -> str:
        container = self.get_container()
        name = self.get_name()
        if container is None:
            raise ValueError("No container for " + str(self))
        if name is None:
            raise ValueError("No name for " + str(self))
        return container.namespace_qualifier() + "." + name

    @abstractmethod
    def get_container(self) -> Optional[NamespaceProvider]:
        pass
