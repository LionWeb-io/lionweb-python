import ast
from _ast import expr, stmt
from pathlib import Path
from typing import Dict, List, cast

import astor  # type: ignore

from lionweb.language import (Concept, Containment, Interface, Language,
                              LionCoreBuiltins, Property)
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
            pass
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


def _generate_concept_class(concept: Concept):
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
                        func=ast.Name(id="super", ctx=ast.Load()), args=[], keywords=[]
                    ),
                    attr="__init__",
                    ctx=ast.Load(),
                ),
                args=[
                    ast.Name(id="id", ctx=ast.Load()),
                    ast.Call(
                        func=ast.Name(
                            id=f"get_{cast(str, concept.get_name()).lower()}",
                            ctx=ast.Load(),
                        ),
                        args=[],
                        keywords=[],
                    ),
                ],
                keywords=[],
            )
        )
    ]

    init_func = ast.FunctionDef(
        name="__init__",
        args=ast.arguments(
            posonlyargs=[], args=init_args, vararg=None, kwonlyargs=[], kw_defaults=[]
        ),
        # defaults=init_defaults),
        body=init_body,
        decorator_list=[],
        returns=None,
    )

    # Property getter and setter (just for the first field, e.g. "title")
    methods: List[stmt] = [init_func]
    for feature in concept.get_features():
        if isinstance(feature, Property):
            f_type = feature.type
            if f_type == LionCoreBuiltins.get_boolean(concept.lion_web_version):
                prop_type = "bool"
            elif f_type == LionCoreBuiltins.get_string(concept.lion_web_version):
                prop_type = "str"
            elif f_type == LionCoreBuiltins.get_integer(concept.lion_web_version):
                prop_type = "int"
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
            methods.append(_generate_reference_getter(feature, prop_type))
            methods.append(_generate_reference_setter(feature, prop_type))
        else:
            raise ValueError()

    return ast.ClassDef(
        name=cast(str, concept.get_name()),
        bases=[ast.Name(id="DynamicNode", ctx=ast.Load())],
        keywords=[],
        body=methods,
        decorator_list=[],
    )


def _generate_property_setter(feature, prop_type):
    return ast.FunctionDef(
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
        ),
        body=[
            ast.Assign(
                targets=[ast.Name(id="property_", ctx=ast.Store())],
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
                        attr="get_property_by_name",
                        ctx=ast.Load(),
                    ),
                    args=[ast.Constant(value=feature.get_name())],
                    keywords=[],
                ),
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
    getter = ast.FunctionDef(
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
                            func=ast.Attribute(
                                value=ast.Name(
                                    id="ClassifierInstanceUtils", ctx=ast.Load()
                                ),
                                attr="get_property_value_by_name",
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
    return ast.FunctionDef(
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
                    func=ast.Attribute(
                        value=ast.Name(id="ClassifierInstanceUtils", ctx=ast.Load()),
                        attr="get_only_reference_value_by_reference_name",
                        ctx=ast.Load(),
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
    return ast.FunctionDef(
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


def node_classes_generation(click, language: Language, output):
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
            ],
            level=0,
        ),
        ast.ImportFrom(
            module="lionweb.model.classifier_instance_utils",
            names=[ast.alias(name="ClassifierInstanceUtils", asname=None)],
            level=0,
        ),
        ast.ImportFrom(
            module="lionweb.model.impl.dynamic_node",
            names=[ast.alias(name="DynamicNode", asname=None)],
            level=0,
        ),
        ast.ImportFrom(
            module="language",
            names=[ast.alias(name="get_language", asname=None)]
            + [
                ast.alias(name=f"get_{cast(str, c.get_name()).lower()}", asname=None)
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
    ]
    module = ast.Module(body=imports, type_ignores=[])

    for element in language.get_elements():
        e_name = cast(str, element.get_name())
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
                        ast.Name(id=cast(str, literal.get_name()), ctx=ast.Store())
                    ],
                    value=ast.Constant(value=cast(str, literal.get_name())),
                )
                for literal in element.literals
            ]

            enum_class = ast.ClassDef(
                name=e_name,
                bases=[ast.Name(id="Enum", ctx=ast.Load())],
                keywords=[],
                body=members,
                decorator_list=[],
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
            module.body.append(_generate_concept_class(classifier))
        elif isinstance(classifier, Interface):
            bases: list[expr] = []
            # if len(classifier.get_extended_interfaces()) == 0:
            #     bases.append("Node")
            # bases.append("ABC")

            classdef = ast.ClassDef(
                c_name, bases=bases, keywords=[], body=[ast.Pass()], decorator_list=[]
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
