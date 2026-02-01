import ast
from dataclasses import dataclass
from typing import Optional

from lionweb.generation.utils import dotted_name_expr
from lionweb.language import Language, DataType


@dataclass(frozen=True)
class LanguageMappingSpec:
    lang: str
    package: str


@dataclass(frozen=True)
class PrimitiveTypeMappingSpec:
    primitive_type: str
    qualified_name: str
