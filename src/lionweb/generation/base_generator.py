import ast
from typing import Optional

from lionweb.generation.configuration import (LanguageMappingSpec,
                                              PrimitiveTypeMappingSpec)
from lionweb.language import DataType, Language


class BaseGenerator:
    """
    Represents a base generator for managing mappings, imports, and function definitions.

    This class provides functionality for looking up language-specific packages, mapping
    primitive types to their qualified names, and managing abstract syntax tree (AST)
    imports and function definitions. It is designed to handle the relationships
    between languages, packages, and primitive types efficiently.

    Attributes:
        language_packages (tuple[LanguageMappingSpec, ...]): A tuple of mappings
            defining relationships between programming languages and their package
            specifications.
        primitive_types (tuple[PrimitiveTypeMappingSpec, ...]): A tuple of mappings
            defining relationships between primitive types and corresponding qualified
            names.
        imports (list[ast.ImportFrom]): A list of `ast.ImportFrom` objects representing
            the imports added during processing.
        language_to_imports (dict[str, ast.ImportFrom]): A dictionary mapping package
            strings to their respective `ast.ImportFrom` objects.
        functions (list[ast.FunctionDef]): A list of `ast.FunctionDef` objects representing
            function definitions handled by the generator.
    """

    def __init__(
        self,
        language_packages: tuple[LanguageMappingSpec, ...],
        primitive_types: tuple[PrimitiveTypeMappingSpec, ...],
    ):
        self.language_packages = language_packages
        self.primitive_types = primitive_types
        self.imports: list[ast.ImportFrom] = []
        self.language_to_imports: dict[str, ast.ImportFrom] = {}
        self.functions: list[ast.FunctionDef] = []

    def _package_lookup(self, language: Language) -> str | None:
        for mapping in self.language_packages:
            if language.id == mapping.lang or language.name == mapping.lang:
                return mapping.package
        return None

    def _data_type_lookup(self, primitive_type: DataType) -> str | None:
        for mapping in self.primitive_types:
            if (
                primitive_type.id == mapping.primitive_type
                or primitive_type.name == mapping.primitive_type
            ):
                return mapping.qualified_name
        return None

    def _primitive_type_lookup_exp(
        self, package_str: str, primitive_type_name: Optional[str]
    ) -> ast.expr:
        if primitive_type_name is None:
            raise ValueError("Primitive type name must be specified")

        existing_import = self.language_to_imports.get(package_str)
        if existing_import is None:
            clean_language_name = package_str.split(".")[-1]
            new_import = ast.ImportFrom(
                module=f"{package_str}.language",
                names=[
                    ast.alias(
                        name="get_language",
                        asname=f"get_{clean_language_name}_language",
                    )
                ],
                level=0,
            )
            self.imports.append(new_import)
            self.language_to_imports[package_str] = new_import
            existing_import = new_import
        alias = existing_import.names[-1].asname
        if alias is None:
            raise ValueError("Language package must be imported with an alias")

        # my.package.name.language.get_language()
        get_lang_call = ast.Call(
            func=ast.Name(id=alias, ctx=ast.Load()),
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
