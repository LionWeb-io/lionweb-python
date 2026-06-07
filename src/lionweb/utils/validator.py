from abc import ABC, abstractmethod


class Validator(ABC):
    """Base class for objects that can validate an element and report issues."""

    @abstractmethod
    def validate(self, element):
        """Validate the given element.

        Args:
            element: The element to validate.

        Returns:
            ValidationResult: The result of the validation, including any issues found.
        """
        ...

    def is_valid(self, element) -> bool:
        """Checks if the validation result is successful."""
        return self.validate(element).is_successful()
