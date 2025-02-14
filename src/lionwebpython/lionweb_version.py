from enum import Enum


class LionWebVersion(Enum):
    """A LionWeb Version. Note that the version is used to refer to the specifications but also to the
    versions of LionCore and LionCore Builtins, as they should always be aligned."""

    V2023_1 = "2023.1"
    V2024_1 = "2024.1"

    @classmethod
    def current_version(cls) -> "LionWebVersion":
        return cls.V2024_1

    @classmethod
    def from_value(cls, version_string: str) -> "LionWebVersion":
        for version in cls:
            if version.value == version_string:
                return version
        raise ValueError(f"Invalid serializationFormatVersion: {version_string}")
