from abc import ABC, abstractmethod
from typing import Optional

from lionwebpython.model.node import Node


class HasSettableParent(ABC):
    @abstractmethod
    def set_parent(self, parent: Optional[Node]) -> None:
        pass
