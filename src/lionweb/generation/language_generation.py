import ast
from _ast import expr, stmt
from pathlib import Path
from typing import List, cast

import astor  # type: ignore

from lionweb.generation.ASTBuilder import ASTBuilder
from lionweb.generation.base_generator import BaseGenerator
from lionweb.generation.configuration import (LanguageMappingSpec,
                                              PrimitiveTypeMappingSpec)
from lionweb.generation.generation_utils import make_function_def
from lionweb.generation.naming_utils import getter_name, to_var_name
from lionweb.language import (Classifier, Concept, Containment, DataType,
                              Enumeration, Feature, Interface, Language,
                              LionCoreBuiltins, PrimitiveType, Property)
from lionweb.language.reference import Reference
from lionweb.model import Node


class LanguageGenerator(BaseGenerator, ASTBuilder):

    def __init__(
        self,
        language_packages: tuple[LanguageMappingSpec, ...] = (),
        primitive_types: tuple[PrimitiveTypeMappingSpec, ...] = (),
    ):
        super().__init__(language_packages, primitive_types)

    def _set_lw_version(self, language: Language):
        return ast.keyword(
            arg="lion_web_version",
            value=ast.Attribute(
                value=ast.Name(id="LionWebVersion", ctx=ast.Load()),
                attr=language.get_lionweb_version().name,
                ctx=ast.Load(),
            ),
        )

    def _generate_language(self, language: Language) -> ast.Assign:
        return ast.Assign(
            targets=[ast.Name(id="language", ctx=ast.Store())],
            value=ast.Call(
                func=ast.Name(id="Language", ctx=ast.Load()),
                args=[],
                keywords=[
                    self._set_lw_version(language),
                    ast.keyword(arg="id", value=ast.Constant(value=language.id)),
                    ast.keyword(
                        arg="name", value=ast.Constant(value=language.get_name())
                    ),
                    ast.keyword(arg="key", value=ast.Constant(value=language.key)),
                    ast.keyword(
                        arg="version", value=ast.Constant(value=language.get_version())
                    ),
                ],
            ),
        )

    def _add_to_language(self, var_name: str) -> ast.Expr:
        return ast.Expr(
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="language", ctx=ast.Load()),
                    attr="add_element",
                    ctx=ast.Load(),
                ),
                args=[ast.Name(id=var_name, ctx=ast.Load())],
                keywords=[],
            )
        )

    def _set_attribute(self, container: str, attribute: str, value: bool) -> ast.stmt:
        return ast.Assign(
            targets=[
                ast.Attribute(
                    value=ast.Name(id=container, ctx=ast.Load()),
                    attr=attribute,
                    ctx=ast.Store(),
                )
            ],
            value=ast.Constant(value=attribute),
        )

    def _instantiate_lw_node(self, cls_name: str, node, extra_kws: dict = {}):
        """Generates: ClsName(id='...', name='...', key='...', lion_web_version=...)"""
        kws = {
            "lion_web_version": self.attr(
                "LionWebVersion", node.language.get_lionweb_version().name
            ),
            "id": self.const(node.id),
            "name": self.const(node.get_name()),
            "key": self.const(node.key),
        }
        if extra_kws:
            kws.update(extra_kws)
        return self.call(cls_name, keywords=kws)

    def _create_concept_in_language(
        self, concept: Concept, get_language_body: List[stmt]
    ):
        language = concept.language
        if language is None:
            raise ValueError(f"Concept {concept.get_name()} has no language")
        concept_name = cast(str, concept.get_name())
        var_name = to_var_name(concept_name)
        get_language_body.append(
            self.assign(
                var_name,
                self.call(
                    "Concept",
                    keywords={
                        "lion_web_version": self.attr(
                            "LionWebVersion", language.get_lionweb_version().name
                        ),
                        "id": self.const(concept.id),
                        "name": self.const(concept_name),
                        "key": self.const(concept.key),
                    },
                ),
            )
        )
        get_language_body.append(
            self._set_attribute(var_name, "abstract", concept.is_abstract())
        )
        get_language_body.append(
            self._set_attribute(var_name, "partition", concept.is_partition())
        )
        get_language_body.append(self._add_to_language(var_name))

    def _create_interface_in_language(
        self, interface: Interface, get_language_body: List[stmt]
    ):
        language = interface.language
        if language is None:
            raise ValueError(f"Interface {interface.get_name()} has no language")
        concept_name = cast(str, interface.get_name())
        var_name = to_var_name(concept_name)
        get_language_body.append(
            self.assign(
                var_name,
                self.call(
                    "Interface",
                    keywords={
                        "lion_web_version": self.attr(
                            "LionWebVersion", language.get_lionweb_version().name
                        ),
                        "id": self.const(interface.id),
                        "name": self.const(concept_name),
                        "key": self.const(interface.key),
                    },
                ),
            )
        )
        get_language_body.append(self._add_to_language(var_name))

    def _process_feature(self, container_name: str, feature: Feature) -> ast.Expr:
        language = cast(Language, cast(Node, feature.parent).get_parent())

        # 1. Common Arguments (shared by Reference, Containment, and Property)
        # Note: We determine the class name dynamically (Reference/Property/Containment)
        cls_name = feature.__class__.__name__

        keywords = {
            "lion_web_version": self.attr(
                "LionWebVersion", language.get_lionweb_version().name
            ),
            "id": self.const(feature.id),
            "name": self.const(feature.get_name()),
            "key": self.const(feature.key),
        }

        # 2. Specific Arguments
        if isinstance(feature, (Reference, Containment)):
            # References and Containments logic is identical
            keywords["type"] = self.name(
                to_var_name(cast(Classifier, feature.type).name)
            )
            keywords["multiple"] = self.const(feature.multiple)
            keywords["optional"] = self.const(feature.optional)

        elif isinstance(feature, Property):
            # Property needs complex type resolution
            keywords["type"] = self._resolve_property_type(feature, language)

        # 3. Create the Node: FeatureClass(...)
        feature_creation = self.call(cls_name, keywords=keywords)

        # 4. Add to Container: container.add_feature(...)
        return ast.Expr(
            self.call(self.attr(container_name, "add_feature"), args=[feature_creation])
        )

    def _resolve_property_type(self, feature: Property, language: Language) -> expr:
        """Helper to resolve the AST node for a Property's type."""
        pt = cast(DataType, feature.type)

        # Helper to generate the version kwarg for builtins
        lw_version_kw = {
            "lion_web_version": self.attr(
                "LionWebVersion", language.get_lionweb_version().name
            )
        }

        # A. Built-in String
        if pt == LionCoreBuiltins.get_string(feature.lion_web_version):
            return self.call(
                self.attr("LionCoreBuiltins", "get_string"), keywords=lw_version_kw
            )

        # B. Built-in Integer
        if pt == LionCoreBuiltins.get_integer(feature.lion_web_version):
            return self.call(
                self.attr("LionCoreBuiltins", "get_integer"), keywords=lw_version_kw
            )

        # C. Local Type (Same Language)
        if language == pt.language:
            return self.name(to_var_name(pt.get_name()))

        # D. External Type (Different Language)
        package = self._package_lookup(cast(Language, pt.language))
        if package is not None:
            return self._primitive_type_lookup_exp(package, pt.get_name())

        # Error handling
        pt_language = pt.language
        if pt_language is None:
            raise ValueError(f"Property {feature.get_name()} has no language")
        raise ValueError(
            f"We need to load {cast(str, pt.get_name())} from language "
            f"{pt_language.get_name()} but no mapping was found"
        )

    def _populate_concept_in_language(
        self, concept: Concept, get_language_body: List[stmt]
    ):
        """
        Add definition details (extension, implementation, features) to the concept.
        """
        language = concept.language
        if language is None:
            raise ValueError(f"Concept {concept.get_name()} has no language")

        concept_name = cast(str, concept.get_name())
        var_name = to_var_name(concept_name)

        if concept.get_extended_concept():
            ec = cast(Concept, concept.get_extended_concept())
            ec_var_name = to_var_name(cast(str, ec.get_name()))

            get_language_body.append(
                ast.Expr(
                    self.call(
                        self.attr(var_name, "set_extended_concept"),
                        args=[self.name(ec_var_name)],
                    )
                )
            )

        for interf in concept.get_implemented():
            interf_var_name = to_var_name(cast(str, interf.get_name()))

            get_language_body.append(
                ast.Expr(
                    self.call(
                        self.attr(var_name, "add_implemented_interface"),
                        args=[self.name(interf_var_name)],
                    )
                )
            )

        for feature in concept.get_features():
            get_language_body.append(self._process_feature(var_name, feature))

    def _populate_interface_in_language(
        self, interface: Interface, get_language_body: List[stmt]
    ):
        """
        Add definition details (extended interfaces, features) to the interface.
        """
        language = interface.language
        if language is None:
            raise ValueError(f"Interface {interface.get_name()} has no language")

        interface_name = cast(str, interface.get_name())
        var_name = to_var_name(interface_name)

        for interf in interface.get_extended_interfaces():
            extended_var_name = to_var_name(cast(str, interf.get_name()))

            get_language_body.append(
                ast.Expr(
                    self.call(
                        self.attr(var_name, "add_extended_interface"),
                        args=[self.name(extended_var_name)],
                    )
                )
            )

        for feature in interface.get_features():
            get_language_body.append(self._process_feature(var_name, feature))

    def _define_primitive_type_in_language(
        self, primitive_type: PrimitiveType, get_language_body: List[stmt]
    ):
        primitive_type_name = cast(str, primitive_type.get_name())
        language = primitive_type.language
        if language is None:
            raise ValueError(f"Primitive type {primitive_type_name} has no language")

        var_name = to_var_name(primitive_type_name)

        get_language_body.append(
            self.assign(
                var_name,
                self.call(
                    "PrimitiveType",
                    keywords={
                        "lion_web_version": self.attr(
                            "LionWebVersion", language.get_lionweb_version().name
                        ),
                        "id": self.const(primitive_type.id),
                        "name": self.const(primitive_type_name),
                        "key": self.const(primitive_type.key),
                    },
                ),
            )
        )

        get_language_body.append(self._add_to_language(var_name))

    def _define_enumeration_in_language(
        self, enumeration: Enumeration, get_language_body: List[stmt]
    ):
        enumeration_name = cast(str, enumeration.get_name())
        language = enumeration.language
        if language is None:
            raise ValueError(f"Enumeration {enumeration_name} has no language")

        var_name = to_var_name(enumeration_name)

        get_language_body.append(
            self.assign(
                var_name,
                self.call(
                    "Enumeration",
                    keywords={
                        "lion_web_version": self.attr(
                            "LionWebVersion", language.get_lionweb_version().name
                        ),
                        "id": self.const(enumeration.id),
                        "name": self.const(enumeration_name),
                        "key": self.const(enumeration.key),
                    },
                ),
            )
        )

        get_language_body.append(self._add_to_language(var_name))

    def language_generation(self, click, language: Language, output):
        # 1. Clean Static Imports
        # Instead of building nodes manually, parse a string. It's readable and standard.
        body = ast.parse(
            "from lionweb.language import Language, Concept, Containment, Enumeration, "
            "Interface, PrimitiveType, Property, Reference, LionCoreBuiltins\n"
            "from lionweb.lionweb_version import LionWebVersion\n"
            "from functools import lru_cache"
        ).body

        func_body: List[stmt] = []

        func_body.append(self._generate_language(language))

        # Creation Loop
        for el in language.get_elements():
            if isinstance(el, Concept):
                self._create_concept_in_language(el, func_body)
            elif isinstance(el, Interface):
                self._create_interface_in_language(el, func_body)
            elif isinstance(el, PrimitiveType):
                self._define_primitive_type_in_language(el, func_body)
            elif isinstance(el, Enumeration):
                self._define_enumeration_in_language(el, func_body)

        # Population Loop
        for el in language.get_elements():
            if isinstance(el, Concept):
                self._populate_concept_in_language(el, func_body)
            elif isinstance(el, Interface):
                self._populate_interface_in_language(el, func_body)

        # Return statement
        func_body.append(ast.Return(value=self.name("language")))

        # 3. Create get_language() Definition
        self.functions.append(
            make_function_def(
                name="get_language",
                args=ast.arguments(
                    posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]
                ),
                body=func_body,
                decorator_list=[
                    self.call("lru_cache", keywords={"maxsize": self.const(1)})
                ],
                returns=self.name("Language"),
            )
        )

        # 4. Generate Getters (Refactored duplication)
        for el in language.get_elements():
            if isinstance(el, Concept):
                self._add_getter_method(el, "get_concept_by_name", "Concept")
            elif isinstance(el, PrimitiveType):
                self._add_getter_method(
                    el, "get_primitive_type_by_name", "PrimitiveType"
                )

        # 5. Final Assembly
        body.extend(self.imports)
        body.extend(self.functions)

        module = ast.Module(body=body, type_ignores=[])

        # 6. Write File
        click.echo(f"📂 Saving language to: {output}")
        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)

        with (output_path / "language.py").open("w", encoding="utf-8") as file:
            file.write(astor.to_source(module))

    def _add_getter_method(self, element, lookup_method: str, return_type: str):
        """Helper to generate specific getter functions (e.g. get_my_concept)."""
        element_name = cast(str, element.get_name())

        # Body: return get_language().lookup_method("element_name")
        body: list[stmt] = [
            ast.Return(
                value=self.call(
                    self.attr(self.call("get_language"), lookup_method),
                    args=[self.const(element_name)],
                )
            )
        ]

        self.functions.append(
            make_function_def(
                name=getter_name(element_name),
                args=ast.arguments(
                    posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]
                ),
                body=body,
                decorator_list=[],
                returns=self.name(return_type),
            )
        )
