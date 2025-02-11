from abc import ABC, abstractmethod
from lionwebpython.language.inamed import INamed
from lionwebpython.language.namespace_provider import NamespaceProvider
from typing import Optional


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
        if self.get_container() is None:
            raise ValueError("No container for " + self)
        return self.get_container().namespace_qualifier() + "." + self.get_name()

    @abstractmethod
    def get_container(self) -> Optional[NamespaceProvider]:
        pass
