from abc import ABC, abstractmethod


class NamespaceProvider(ABC):
    """Something which can act as the namespace for contained named things.

    <p>A Language com.foo.Accounting can be the NamespaceProvider for a Concept Invoice, which will
    therefore have the qualifiedName com.foo.Accounting.Invoice.
    """

    @abstractmethod
    def namespace_qualifier(self) -> str:
        pass
