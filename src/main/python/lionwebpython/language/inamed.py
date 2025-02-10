from abc import ABC, abstractmethod


class INamed(ABC):

    @abstractmethod
    def get_name(self) -> str:
        pass

