from abc import ABC, abstractmethod


class INamed(ABC):
    """
    Interface for objects that have a name.
    """

    @abstractmethod
    def get_name(self) -> str:
        """
        Returns the name of the object.
        """
        pass