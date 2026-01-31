import ast
from dataclasses import dataclass

from lionweb.generation.utils import dotted_name_expr
from lionweb.language import Language, PrimitiveType


@dataclass(frozen=True)
class LanguageMappingSpec:
    lang: str
    package: str


@dataclass(frozen=True)
class PrimitiveTypeMappingSpec:
    primitive_type: str
    qualified_name: str


class BaseGenerator:

    def __init__(self, language_packages: tuple[LanguageMappingSpec, ...],
                 primitive_types: tuple[PrimitiveTypeMappingSpec, ...],):
        self.language_packages = language_packages
        self.primitive_types = primitive_types

    def _package_lookup(self, language: Language) -> str | None:
        for mapping in self.language_packages:
            if language.id == mapping.lang or language.name == mapping.lang:
                return mapping.package
        return None

    def _primitive_type_lookup(self, primitive_type: PrimitiveType) -> str | None:
        for mapping in self.primitive_types:
            if primitive_type.id == mapping.primitive_type or primitive_type.name == mapping.primitive_type:
                return mapping.qualified_name
        return None

    def _primitive_type_lookup_exp(self, package_str: str, primitive_type_name: str) -> ast.expr:
        # my.package.name
        base = dotted_name_expr(package_str)

        # my.package.name.language
        lang_mod = ast.Attribute(value=base, attr="language", ctx=ast.Load())

        # my.package.name.language.get_language()
        get_lang_call = ast.Call(
            func=ast.Attribute(value=lang_mod, attr="get_language", ctx=ast.Load()),
            args=[],
            keywords=[],
        )

        # my.package.name.language.get_language().get_primitive_type_by_name("somePrimitiveTypeName")
        full_call = ast.Call(
            func=ast.Attribute(
                value=get_lang_call,
                attr="get_primitive_type_by_name",
                ctx=ast.Load(),
            ),
            args=[ast.Constant(value=primitive_type_name)],
            keywords=[],
        )

        return full_call