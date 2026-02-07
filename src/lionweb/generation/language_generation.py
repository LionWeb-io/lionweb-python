import ast
from _ast import expr, stmt
from pathlib import Path
from typing import List, cast

import astor  # type: ignore

from lionweb.generation.base_generator import BaseGenerator
from lionweb.generation.configuration import (LanguageMappingSpec,
                                              PrimitiveTypeMappingSpec)
from lionweb.generation.generation_utils import make_function_def
from lionweb.generation.naming_utils import getter_name, to_var_name
from lionweb.language import (Classifier, Concept, Containment, DataType,
                              Enumeration, Interface, Language,
                              LionCoreBuiltins, PrimitiveType, Property, Feature)
from lionweb.language.reference import Reference


def _set_lw_version(language: Language):
    return ast.keyword(
        arg="lion_web_version",
        value=ast.Attribute(
            value=ast.Name(id="LionWebVersion", ctx=ast.Load()),
            attr=language.get_lionweb_version().name,
            ctx=ast.Load(),
        ),
    )


def _generate_language(language: Language) -> ast.Assign:
    return ast.Assign(
        targets=[ast.Name(id="language", ctx=ast.Store())],
        value=ast.Call(
            func=ast.Name(id="Language", ctx=ast.Load()),
            args=[],
            keywords=[
                _set_lw_version(language),
                ast.keyword(arg="id", value=ast.Constant(value=language.id)),
                ast.keyword(arg="name", value=ast.Constant(value=language.get_name())),
                ast.keyword(arg="key", value=ast.Constant(value=language.key)),
                ast.keyword(
                    arg="version", value=ast.Constant(value=language.get_version())
                ),
            ],
        ),
    )


class LanguageGenerator(BaseGenerator):

    def __init__(
        self,
        language_packages: tuple[LanguageMappingSpec, ...] = (),
        primitive_types: tuple[PrimitiveTypeMappingSpec, ...] = (),
    ):
        super().__init__(language_packages, primitive_types)

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
        ast.Assign(
            targets=[
                ast.Attribute(
                    value=ast.Name(id=container, ctx=ast.Load()),
                    attr=attribute,
                    ctx=ast.Store(),
                )
            ],
            value=ast.Constant(value=attribute),
        )


    def _create_concept_in_language(
        self, concept: Concept, get_language_body: List[stmt]
    ):
        language = concept.language
        if language is None:
            raise ValueError(f"Concept {concept.get_name()} has no language")
        concept_name = cast(str, concept.get_name())
        var_name = to_var_name(concept_name)
        get_language_body.append(
            ast.Assign(
                targets=[ast.Name(id=var_name, ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Name(id="Concept", ctx=ast.Load()),
                    args=[],
                    keywords=[
                        _set_lw_version(language),
                        ast.keyword(arg="id", value=ast.Constant(value=concept.id)),
                        ast.keyword(arg="name", value=ast.Constant(value=concept_name)),
                        ast.keyword(
                            arg="key",
                            value=ast.Constant(value=concept.key),
                        ),
                    ],
                ),
            )
        )
        get_language_body.append(self._set_attribute(var_name, "abstract", concept.is_abstract()))
        get_language_body.append(self._set_attribute(var_name, "partition", concept.is_partition()))
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
            ast.Assign(
                targets=[ast.Name(id=var_name, ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Name(id="Interface", ctx=ast.Load()),
                    args=[],
                    keywords=[
                        _set_lw_version(language),
                        ast.keyword(arg="id", value=ast.Constant(value=interface.id)),
                        ast.keyword(arg="name", value=ast.Constant(value=concept_name)),
                        ast.keyword(
                            arg="key",
                            value=ast.Constant(value=interface.key),
                        ),
                    ],
                ),
            )
        )
        get_language_body.append(self._add_to_language(var_name))

    def _process_feature(self, container_name: str, feature: Feature) -> ast.Expr:
        language = cast(Language, feature.parent.parent)
        if isinstance(feature, Reference):
            feature_creation = ast.Call(
                func=ast.Name(id="Reference", ctx=ast.Load()),
                args=[],
                keywords=[
                    _set_lw_version(language),
                    ast.keyword(arg="id", value=ast.Constant(value=feature.id)),
                    ast.keyword(
                        arg="name", value=ast.Constant(value=feature.get_name())
                    ),
                    ast.keyword(arg="key", value=ast.Constant(value=feature.key)),
                    ast.keyword(
                        arg="type",
                        value=ast.Name(
                            id=to_var_name(cast(Classifier, feature.type).name),
                            ctx=ast.Load(),
                        ),
                    ),
                    ast.keyword(
                        arg="multiple", value=ast.Constant(value=feature.multiple)
                    ),
                    ast.keyword(
                        arg="optional", value=ast.Constant(value=feature.optional)
                    ),
                ],
            )
            return ast.Expr(
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id=container_name, ctx=ast.Load()),
                            attr="add_feature",
                            ctx=ast.Load(),
                        ),
                        args=[feature_creation],
                        keywords=[],
                    )
                )
        elif isinstance(feature, Property):
            pt = cast(DataType, feature.type)
            property_type: expr
            if pt == LionCoreBuiltins.get_string(feature.lion_web_version):
                property_type = ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id="LionCoreBuiltins", ctx=ast.Load()),
                        attr="get_string",
                        ctx=ast.Load(),
                    ),
                    args=[],
                    keywords=[_set_lw_version(language)],
                )
            elif pt == LionCoreBuiltins.get_integer(feature.lion_web_version):
                property_type = ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id="LionCoreBuiltins", ctx=ast.Load()),
                        attr="get_integer",
                        ctx=ast.Load(),
                    ),
                    args=[],
                    keywords=[_set_lw_version(language)],
                )
            elif language == pt.language:
                # We have declared the property above
                property_type = ast.Name(
                    id=to_var_name(pt.get_name()), ctx=ast.Load()
                )
            else:
                package = self._package_lookup(cast(Language, pt.language))
                if package is not None:
                    property_type = self._primitive_type_lookup_exp(
                        package, pt.get_name()
                    )
                else:
                    pt_language = pt.language
                    if pt_language is None:
                        raise ValueError(
                            f"Property {feature.get_name()} has no language"
                        )
                    raise ValueError(
                        f"We need to load {cast(str, pt.get_name())} from language {pt_language.get_name()} but no mapping was found"
                    )
            feature_creation = ast.Call(
                func=ast.Name(id="Property", ctx=ast.Load()),
                args=[],
                keywords=[
                    _set_lw_version(language),
                    ast.keyword(arg="id", value=ast.Constant(value=feature.id)),
                    ast.keyword(
                        arg="name", value=ast.Constant(value=feature.get_name())
                    ),
                    ast.keyword(arg="key", value=ast.Constant(value=feature.key)),
                    ast.keyword(arg="type", value=property_type),
                ],
            )
            return ast.Expr(
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id=container_name, ctx=ast.Load()),
                            attr="add_feature",
                            ctx=ast.Load(),
                        ),
                        args=[feature_creation],
                        keywords=[],
                    )
                )
        elif isinstance(feature, Containment):
            feature_creation = ast.Call(
                func=ast.Name(id="Containment", ctx=ast.Load()),
                args=[],
                keywords=[
                    _set_lw_version(language),
                    ast.keyword(arg="id", value=ast.Constant(value=feature.id)),
                    ast.keyword(
                        arg="name", value=ast.Constant(value=feature.get_name())
                    ),
                    ast.keyword(arg="key", value=ast.Constant(value=feature.key)),
                    ast.keyword(
                        arg="type",
                        value=ast.Name(
                            id=to_var_name(cast(Classifier, feature.type).name),
                            ctx=ast.Load(),
                        ),
                    ),
                    ast.keyword(
                        arg="multiple", value=ast.Constant(value=feature.multiple)
                    ),
                    ast.keyword(
                        arg="optional", value=ast.Constant(value=feature.optional)
                    ),
                ],
            )
            return ast.Expr(
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id=container_name, ctx=ast.Load()),
                            attr="add_feature",
                            ctx=ast.Load(),
                        ),
                        args=[feature_creation],
                        keywords=[],
                    )
                )

    def _populate_concept_in_language(
        self, concept: Concept, get_language_body: List[stmt]
    ):
        """
        add to the get_language() function the definition of the concept
        """
        language = concept.language
        if language is None:
            raise ValueError(f"Concept {concept.get_name()} has no language")
        concept_name = cast(str, concept.get_name())
        var_name = to_var_name(concept_name)

        if concept.get_extended_concept():
            ec = cast(Concept, concept.get_extended_concept())
            ec_name = cast(str, ec.get_name())
            get_language_body.append(
                ast.Expr(
                    ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id=var_name, ctx=ast.Load()),
                            attr="set_extended_concept",
                            ctx=ast.Load(),
                        ),
                        args=[ast.Name(id=to_var_name(ec_name), ctx=ast.Load())],
                        keywords=[],
                    )
                )
            )

        for interf in concept.get_implemented():
            get_language_body.append(
                ast.Expr(
                    ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id=var_name, ctx=ast.Load()),
                            attr="add_implemented_interface",
                            ctx=ast.Load(),
                        ),
                        args=[
                            ast.Name(id=to_var_name(interf.get_name()), ctx=ast.Load())
                        ],
                        keywords=[],
                    )
                )
            )

        for feature in concept.get_features():
            get_language_body.append(self._process_feature(var_name, feature))

    def _populate_interface_in_language(
        self, interface: Interface, get_language_body: List[stmt]
    ):
        """
        add to the get_language() function the definition of the interface
        """
        language = interface.language
        if language is None:
            raise ValueError(f"Interface {interface.get_name()} has no language")
        interface_name = cast(str, interface.get_name())
        var_name = to_var_name(interface_name)

        for interf in interface.get_extended_interfaces():
            get_language_body.append(
                ast.Expr(
                    ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id=var_name, ctx=ast.Load()),
                            attr="add_extended_interface",
                            ctx=ast.Load(),
                        ),
                        args=[
                            ast.Name(id=to_var_name(interf.get_name()), ctx=ast.Load())
                        ],
                        keywords=[],
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
            ast.Assign(
                targets=[ast.Name(id=var_name, ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Name(id="PrimitiveType", ctx=ast.Load()),
                    args=[],
                    keywords=[
                        _set_lw_version(language),
                        ast.keyword(
                            arg="id", value=ast.Constant(value=primitive_type.id)
                        ),
                        ast.keyword(
                            arg="name", value=ast.Constant(value=primitive_type_name)
                        ),
                        ast.keyword(
                            arg="key",
                            value=ast.Constant(value=primitive_type.key),
                        ),
                    ],
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
            ast.Assign(
                targets=[ast.Name(id=var_name, ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Name(id="Enumeration", ctx=ast.Load()),
                    args=[],
                    keywords=[
                        _set_lw_version(language),
                        ast.keyword(arg="id", value=ast.Constant(value=enumeration.id)),
                        ast.keyword(
                            arg="name", value=ast.Constant(value=enumeration_name)
                        ),
                        ast.keyword(
                            arg="key",
                            value=ast.Constant(value=enumeration.key),
                        ),
                    ],
                ),
            )
        )
        get_language_body.append(self._add_to_language(var_name))

    def language_generation(self, click, language: Language, output):
        body: List[stmt] = []
        body.append(
            ast.ImportFrom(
                module="lionweb.language",
                names=[
                    ast.alias(name="Language", asname=None),
                    ast.alias(name="Concept", asname=None),
                    ast.alias(name="Containment", asname=None),
                    ast.alias(name="Enumeration", asname=None),
                    ast.alias(name="Interface", asname=None),
                    ast.alias(name="PrimitiveType", asname=None),
                    ast.alias(name="Property", asname=None),
                    ast.alias(name="Reference", asname=None),
                    ast.alias(name="LionCoreBuiltins", asname=None),
                ],
                level=0,
            )
        )
        body.append(
            ast.ImportFrom(
                module="lionweb.lionweb_version",
                names=[ast.alias(name="LionWebVersion", asname=None)],
                level=0,
            )
        )
        body.append(
            ast.ImportFrom(
                module="functools",
                names=[ast.alias(name="lru_cache", asname=None)],
                level=0,
            )
        )
        # Decorator: @lru_cache(maxsize=1)
        decorator = ast.Call(
            func=ast.Name(id="lru_cache", ctx=ast.Load()),
            args=[],
            keywords=[ast.keyword(arg="maxsize", value=ast.Constant(value=1))],
        )

        # Function body for get_language()
        function_body: List[stmt] = []
        function_body.append(_generate_language(language))

        for language_element in language.get_elements():
            if isinstance(language_element, Concept):
                self._create_concept_in_language(language_element, function_body)

            if isinstance(language_element, Interface):
                self._create_interface_in_language(language_element, function_body)

            if isinstance(language_element, PrimitiveType):
                self._define_primitive_type_in_language(language_element, function_body)

            if isinstance(language_element, Enumeration):
                self._define_enumeration_in_language(language_element, function_body)

        for language_element in language.get_elements():
            if isinstance(language_element, Concept):
                self._populate_concept_in_language(language_element, function_body)

            if isinstance(language_element, Interface):
                self._populate_interface_in_language(language_element, function_body)

        # return language
        function_body.append(ast.Return(value=ast.Name(id="language", ctx=ast.Load())))

        # Define get_language function
        get_language_def = make_function_def(
            name="get_language",
            args=ast.arguments(
                posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]
            ),
            body=function_body,
            decorator_list=[decorator],
            returns=ast.Name(id="Language", ctx=ast.Load()),
        )

        # Wrap function in module
        self.functions.append(get_language_def)

        for language_element in language.get_elements():
            if isinstance(language_element, Concept):
                concept_name = cast(str, language_element.get_name())
                self.functions.append(
                    make_function_def(
                        name=getter_name(concept_name),
                        args=ast.arguments(
                            posonlyargs=[],
                            args=[],
                            kwonlyargs=[],
                            kw_defaults=[],
                            defaults=[],
                        ),
                        body=[
                            ast.Return(
                                value=ast.Call(
                                    func=ast.Attribute(
                                        value=ast.Call(
                                            func=ast.Name(
                                                id="get_language", ctx=ast.Load()
                                            ),
                                            args=[],
                                            keywords=[],
                                        ),
                                        attr="get_concept_by_name",
                                        ctx=ast.Load(),
                                    ),
                                    args=[
                                        ast.Constant(value=language_element.get_name())
                                    ],
                                    keywords=[],
                                )
                            )
                        ],
                        decorator_list=[],
                        returns=ast.Name(id="Concept", ctx=ast.Load()),
                    )
                )
            if isinstance(language_element, PrimitiveType):
                element_name = cast(str, language_element.get_name())
                self.functions.append(
                    make_function_def(
                        name=getter_name(element_name),
                        args=ast.arguments(
                            posonlyargs=[],
                            args=[],
                            kwonlyargs=[],
                            kw_defaults=[],
                            defaults=[],
                        ),
                        body=[
                            ast.Return(
                                value=ast.Call(
                                    func=ast.Attribute(
                                        value=ast.Call(
                                            func=ast.Name(
                                                id="get_language", ctx=ast.Load()
                                            ),
                                            args=[],
                                            keywords=[],
                                        ),
                                        attr="get_primitive_type_by_name",
                                        ctx=ast.Load(),
                                    ),
                                    args=[
                                        ast.Constant(value=language_element.get_name())
                                    ],
                                    keywords=[],
                                )
                            )
                        ],
                        decorator_list=[],
                        returns=ast.Name(id="PrimitiveType", ctx=ast.Load()),
                    )
                )

        for i in self.imports:
            body.append(i)

        for f in self.functions:
            body.append(f)

        module = ast.Module(body=body, type_ignores=[])

        click.echo(f"📂 Saving language to: {output}")
        generated_code = astor.to_source(module)
        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)

        with Path(f"{output}/language.py").open("w", encoding="utf-8") as file:
            file.write(generated_code)
