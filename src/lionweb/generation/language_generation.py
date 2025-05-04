import ast
from _ast import expr, stmt
from pathlib import Path
from typing import List, cast

import astor  # type: ignore

from lionweb.language import (Concept, Containment, DataType, Language,
                              LionCoreBuiltins, Property)
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


def language_generation(click, language: Language, output):
    body: List[stmt] = []
    body.append(
        ast.ImportFrom(
            module="lionweb.language",
            names=[
                ast.alias(name="Language", asname=None),
                ast.alias(name="Concept", asname=None),
                ast.alias(name="Property", asname=None),
                ast.alias(name="Containment", asname=None),
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
            concept_name = cast(str, language_element.get_name())
            function_body.append(
                ast.Assign(
                    targets=[ast.Name(id=concept_name, ctx=ast.Store())],
                    value=ast.Call(
                        func=ast.Name(id="Concept", ctx=ast.Load()),
                        args=[],
                        keywords=[
                            _set_lw_version(language),
                            ast.keyword(
                                arg="id", value=ast.Constant(value=language_element.id)
                            ),
                            ast.keyword(
                                arg="name", value=ast.Constant(value=concept_name)
                            ),
                            ast.keyword(
                                arg="key",
                                value=ast.Constant(value=language_element.key),
                            ),
                        ],
                    ),
                )
            )

            if language_element.get_extended_concept():
                ec = cast(Concept, language_element.get_extended_concept())
                ec_name = cast(str, ec.get_name())
                function_body.append(
                    ast.Expr(
                        ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(id=concept_name, ctx=ast.Load()),
                                attr="set_extended_concept",
                                ctx=ast.Load(),
                            ),
                            args=[ast.Name(id=ec_name, ctx=ast.Load())],
                            keywords=[],
                        )
                    )
                )

            for interf in language_element.get_implemented():
                function_body.append(
                    ast.Expr(
                        ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(id=concept_name, ctx=ast.Load()),
                                attr="add_implemented",
                                ctx=ast.Load(),
                            ),
                            args=[],
                            keywords=[],
                        )
                    )
                )

            # language.add_element(concept1)
            function_body.append(
                ast.Expr(
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id="language", ctx=ast.Load()),
                            attr="add_element",
                            ctx=ast.Load(),
                        ),
                        args=[ast.Name(id=concept_name, ctx=ast.Load())],
                        keywords=[],
                    )
                )
            )

            for feature in language_element.get_features():
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
                            ast.keyword(
                                arg="key", value=ast.Constant(value=feature.key)
                            ),
                        ],
                    )
                    function_body.append(
                        ast.Expr(
                            value=ast.Call(
                                func=ast.Attribute(
                                    value=ast.Name(id=concept_name, ctx=ast.Load()),
                                    attr="add_feature",
                                    ctx=ast.Load(),
                                ),
                                args=[feature_creation],
                                keywords=[],
                            )
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
                    else:
                        raise ValueError(cast(str, pt.get_name()))
                    feature_creation = ast.Call(
                        func=ast.Name(id="Property", ctx=ast.Load()),
                        args=[],
                        keywords=[
                            _set_lw_version(language),
                            ast.keyword(arg="id", value=ast.Constant(value=feature.id)),
                            ast.keyword(
                                arg="name", value=ast.Constant(value=feature.get_name())
                            ),
                            ast.keyword(
                                arg="key", value=ast.Constant(value=feature.key)
                            ),
                            ast.keyword(arg="type", value=property_type),
                        ],
                    )
                    function_body.append(
                        ast.Expr(
                            value=ast.Call(
                                func=ast.Attribute(
                                    value=ast.Name(id=concept_name, ctx=ast.Load()),
                                    attr="add_feature",
                                    ctx=ast.Load(),
                                ),
                                args=[feature_creation],
                                keywords=[],
                            )
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
                            ast.keyword(
                                arg="key", value=ast.Constant(value=feature.key)
                            ),
                        ],
                    )
                    function_body.append(
                        ast.Expr(
                            value=ast.Call(
                                func=ast.Attribute(
                                    value=ast.Name(id=concept_name, ctx=ast.Load()),
                                    attr="add_feature",
                                    ctx=ast.Load(),
                                ),
                                args=[feature_creation],
                                keywords=[],
                            )
                        )
                    )

    # return language
    function_body.append(ast.Return(value=ast.Name(id="language", ctx=ast.Load())))

    # Define get_language function
    get_language_def = ast.FunctionDef(
        name="get_language",
        args=ast.arguments(
            posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]
        ),
        body=function_body,
        decorator_list=[decorator],
        returns=ast.Name(id="Language", ctx=ast.Load()),
        type_comment=None,
    )

    # Wrap function in module
    body.append(get_language_def)

    for language_element in language.get_elements():
        if isinstance(language_element, Concept):
            concept_name = cast(str, language_element.get_name())
            body.append(
                ast.FunctionDef(
                    name=f"get_{concept_name.lower()}",
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
                                args=[ast.Constant(value=language_element.get_name())],
                                keywords=[],
                            )
                        )
                    ],
                    decorator_list=[],
                    returns=ast.Name(id="Concept", ctx=ast.Load()),
                    type_comment=None,
                )
            )

    module = ast.Module(body=body, type_ignores=[])

    click.echo(f"📂 Saving language to: {output}")
    generated_code = astor.to_source(module)
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)

    with Path(f"{output}/language.py").open("w", encoding="utf-8") as f:
        f.write(generated_code)
