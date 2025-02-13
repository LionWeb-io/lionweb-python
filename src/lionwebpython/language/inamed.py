from abc import ABC, abstractmethod
from typing import Optional


class INamed(ABC):

    @abstractmethod
    def get_name(self) -> Optional[str]:
        pass
