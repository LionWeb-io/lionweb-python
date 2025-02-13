import re

from lionwebpython.utils.invalid_name import InvalidName


class Naming:
    QUALIFIED_NAME_PATTERN = re.compile(
        r"^[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z][a-zA-Z0-9_]*)*$"
    )

    @staticmethod
    def validate_qualified_name(qualified_name: str) -> None:
        if Naming.QUALIFIED_NAME_PATTERN.fullmatch(qualified_name) is None:
            raise InvalidName("qualified name", qualified_name)

    @staticmethod
    def validate_name(name: str) -> None:
        if name is None:
            raise ValueError("The name should not be null")
        if not re.fullmatch("[a-zA-Z][a-zA-Z0-9_]*", name) is not None:
            raise InvalidName("simple name", name)
