from typing import TypeVar

from lionwebpython.language.feature import Feature
from lionwebpython.model.impl.m3node import M3Node

T = TypeVar("T", bound=M3Node)


class Link(Feature[T]):

    def is_multiple(self) -> bool:
        raise ValueError("NOT YET TRANSLATED")
