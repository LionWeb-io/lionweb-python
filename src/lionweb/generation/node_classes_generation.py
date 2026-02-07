import ast
from _ast import stmt
from pathlib import Path
from typing import List, Set, cast

import astor  # type: ignore

from lionweb.generation.ASTBuilder import ASTBuilder
from lionweb.generation.base_generator import BaseGenerator
from lionweb.generation.configuration import (LanguageMappingSpec,
                                              PrimitiveTypeMappingSpec)
from lionweb.generation.generation_utils import (make_class_def,
                                                 make_function_def)
from lionweb.generation.naming_utils import (getter_name, to_snake_case,
                                             to_type_name, to_var_name)
from lionweb.generation.topological_sorting import topological_classifiers_sort
from lionweb.language import (Concept, Containment, Feature, Interface,
                              Language, LionCoreBuiltins, Property)
from lionweb.language.classifier import Classifier
from lionweb.language.enumeration import Enumeration
from lionweb.language.reference import Reference


class NodeClassesGenerator(BaseGenerator, ASTBuilder):

    def __init__(
        self,
        language_packages: tuple[LanguageMappingSpec, ...],
        primitive_types: tuple[PrimitiveTypeMappingSpec, ...],
    ):
        super().__init__(language_packages, primitive_types)

    def _get_feature_by_name(self, feature: Feature, method: str):
        """Helper to generate self.get_classifier().method(feature_name)"""
        return self.call(
            self.attr(self.call(self.attr("self", "get_classifier")), method),
            args=[self.const(feature.get_name())],
        )

    def _generate_enumeration_class(self, enumeration: Enumeration):
        """Generate an Enum class definition."""
        members: list[stmt] = [
            self.assign(to_var_name(literal.get_name()), self.const(literal.get_name()))
            for literal in enumeration.literals
        ]
        return make_class_def(
            name=to_type_name(enumeration.get_name()),
            bases=[self.name("Enum")],
            body=members,
        )

    def _generate_interface_class(self, interface: Interface):
        """Generate an interface class definition."""
        return make_class_def(
            name=to_type_name(interface.get_name()),
            bases=[self.name("Node"), self.name("ABC")],
            body=[ast.Pass()],
        )

    def _get_safe_filename(self, element) -> str:
        """
        Generate a safe filename for an element, avoiding Python reserved keywords.
        Uses to_var_name which already handles keywords by appending underscore.
        """
        import keyword

        base_name = to_snake_case(element.get_name())

        # Check if the base name is a Python keyword or built-in
        if keyword.iskeyword(base_name) or base_name in dir(__builtins__):
            base_name = f"{base_name}_"

        return f"{base_name}.py"

    def _get_imports_for_enumeration(self) -> List[stmt]:
        """Get standard imports needed for enumerations."""
        return ast.parse("from enum import Enum").body

    def _get_imports_for_interface(self) -> List[stmt]:
        """Get standard imports needed for interfaces."""
        return ast.parse("from abc import ABC\n" "from lionweb.model import Node").body

    def _get_imports_for_concept(
        self, concept: Concept, language: Language
    ) -> List[stmt]:
        """Get imports needed for a specific concept."""
        # Standard runtime imports
        imports = ast.parse(
            "from typing import TYPE_CHECKING, Optional, cast, List\n"
            "from lionweb.model.classifier_instance_utils import (\n"
            "    get_only_reference_value_by_reference_name,\n"
            "    get_property_value_by_name,\n"
            "    get_reference_value_by_name\n"
            ")\n"
            "from lionweb.model.reference_value import ReferenceValue"
        ).body

        # Import the concept getter from language module (runtime needed)
        imports.append(
            ast.ImportFrom(
                module=".language",
                names=[ast.alias(name=getter_name(concept.name), asname=None)],
                level=0,
            )
        )

        # Determine base class import (runtime needed for inheritance)
        extended_concept = concept.get_extended_concept()
        if extended_concept:
            # Import parent concept using safe filename
            module_name = self._get_safe_filename(extended_concept)[:-3]  # Remove .py
            imports.append(
                ast.ImportFrom(
                    module=f".{module_name}",
                    names=[
                        ast.alias(
                            name=to_type_name(extended_concept.get_name()), asname=None
                        )
                    ],
                    level=0,
                )
            )
        else:
            # Import DynamicNode
            imports.append(
                ast.ImportFrom(
                    module="lionweb.model.impl.dynamic_node",
                    names=[ast.alias(name="DynamicNode", asname=None)],
                    level=0,
                )
            )

        # Collect type-checking-only imports (for type hints that could cause circular imports)
        type_checking_imports: list[stmt] = []
        imported_types = set()

        for feature in self._relevant_features(concept):
            if isinstance(feature, Property):
                # If it's a local enumeration, import at runtime (needed for isinstance checks)
                if feature.type and feature.type.language == concept.language:
                    if (
                        isinstance(feature.type, Enumeration)
                        and feature.type.name not in imported_types
                    ):
                        module_name = self._get_safe_filename(feature.type)[
                            :-3
                        ]  # Remove .py
                        imports.append(
                            ast.ImportFrom(
                                module=f".{module_name}",
                                names=[
                                    ast.alias(
                                        name=to_type_name(feature.type.name),
                                        asname=None,
                                    )
                                ],
                                level=0,
                            )
                        )
                        imported_types.add(feature.type.name)
            elif isinstance(feature, Reference):
                feature_type = cast(Classifier, feature.get_type())
                type_name = feature_type.get_name()
                # Import referenced classifiers only for type checking
                if (
                    feature_type.language == concept.language
                    and type_name not in imported_types
                ):
                    module_name = self._get_safe_filename(feature_type)[
                        :-3
                    ]  # Remove .py
                    type_checking_imports.append(
                        ast.ImportFrom(
                            module=f".{module_name}",
                            names=[
                                ast.alias(name=to_type_name(type_name), asname=None)
                            ],
                            level=0,
                        )
                    )
                    imported_types.add(type_name)

        # Add TYPE_CHECKING block if we have type-only imports
        if type_checking_imports:
            # Create: if TYPE_CHECKING:
            type_checking_block = ast.If(
                test=self.name("TYPE_CHECKING"), body=type_checking_imports, orelse=[]
            )
            imports.append(type_checking_block)

        return imports

    def _should_quote_type(self, type_name: str, feature, concept: Concept) -> bool:
        """
        Determine if a type annotation should be quoted (forward reference).
        Types under TYPE_CHECKING need to be quoted.
        """
        # References to other concepts should be quoted (they're under TYPE_CHECKING)
        if isinstance(feature, Reference):
            feature_type = cast(Classifier, feature.get_type())
            # Same language references are under TYPE_CHECKING
            return feature_type.language == concept.language

        # Enumerations and built-in types don't need quoting
        return False

    def _resolve_property_type_for_node_class(
        self, feature: Property, concept: Concept
    ) -> str:
        """Resolve the Python type string for a property in node class generation."""
        f_type = feature.type
        if f_type is None:
            raise ValueError("feature type is None")

        if f_type == LionCoreBuiltins.get_boolean(concept.lion_web_version):
            return "bool"
        elif f_type == LionCoreBuiltins.get_string(concept.lion_web_version):
            return "str"
        elif f_type == LionCoreBuiltins.get_integer(concept.lion_web_version):
            return "int"
        elif f_type.language == concept.language:
            if isinstance(f_type, Enumeration):
                return to_type_name(f_type.name)
            else:
                raise ValueError("using type that we are generating")
        else:
            qualified_name = self._data_type_lookup(f_type)
            if qualified_name is not None:
                return qualified_name
            else:
                raise ValueError(f"type: {f_type}")

    def _generate_property_setter(self, feature: Property, prop_type: str):
        return make_function_def(
            name=feature.get_name(),
            args=ast.arguments(
                posonlyargs=[],
                args=[
                    ast.arg(arg="self"),
                    ast.arg(arg="value", annotation=self.name(prop_type.strip('"'))),
                ],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
            ),
            body=[
                self.assign(
                    "property_",
                    self._get_feature_by_name(feature, "require_property_by_name"),
                ),
                ast.Expr(
                    self.call(
                        self.attr("self", "set_property_value"),
                        keywords={
                            "property": self.name("property_"),
                            "value": self.name("value"),
                        },
                    )
                ),
            ],
            decorator_list=[self.attr(feature.get_name(), "setter")],
            returns=None,
        )

    def _generate_property_getter(self, feature: Property, prop_type: str):
        return make_function_def(
            name=feature.get_name(),
            args=ast.arguments(
                posonlyargs=[],
                args=[ast.arg(arg="self")],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
            ),
            body=[
                ast.Return(
                    self.call(
                        "cast",
                        args=[
                            self.name(prop_type.strip('"')),
                            self.call(
                                "get_property_value_by_name",
                                args=[
                                    self.name("self"),
                                    self.const(feature.get_name()),
                                ],
                            ),
                        ],
                    )
                )
            ],
            decorator_list=[self.name("property")],
            returns=self.name(prop_type.strip('"')),
        )

    def _generate_reference_getter(self, feature: Reference, prop_type: str):
        # Use string annotation for forward reference
        return make_function_def(
            name=feature.get_name(),
            args=ast.arguments(
                posonlyargs=[],
                args=[ast.arg(arg="self")],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
            ),
            body=[
                self.assign(
                    "res",
                    self.call(
                        "get_only_reference_value_by_reference_name",
                        args=[self.name("self"), self.const(feature.get_name())],
                    ),
                ),
                ast.If(
                    test=self.name("res"),
                    body=[
                        ast.Return(
                            self.call(
                                "cast",
                                args=[
                                    self.const(prop_type),  # Use string for cast
                                    self.attr("res", "referred"),
                                ],
                            )
                        )
                    ],
                    orelse=[ast.Return(value=self.const(None))],
                ),
            ],
            decorator_list=[self.name("property")],
            returns=self.const(f'Optional["{prop_type}"]'),  # String annotation
        )

    def _generate_reference_setter(self, feature: Reference, prop_type: str):
        # Use string annotation for forward reference
        return make_function_def(
            name=feature.get_name(),
            args=ast.arguments(
                posonlyargs=[],
                args=[
                    ast.arg(arg="self"),
                    ast.arg(
                        arg=cast(str, feature.get_name()),
                        annotation=self.const(f'"{prop_type}"'),  # String annotation
                    ),
                ],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
            ),
            body=[
                self.assign(
                    "reference",
                    self._get_feature_by_name(feature, "get_reference_by_name"),
                ),
                ast.If(
                    test=self.attr("self", feature.get_name()),
                    body=[
                        ast.Expr(
                            self.call(
                                self.attr("self", "remove_reference_value_by_index"),
                                args=[self.name("reference"), self.const(0)],
                            )
                        )
                    ],
                    orelse=[],
                ),
                ast.Expr(
                    self.call(
                        self.attr("self", "add_reference_value"),
                        args=[
                            self.name("reference"),
                            self.call(
                                "ReferenceValue",
                                args=[
                                    self.name(feature.get_name()),
                                    self.attr(feature.get_name(), "name"),
                                ],
                            ),
                        ],
                    )
                ),
            ],
            decorator_list=[self.attr(feature.get_name(), "setter")],
            returns=None,
        )

    def _generate_multiple_reference_getter(self, feature: Reference, prop_type: str):
        # Use string annotation for forward reference
        return make_function_def(
            name=feature.name,
            args=ast.arguments(
                posonlyargs=[],
                args=[ast.arg(arg="self")],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
            ),
            body=[
                self.assign(
                    "res",
                    self.call(
                        "get_reference_value_by_name",
                        args=[self.name("self"), self.const(feature.name)],
                    ),
                ),
                ast.Return(
                    value=ast.ListComp(
                        elt=ast.IfExp(
                            test=self.name("r"),
                            body=self.call(
                                "cast",
                                args=[
                                    self.const(prop_type),
                                    self.attr("r", "referred"),
                                ],  # String for cast
                            ),
                            orelse=self.const(None),
                        ),
                        generators=[
                            ast.comprehension(
                                target=ast.Name(id="r", ctx=ast.Store()),
                                iter=self.name("res"),
                                ifs=[],
                                is_async=0,
                            )
                        ],
                    )
                ),
            ],
            decorator_list=[self.name("property")],
            returns=self.const(f'List["{prop_type}"]'),  # String annotation
        )

    def _generate_multiple_reference_adder(self, feature: Reference, prop_type: str):
        # Use string annotation for forward reference
        return make_function_def(
            name=f"add_to_{to_snake_case(feature.name)}",
            args=ast.arguments(
                posonlyargs=[],
                args=[
                    ast.arg(arg="self"),
                    ast.arg(
                        arg="new_element", annotation=self.const(f'"{prop_type}"')
                    ),  # String annotation
                ],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
            ),
            body=[
                ast.Expr(
                    self.call(
                        self.attr("self", "add_reference_value"),
                        args=[
                            self._get_feature_by_name(
                                feature, "require_reference_by_name"
                            ),
                            self.call(
                                "ReferenceValue",
                                args=[
                                    self.name("new_element"),
                                    self.attr("new_element", "name"),
                                ],
                            ),
                        ],
                    )
                )
            ],
            decorator_list=[],
            returns=None,
        )

    def node_classes_generation(self, click, language: Language, output):
        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)
        click.echo(f"📂 Generating node classes to: {output}")

        # Track all elements to generate (for avoiding duplicates across languages)
        generated_files = set()

        # Generate enumerations first (they have no dependencies)
        for element in language.get_elements():
            if isinstance(element, Enumeration):
                file_name = self._get_safe_filename(element)
                if file_name not in generated_files:
                    self._write_enumeration_file(element, output_path, click)
                    generated_files.add(file_name)

        # Generate interfaces (may have dependencies on each other but simpler)
        for element in language.get_elements():
            if isinstance(element, Interface):
                file_name = self._get_safe_filename(element)
                if file_name not in generated_files:
                    self._write_interface_file(element, output_path, click)
                    generated_files.add(file_name)

        # Generate concepts in topological order (respects inheritance)
        sorted_classifiers = cast(
            list[Concept],
            topological_classifiers_sort(
                [c for c in language.get_elements() if isinstance(c, Concept)]
            ),
        )

        for concept in sorted_classifiers:
            file_name = self._get_safe_filename(concept)
            if file_name not in generated_files:
                self._write_concept_file(concept, language, output_path, click)
                generated_files.add(file_name)

        # Generate __init__.py to export all classes (always, even if empty)
        self._write_init_file(language, output_path, click)

    def _write_enumeration_file(
        self, enumeration: Enumeration, output_path: Path, click
    ):
        """Write a single enumeration to its own file."""
        imports = self._get_imports_for_enumeration()
        class_def = self._generate_enumeration_class(enumeration)

        module = ast.Module(body=imports + [class_def], type_ignores=[])
        generated_code = astor.to_source(module)

        file_name = self._get_safe_filename(enumeration)
        file_path = output_path / file_name

        with file_path.open("w", encoding="utf-8") as f:
            f.write(generated_code)

        click.echo(f"  ✓ {file_name}")

    def _write_interface_file(self, interface: Interface, output_path: Path, click):
        """Write a single interface to its own file."""
        imports = self._get_imports_for_interface()
        class_def = self._generate_interface_class(interface)

        module = ast.Module(body=imports + [class_def], type_ignores=[])
        generated_code = astor.to_source(module)

        file_name = self._get_safe_filename(interface)
        file_path = output_path / file_name

        with file_path.open("w", encoding="utf-8") as f:
            f.write(generated_code)

        click.echo(f"  ✓ {file_name}")

    def _write_concept_file(
        self, concept: Concept, language: Language, output_path: Path, click
    ):
        """Write a single concept to its own file."""
        imports = self._get_imports_for_concept(concept, language)
        class_def = self._generate_concept_class(concept)

        module = ast.Module(body=imports + [class_def], type_ignores=[])
        generated_code = astor.to_source(module)

        file_name = self._get_safe_filename(concept)
        file_path = output_path / file_name

        with file_path.open("w", encoding="utf-8") as f:
            f.write(generated_code)

        click.echo(f"  ✓ {file_name}")

    def _write_init_file(self, language: Language, output_path: Path, click):
        """Write __init__.py to export all generated classes."""
        exports = []
        all_exports = []

        for element in language.get_elements():
            if isinstance(element, (Enumeration, Interface, Concept)):
                class_name = to_type_name(element.get_name())
                # Get safe module name (without .py extension)
                module_name = self._get_safe_filename(element)[:-3]  # Remove .py
                exports.append(f"from .{module_name} import {class_name}")
                all_exports.append(class_name)

        # Always create __init__.py, even if empty
        if exports:
            init_content = "\n".join(exports) + "\n\n__all__ = [\n"
            init_content += ",\n".join(f'    "{name}"' for name in all_exports)
            init_content += "\n]\n"
        else:
            # Empty __init__.py with just an empty __all__
            init_content = "__all__ = []\n"

        file_path = output_path / "__init__.py"
        with file_path.open("w", encoding="utf-8") as f:
            f.write(init_content)

        click.echo("  ✓ __init__.py")

    def _relevant_features(self, concept: Concept) -> List[Feature]:
        """
        Returns a list of features that should be considered for a concept, including those inherited from interfaces.
        """
        # We should consider all defined features, but also all features inherited from interfaces,
        # as they may lack definitions
        relevant_features = concept.get_features()
        interfaces = concept.get_implemented()
        examined_interfaces: Set[Classifier] = set()
        while len(interfaces) > 0:
            interface = interfaces.pop(0)
            if interface not in examined_interfaces:
                for feature in interface.get_features():
                    if feature not in relevant_features:
                        relevant_features.append(feature)
                interfaces += interface.get_extended_interfaces()
                examined_interfaces.add(interface)
        return relevant_features

    def _generate_concept_class(self, concept: Concept):
        """Generate a class definition for a concept."""
        # Generate __init__ method
        init_func = make_function_def(
            name="__init__",
            args=ast.arguments(
                posonlyargs=[],
                args=[
                    ast.arg(arg="self"),
                    ast.arg(arg="id", annotation=self.name("str")),
                ],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
            ),
            body=[
                ast.Expr(
                    self.call(
                        self.attr(self.call("super"), "__init__"),
                        args=[self.name("id")],
                    )
                ),
                ast.Assign(
                    targets=[self.attr("self", "concept")],
                    value=self.call(getter_name(concept.name)),
                ),
            ],
            decorator_list=[],
            returns=None,
        )

        # Property getter and setter (just for the first field, e.g. "title")
        methods: List[stmt] = [init_func]

        for feature in self._relevant_features(concept):
            if isinstance(feature, Property):
                prop_type = self._resolve_property_type_for_node_class(feature, concept)
                methods.append(self._generate_property_getter(feature, prop_type))
                methods.append(self._generate_property_setter(feature, prop_type))
            elif isinstance(feature, Containment):
                pass  # Containment not yet implemented
            elif isinstance(feature, Reference):
                feature_type = cast(Classifier, feature.get_type())
                prop_type = cast(str, feature_type.get_name())
                if feature.is_multiple():
                    methods.append(
                        self._generate_multiple_reference_getter(feature, prop_type)
                    )
                    methods.append(
                        self._generate_multiple_reference_adder(feature, prop_type)
                    )
                else:
                    methods.append(self._generate_reference_getter(feature, prop_type))
                    methods.append(self._generate_reference_setter(feature, prop_type))
            else:
                raise ValueError(f"Unsupported feature type: {type(feature)}")

        # Determine base class
        extended_concept = concept.get_extended_concept()
        bases: list[ast.expr] = [
            (
                self.name(to_type_name(extended_concept.get_name()))
                if extended_concept
                else self.name("DynamicNode")
            )
        ]

        return make_class_def(
            name=to_type_name(concept.get_name()),
            bases=bases,
            body=methods,
        )
