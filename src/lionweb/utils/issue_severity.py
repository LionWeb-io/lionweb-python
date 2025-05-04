from enum import IntEnum


class IssueSeverity(IntEnum):
    WARNING = 1
    ERROR = 2

    def __str__(self) -> str:
        return self.name.capitalize()
