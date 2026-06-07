from abc import ABC, abstractmethod

from lionweb.language.inamed import INamed
from lionweb.language.namespace_provider import NamespaceProvider


class NamespacedEntity(INamed, ABC):
    """
    Something with a name and contained in a Namespace.

    <p>A Concept Invoice, contained in a Language com.foo.Accounting. Therefore, Invoice will have
    the qualifiedName com.foo.Accounting.Invoice.
    """

    @abstractmethod
    def get_name(self) -> str | None:
        pass

    def qualified_name(self) -> str:
        """Compute the fully qualified name of this entity.

        Returns:
            str: The container's namespace qualifier joined with this entity's name.

        Raises:
            ValueError: If this entity has no container or no name.
        """
        container = self.get_container()
        name = self.get_name()
        if container is None:
            raise ValueError(f"No container for {self}")
        if name is None:
            raise ValueError(f"No name for {self}")
        return f"{container.namespace_qualifier()}.{name}"

    @abstractmethod
    def get_container(self) -> NamespaceProvider | None:
        pass
