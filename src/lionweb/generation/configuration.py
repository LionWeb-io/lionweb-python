from dataclasses import dataclass


@dataclass(frozen=True)
class LanguageMappingSpec:
    """
    Represents a mapping specification between a LionWeb language (specified by name or id) and its associated
    python package.
    """

    lang: str
    package: str


@dataclass(frozen=True)
class PrimitiveTypeMappingSpec:
    """
    Represents the mapping specification for a LionWeb primitive type (specified by name or id) to a
    a fully qualified name of a Python type that provides it.
    """

    primitive_type: str
    qualified_name: str
