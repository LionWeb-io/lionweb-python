from abc import ABC, abstractmethod


class Validator(ABC):
    @abstractmethod
    def validate(self, element):
        """Abstract method to validate an element."""
        pass

    def is_valid(self, element) -> bool:
        """Checks if the validation result is successful."""
        return self.validate(element).is_successful()
