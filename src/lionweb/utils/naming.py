import re

from lionweb.utils.invalid_name import InvalidName


class Naming:
    """Helpers to validate names and qualified names used in LionWeb models."""

    QUALIFIED_NAME_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z][a-zA-Z0-9_]*)*$")

    @staticmethod
    def validate_qualified_name(qualified_name: str) -> None:
        """Validate that the given string is a well-formed qualified name.

        Args:
            qualified_name: The qualified name to validate.

        Raises:
            InvalidName: If the qualified name does not match the expected pattern.
        """
        if Naming.QUALIFIED_NAME_PATTERN.fullmatch(qualified_name) is None:
            raise InvalidName("qualified name", qualified_name)

    @staticmethod
    def validate_name(name: str) -> None:
        """Validate that the given string is a well-formed simple name.

        Args:
            name: The name to validate.

        Raises:
            ValueError: If `name` is None.
            InvalidName: If the name does not match the expected pattern.
        """
        if name is None:
            raise ValueError("The name should not be null")
        if not re.fullmatch("[a-zA-Z][a-zA-Z0-9_]*", name) is not None:
            raise InvalidName("simple name", name)
