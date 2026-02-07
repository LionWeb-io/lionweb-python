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
                                    self.name(prop_type.strip('"')),
                                    self.attr("res", "referred"),
                                ],
                            )
                        )
                    ],
                    orelse=[ast.Return(value=self.const(None))],
                ),
            ],
            decorator_list=[self.name("property")],
            returns=ast.Subscript(
                value=self.name("Optional"),
                slice=self.const(prop_type.strip('"')),
                ctx=ast.Load(),
            ),
        )

    def _generate_reference_setter(self, feature: Reference, prop_type: str):
        return make_function_def(
            name=feature.get_name(),
            args=ast.arguments(
                posonlyargs=[],
                args=[
                    ast.arg(arg="self"),
                    ast.arg(
                        arg=cast(str, feature.get_name()),
                        annotation=self.const(prop_type.strip('"')),
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
                                args=[self.name(prop_type), self.attr("r", "referred")],
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
            returns=ast.Subscript(
                value=self.name("List"),
                slice=self.const(prop_type),
                ctx=ast.Load(),
            ),
        )

    def _generate_multiple_reference_adder(self, feature: Reference, prop_type: str):
        return make_function_def(
            name=f"add_to_{to_snake_case(feature.name)}",
            args=ast.arguments(
                posonlyargs=[],
                args=[
                    ast.arg(arg="self"),
                    ast.arg(arg="new_element", annotation=self.const(prop_type)),
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
        classifiers = [e for e in language.get_elements() if isinstance(e, Classifier)]
        if len(classifiers) == 0:
            # Nothing to generate
            return

        # Use ast.parse for cleaner import generation, similar to language_generation.py
        body = ast.parse(
            "from abc import ABC\n"
            "from dataclasses import dataclass\n"
            "from enum import Enum\n"
            "from typing import Optional, cast, List\n"
            "from lionweb.model.classifier_instance_utils import (\n"
            "    get_only_reference_value_by_reference_name,\n"
            "    get_property_value_by_name,\n"
            "    get_reference_value_by_name\n"
            ")\n"
            "from lionweb.model.impl.dynamic_node import DynamicNode\n"
            "from lionweb.model.reference_value import ReferenceValue\n"
            "from lionweb.model import Node"
        ).body

        # Add language-specific imports
        language_imports = [ast.alias(name="get_language", asname=None)] + [
            ast.alias(name=getter_name(c.name), asname=None)
            for c in language.get_elements()
            if isinstance(c, Concept)
        ]
        body.append(ast.ImportFrom(module=".language", names=language_imports, level=0))

        module = ast.Module(body=body, type_ignores=[])

        # Generate enumerations first
        for element in language.get_elements():
            if isinstance(element, Enumeration):
                module.body.append(self._generate_enumeration_class(element))

        sorted_classifier = topological_classifiers_sort(
            [c for c in language.get_elements() if isinstance(c, Classifier)]
        )

        # Generate classifiers (concepts and interfaces)
        for classifier in sorted_classifier:
            if isinstance(classifier, Concept):
                module.body.append(self._generate_concept_class(classifier))
            elif isinstance(classifier, Interface):
                module.body.append(self._generate_interface_class(classifier))

        click.echo(f"📂 Saving ast to: {output}")
        generated_code = astor.to_source(module)
        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)
        with Path(f"{output}/node_classes.py").open("w", encoding="utf-8") as f:
            f.write(generated_code)

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
