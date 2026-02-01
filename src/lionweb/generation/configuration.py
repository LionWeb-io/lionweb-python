from dataclasses import dataclass


@dataclass(frozen=True)
class LanguageMappingSpec:
    lang: str
    package: str


@dataclass(frozen=True)
class PrimitiveTypeMappingSpec:
    primitive_type: str
    qualified_name: str
