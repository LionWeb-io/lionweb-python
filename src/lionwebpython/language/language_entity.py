from typing import TypeVar

from lionwebpython.language.ikeyed import IKeyed
from lionwebpython.language.namespaced_entity import NamespacedEntity
from lionwebpython.model.impl.m3node import M3Node

T = TypeVar("T", bound=M3Node)


class LanguageEntity(M3Node[T], NamespacedEntity, IKeyed[T]):
    pass
