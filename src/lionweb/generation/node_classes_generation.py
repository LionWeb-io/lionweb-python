import ast
from _ast import expr, stmt
from pathlib import Path
from typing import Dict, List, Optional, Set, cast

import astor  # type: ignore

from lionweb.generation.base_generator import BaseGenerator
from lionweb.generation.configuration import (LanguageMappingSpec,
                                              PrimitiveTypeMappingSpec)
from lionweb.generation.generation_utils import (make_class_def,
                                                 make_function_def)
from lionweb.generation.naming_utils import (to_snake_case, to_type_name,
                                             to_var_name)
from lionweb.language import (Concept, Containment, Feature, Interface,
                              Language, LionCoreBuiltins, Property)
from lionweb.language.classifier import Classifier
from lionweb.language.enumeration import Enumeration
from lionweb.language.primitive_type import PrimitiveType
from lionweb.language.reference import Reference


def _identify_topological_deps(
    classifiers: List[Classifier], id_to_concept
) -> Dict[str, List[str]]:
    graph: Dict[str, List[str]] = {cast(str, el.get_id()): [] for el in classifiers}
    for c in classifiers:
        if isinstance(c, Concept):
            c_id = cast(str, c.get_id())
            ec = c.get_extended_concept()
            if ec and cast(str, ec.get_id()) in id_to_concept:
                graph[c_id].append(cast(str, ec.get_id()))
            for i in c.get_implemented():
                graph[c_id].append(cast(str, i.get_id()))
            for f in c.get_features():
                if isinstance(f, Containment):
                    f_type = f.get_type()
                    if f_type and cast(str, f_type.get_id()) in id_to_concept:
                        graph[cast(str, c_id)].append(cast(str, f_type.get_id()))
        elif isinstance(c, Interface):
            c_id = cast(str, c.get_id())
            for i in c.get_extended_interfaces():
                graph[c_id].append(cast(str, i.get_id()))
            for f in c.get_features():
                if isinstance(f, Containment):
                    f_type = f.get_type()
                    if f_type and cast(str, f_type.get_id()) in id_to_concept:
                        graph[cast(str, c_id)].append(cast(str, f_type.get_id()))
        else:
            raise ValueError()
    return graph


def topological_classifiers_sort(classifiers: List[Classifier]) -> List[Classifier]:
    id_to_concept = {el.get_id(): el for el in classifiers}

    # Build graph edges: child -> [parents]
    graph: Dict[str, List[str]] = _identify_topological_deps(classifiers, id_to_concept)

    visited = set()
    sorted_list = []

    def visit(name: str):
        if name in visited:
            return
        visited.add(name)
        if name in graph:
            for dep in graph[name]:
                visit(dep)
        if name in id_to_concept:
            sorted_list.append(id_to_concept[name])

    for c in classifiers:
        visit(cast(str, c.get_id()))

    return sorted_list


def _expr_to_get_property(feature: Property):
    return ast.Call(
        func=ast.Attribute(
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="self", ctx=ast.Load()),
                    attr="get_classifier",
                    ctx=ast.Load(),
                ),
                args=[],
                keywords=[],
            ),
            attr="require_property_by_name",
            ctx=ast.Load(),
        ),
        args=[ast.Constant(value=feature.get_name())],
        keywords=[],
    )


def _expr_to_get_reference(feature: Reference):
    return ast.Call(
        func=ast.Attribute(
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="self", ctx=ast.Load()),
                    attr="get_classifier",
                    ctx=ast.Load(),
                ),
                args=[],
                keywords=[],
            ),
            attr="require_reference_by_name",
            ctx=ast.Load(),
        ),
        args=[ast.Constant(value=feature.get_name())],
        keywords=[],
    )


def _generate_property_setter(feature, prop_type):
    return make_function_def(
        name=feature.get_name(),
        args=ast.arguments(
            posonlyargs=[],
            args=[
                ast.arg(arg="self"),
                ast.arg(
                    arg="value",
                    annotation=ast.Name(id=prop_type.strip('"'), ctx=ast.Load()),
                ),
            ],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
            type_comment=None,
        ),
        body=[
            ast.Assign(
                targets=[ast.Name(id="property_", ctx=ast.Store())],
                value=_expr_to_get_property(feature),
            ),
            ast.Expr(
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id="self", ctx=ast.Load()),
                        attr="set_property_value",
                        ctx=ast.Load(),
                    ),
                    args=[],
                    keywords=[
                        ast.keyword(
                            arg="property",
                            value=ast.Name(id="property_", ctx=ast.Load()),
                        ),
                        ast.keyword(
                            arg="value", value=ast.Name(id="value", ctx=ast.Load())
                        ),
                    ],
                )
            ),
        ],
        decorator_list=[
            ast.Attribute(
                value=ast.Name(id=feature.get_name(), ctx=ast.Load()),
                attr="setter",
                ctx=ast.Load(),
            )
        ],
        returns=None,
    )


def _generate_property_getter(feature, prop_type):
    getter = make_function_def(
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
                value=ast.Call(
                    func=ast.Name(id="cast", ctx=ast.Load()),
                    args=[
                        ast.Name(id=prop_type.strip('"'), ctx=ast.Load()),
                        ast.Call(
                            func=ast.Name(
                                id="get_property_value_by_name",
                                ctx=ast.Load(),
                            ),
                            args=[
                                ast.Name(id="self", ctx=ast.Load()),
                                ast.Constant(value=feature.get_name()),
                            ],
                            keywords=[],
                        ),
                    ],
                    keywords=[],
                )
            )
        ],
        decorator_list=[ast.Name(id="property", ctx=ast.Load())],
        returns=ast.Name(id=prop_type.strip('"'), ctx=ast.Load()),
    )
    return getter


def _generate_reference_getter(feature, prop_type):
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
            ast.Assign(
                targets=[ast.Name(id="res", ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Name(
                        id="get_only_reference_value_by_reference_name", ctx=ast.Load()
                    ),
                    args=[
                        ast.Name(id="self", ctx=ast.Load()),
                        ast.Constant(value=feature.get_name()),
                    ],
                    keywords=[],
                ),
            ),
            ast.If(
                test=ast.Name(id="res", ctx=ast.Load()),
                body=[
                    ast.Return(
                        value=ast.Call(
                            func=ast.Name(id="cast", ctx=ast.Load()),
                            args=[
                                ast.Name(id=prop_type.strip('"'), ctx=ast.Load()),
                                ast.Attribute(
                                    value=ast.Name(id="res", ctx=ast.Load()),
                                    attr="referred",
                                    ctx=ast.Load(),
                                ),
                            ],
                            keywords=[],
                        )
                    )
                ],
                orelse=[ast.Return(value=ast.Constant(value=None))],
            ),
        ],
        decorator_list=[ast.Name(id="property", ctx=ast.Load())],
        returns=ast.Subscript(
            value=ast.Name(id="Optional", ctx=ast.Load()),
            slice=ast.Constant(value=prop_type.strip('"'), ctx=ast.Load()),
            ctx=ast.Load(),
        ),
    )


def _generate_reference_setter(feature, prop_type):
    return make_function_def(
        name=feature.get_name(),
        args=ast.arguments(
            posonlyargs=[],
            args=[
                ast.arg(arg="self"),
                ast.arg(
                    arg=feature.get_name(),
                    annotation=ast.Constant(value=prop_type.strip('"'), ctx=ast.Load()),
                ),
            ],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
        ),
        body=[
            ast.Assign(
                targets=[ast.Name(id="reference", ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(id="self", ctx=ast.Load()),
                                attr="get_classifier",
                                ctx=ast.Load(),
                            ),
                            args=[],
                            keywords=[],
                        ),
                        attr="get_reference_by_name",
                        ctx=ast.Load(),
                    ),
                    args=[ast.Constant(value=feature.get_name())],
                    keywords=[],
                ),
            ),
            ast.If(
                test=ast.Attribute(
                    value=ast.Name(id="self", ctx=ast.Load()),
                    attr=feature.get_name(),
                    ctx=ast.Load(),
                ),
                body=[
                    ast.Expr(
                        value=ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(id="self", ctx=ast.Load()),
                                attr="remove_reference_value_by_index",
                                ctx=ast.Load(),
                            ),
                            args=[
                                ast.Name(id="reference", ctx=ast.Load()),
                                ast.Constant(value=0),
                            ],
                            keywords=[],
                        )
                    )
                ],
                orelse=[],
            ),
            ast.Expr(
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id="self", ctx=ast.Load()),
                        attr="add_reference_value",
                        ctx=ast.Load(),
                    ),
                    args=[
                        ast.Name(id="reference", ctx=ast.Load()),
                        ast.Call(
                            func=ast.Name(id="ReferenceValue", ctx=ast.Load()),
                            args=[
                                ast.Name(id=feature.get_name(), ctx=ast.Load()),
                                ast.Attribute(
                                    value=ast.Name(
                                        id=feature.get_name(), ctx=ast.Load()
                                    ),
                                    attr="name",
                                    ctx=ast.Load(),
                                ),
                            ],
                            keywords=[],
                        ),
                    ],
                    keywords=[],
                )
            ),
        ],
        decorator_list=[
            ast.Attribute(
                value=ast.Name(id=feature.get_name(), ctx=ast.Load()),
                attr="setter",
                ctx=ast.Load(),
            )
        ],
        returns=None,
    )


class NodeClassesGenerator(BaseGenerator):

    def __init__(
        self,
        language_packages: tuple[LanguageMappingSpec, ...],
        primitive_types: tuple[PrimitiveTypeMappingSpec, ...],
    ):
        super().__init__(language_packages, primitive_types)

    def _generate_multiple_reference_getter(self, feature, prop_type):
        # @property
        decorator_property = ast.Name(id="property", ctx=ast.Load())

        # -> List['Expression']
        returns_annotation = ast.Subscript(
            value=ast.Name(id="List", ctx=ast.Load()),
            slice=ast.Constant(value=prop_type),
            ctx=ast.Load(),
        )

        # res = get_reference_value_by_name(self, 'filterCondition')
        assign_res = ast.Assign(
            targets=[ast.Name(id="res", ctx=ast.Store())],
            value=ast.Call(
                func=ast.Name(id="get_reference_value_by_name", ctx=ast.Load()),
                args=[
                    ast.Name(id="self", ctx=ast.Load()),
                    ast.Constant(value=feature.name),
                ],
                keywords=[],
            ),
        )

        # cast(Expression, r.referred)
        cast_expr = ast.Call(
            func=ast.Name(id="cast", ctx=ast.Load()),
            args=[
                ast.Name(id=prop_type, ctx=ast.Load()),
                ast.Attribute(
                    value=ast.Name(id="r", ctx=ast.Load()),
                    attr="referred",
                    ctx=ast.Load(),
                ),
            ],
            keywords=[],
        )

        # cast(Expression, r.referred) if r else None
        ifexp = ast.IfExp(
            test=ast.Name(id="r", ctx=ast.Load()),
            body=cast_expr,
            orelse=ast.Constant(value=None),
        )

        # [cast(Expression, r.referred) if r else None for r in res]
        list_comp = ast.ListComp(
            elt=ifexp,
            generators=[
                ast.comprehension(
                    target=ast.Name(id="r", ctx=ast.Store()),
                    iter=ast.Name(id="res", ctx=ast.Load()),
                    ifs=[],
                    is_async=0,
                )
            ],
        )

        # return [...]
        return_stmt = ast.Return(value=list_comp)

        # def filterConditions(self) -> List['Expression']:
        return ast.FunctionDef(
            name=feature.name,
            args=ast.arguments(
                posonlyargs=[],
                args=[ast.arg(arg="self")],
                vararg=None,
                kwonlyargs=[],
                kw_defaults=[],
                kwarg=None,
                defaults=[],
            ),
            body=[assign_res, return_stmt],
            decorator_list=[decorator_property],
            returns=returns_annotation,
            type_comment=None,
        )

    def _generate_multiple_reference_adder(self, feature, prop_type):
        # new_element: 'Expression'
        new_element_arg = ast.arg(
            arg="new_element",
            annotation=ast.Constant(prop_type),  # forward ref: 'Expression'
        )

        # ReferenceValue(new_element, new_element.name)
        reference_value_call = ast.Call(
            func=ast.Name(id="ReferenceValue", ctx=ast.Load()),
            args=[
                ast.Name(id="new_element", ctx=ast.Load()),
                ast.Attribute(
                    value=ast.Name(id="new_element", ctx=ast.Load()),
                    attr="name",
                    ctx=ast.Load(),
                ),
            ],
            keywords=[],
        )

        # self.add_reference_value(reference, ReferenceValue(...))
        call_add_reference_value = ast.Call(
            func=ast.Attribute(
                value=ast.Name(id="self", ctx=ast.Load()),
                attr="add_reference_value",
                ctx=ast.Load(),
            ),
            args=[
                _expr_to_get_reference(feature),
                reference_value_call,
            ],
            keywords=[],
        )

        return ast.FunctionDef(
            name=f"add_to_{to_snake_case(feature.name)}",
            args=ast.arguments(
                posonlyargs=[],
                args=[ast.arg(arg="self"), new_element_arg],
                vararg=None,
                kwonlyargs=[],
                kw_defaults=[],
                kwarg=None,
                defaults=[],
            ),
            body=[ast.Expr(value=call_add_reference_value)],
            decorator_list=[],
            returns=None,
            type_comment=None,
        )

    def node_classes_generation(self, click, language: Language, output):
        classifiers = [e for e in language.get_elements() if isinstance(e, Classifier)]
        if len(classifiers) == 0:
            # Nothing to generate
            return
        imports: list[stmt] = [
            ast.ImportFrom(
                module="abc", names=[ast.alias(name="ABC", asname=None)], level=0
            ),
            ast.ImportFrom(
                module="dataclasses",
                names=[ast.alias(name="dataclass", asname=None)],
                level=0,
            ),
            ast.ImportFrom(
                module="enum", names=[ast.alias(name="Enum", asname=None)], level=0
            ),
            ast.ImportFrom(
                module="typing",
                names=[
                    ast.alias(name="Optional", asname=None),
                    ast.alias(name="cast", asname=None),
                    ast.alias(name="List", asname=None),
                ],
                level=0,
            ),
            ast.ImportFrom(
                module="lionweb.model.classifier_instance_utils",
                names=[
                    ast.alias(
                        name="get_only_reference_value_by_reference_name", asname=None
                    ),
                    ast.alias(name="get_property_value_by_name", asname=None),
                ],
                level=0,
            ),
            ast.ImportFrom(
                module="lionweb.model.impl.dynamic_node",
                names=[ast.alias(name="DynamicNode", asname=None)],
                level=0,
            ),
            ast.ImportFrom(
                module=".language",
                names=[ast.alias(name="get_language", asname=None)]
                + [
                    ast.alias(
                        name=f"get_{cast(str, c.get_name()).lower()}", asname=None
                    )
                    for c in language.get_elements()
                    if isinstance(c, Concept)
                ],
                level=0,
            ),
            ast.ImportFrom(
                module="lionweb.model.reference_value",
                names=[ast.alias(name="ReferenceValue", asname=None)],
                level=0,
            ),
            ast.ImportFrom(
                module="lionweb.model",
                names=[ast.alias(name="Node", asname=None)],
                level=0,
            ),
        ]
        module = ast.Module(body=imports, type_ignores=[])

        for element in language.get_elements():
            e_name = to_type_name(cast(str, element.get_name()))
            if isinstance(element, Concept):
                pass
            elif isinstance(element, Interface):
                pass
            elif isinstance(element, PrimitiveType):
                pass
            elif isinstance(element, Enumeration):
                members: List[stmt] = [
                    ast.Assign(
                        targets=[
                            ast.Name(
                                id=cast(str, to_var_name(literal.get_name())),
                                ctx=ast.Store(),
                            )
                        ],
                        value=ast.Constant(value=cast(str, literal.get_name())),
                    )
                    for literal in element.literals
                ]

                enum_class = make_class_def(
                    name=e_name,
                    bases=[ast.Name(id="Enum", ctx=ast.Load())],
                    body=members,
                )
                module.body.append(enum_class)
            else:
                raise ValueError(f"Unsupported {element}")

        sorted_classifier = topological_classifiers_sort(
            [c for c in language.get_elements() if isinstance(c, Classifier)]
        )

        for classifier in sorted_classifier:
            c_name = cast(str, classifier.get_name())
            if isinstance(classifier, Concept):
                module.body.append(self._generate_concept_class(classifier))
            elif isinstance(classifier, Interface):
                bases: list[expr] = [
                    ast.Name(id="Node", ctx=ast.Load()),
                    ast.Name(id="ABC", ctx=ast.Load()),
                ]

                classdef = make_class_def(
                    c_name,
                    bases=bases,
                    body=[ast.Pass()],
                )
                module.body.append(classdef)
            else:
                raise ValueError()

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
        """
        :param class_name: e.g. "Book"
        :param concept_ref: e.g. "BOOK" (refers to LibraryLanguage.BOOK)
        :param fields: list of tuples like [("title", "str"), ("author", '"Writer"')]
        """
        # __init__ method
        init_args = [
            ast.arg(arg="self"),
            ast.arg(arg="id", annotation=ast.Name(id="str", ctx=ast.Load())),
        ]

        init_body: List[stmt] = [
            ast.Expr(
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Call(
                            func=ast.Name(id="super", ctx=ast.Load()),
                            args=[],
                            keywords=[],
                        ),
                        attr="__init__",
                        ctx=ast.Load(),
                    ),
                    args=[
                        ast.Name(id="id", ctx=ast.Load()),
                    ],
                    keywords=[],
                )
            ),
            ast.Assign(
                targets=[
                    ast.Attribute(
                        value=ast.Name(id="self", ctx=ast.Load()),
                        attr="concept",
                        ctx=ast.Load(),
                    )
                ],
                value=ast.Call(
                    func=ast.Name(
                        id=f"get_{cast(str, concept.get_name()).lower()}",
                        ctx=ast.Load(),
                    ),
                    args=[],
                    keywords=[],
                ),
            ),
        ]

        init_func = make_function_def(
            name="__init__",
            args=ast.arguments(
                posonlyargs=[],  # Python 3.8+
                args=init_args,
                vararg=None,
                kwonlyargs=[],
                kw_defaults=cast(List[Optional[ast.expr]], []),
                kwarg=None,
                defaults=[],
            ),
            # defaults=init_defaults),
            body=init_body,
            decorator_list=[],
            returns=None,
        )

        # Property getter and setter (just for the first field, e.g. "title")
        methods: List[stmt] = [init_func]

        for feature in self._relevant_features(concept):
            if isinstance(feature, Property):
                f_type = feature.type
                if f_type is None:
                    raise ValueError("feature type is None")
                if f_type == LionCoreBuiltins.get_boolean(concept.lion_web_version):
                    prop_type = "bool"
                elif f_type == LionCoreBuiltins.get_string(concept.lion_web_version):
                    prop_type = "str"
                elif f_type == LionCoreBuiltins.get_integer(concept.lion_web_version):
                    prop_type = "int"
                elif f_type.language == concept.language:
                    if isinstance(f_type, Enumeration):
                        # This should have been created in this file
                        prop_type = to_type_name(f_type.name)
                    else:
                        raise ValueError("using type that we are generating")
                else:
                    qualified_name = self._data_type_lookup(f_type)
                    if qualified_name is not None:
                        prop_type = qualified_name
                    else:
                        raise ValueError(f"type: {f_type}")
                methods.append(_generate_property_getter(feature, prop_type))
                methods.append(_generate_property_setter(feature, prop_type))
            elif isinstance(feature, Containment):
                # raise ValueError("Containment")
                pass
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
                    methods.append(_generate_reference_getter(feature, prop_type))
                    methods.append(_generate_reference_setter(feature, prop_type))
            else:
                raise ValueError()

        bases: list[expr] = [ast.Name(id="DynamicNode", ctx=ast.Load())]
        extended_concept = concept.get_extended_concept()
        if extended_concept is not None:
            bases = [
                ast.Name(
                    id=cast(str, to_type_name(extended_concept.get_name())),
                    ctx=ast.Load(),
                )
            ]

        return make_class_def(
            name=cast(str, to_type_name(concept.get_name())),
            bases=bases,
            body=methods,
        )
