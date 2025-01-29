from typing import Optional, TypeVar, Generic
from abc import ABC

from lionwebpython.language.IKeyed import IKeyed

T = TypeVar('T', bound='M3Node')


class LanguageEntity(M3Node[T], NamespacedEntity, IKeyed[T], ABC, Generic[T]):
    """
    A LanguageEntity is an element with an identity within a Language.

    Equivalent to EClassifier in Ecore, IStructureElement in MPS, and SElement in SModel.
    """

    def __init__(self, lion_web_version: Optional['LionWebVersion'] = None,
                 language: Optional['Language'] = None, name: Optional[str] = None, id: Optional[str] = None):
        if lion_web_version is None:
            lion_web_version = LionWebVersion.current_version()

        super().__init__(lion_web_version)
        self.set_name(name)

        if id:
            self.set_id(id)

        if language:
            language.add_element(self)
        else:
            self.set_parent(None)

    def get_language(self) -> Optional['Language']:
        """
        Returns the Language containing this element. It is the parent, casted to Language.
        """
        parent = self.get_parent()
        if parent is None:
            return None
        elif isinstance(parent, Language):
            return parent
        else:
            raise ValueError("The parent of this LanguageEntity is not a Language")

    def get_name(self) -> Optional[str]:
        """
        Returns the name of this LanguageEntity.
        """
        return self.get_property_value("name", str)

    def set_name(self, name: Optional[str]) -> T:
        """
        Sets the name of this LanguageEntity.
        """
        self.set_property_value("name", name)
        return self  # type: ignore

    def get_container(self) -> Optional['NamespaceProvider']:
        """
        Returns the container, which should be a NamespaceProvider.
        """
        parent = self.get_parent()
        if parent is None:
            return None
        elif isinstance(parent, NamespaceProvider):
            return parent
        else:
            raise ValueError("The parent is not a NamespaceProvider")

    def get_key(self) -> str:
        """
        Returns the key of this LanguageEntity.
        """
        return self.get_property_value("key", str)

    def set_key(self, key: str) -> T:
        """
        Sets the key of this LanguageEntity.
        """
        self.set_property_value("key", key)
        return self  # type: ignore

    def __str__(self) -> str:
        return super().__str__() + "{" + f"qualifiedName={DebugUtils.qualified_name(self)}" + "}"
