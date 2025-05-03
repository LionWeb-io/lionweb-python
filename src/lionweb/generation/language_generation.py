import ast
import keyword
from _ast import ClassDef
from pathlib import Path
from typing import List, Dict, cast

import astor # type: ignore

from lionweb.language import Language, Concept, Interface, Containment, Property, Feature
from lionweb.language.classifier import Classifier
from lionweb.language.enumeration import Enumeration
from lionweb.language.primitive_type import PrimitiveType
from lionweb.language.reference import Reference

from lionweb.generation.utils import calculate_field_name

def _set_lw_version(language: Language):
    return ast.keyword(arg="lion_web_version", value=ast.Attribute(
                    value=ast.Name(id="LionWebVersion", ctx=ast.Load()),
                    attr=language.get_lionweb_version().name,
                    ctx=ast.Load()
                ))

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
                ast.keyword(arg="key", value=ast.Constant(value=language.get_key())),
                ast.keyword(arg="version", value=ast.Constant(value=language.get_version()))
            ]
        )
    )

def language_generation(click, language: Language, output):
    body = []
    body.append(ast.ImportFrom(
        module="lionweb.language",
        names=[ast.alias(name="Language", asname=None),
               ast.alias(name="Concept", asname=None)],
        level=0
    ))
    body.append(ast.ImportFrom(
        module="lionweb.lionweb_version",
        names=[ast.alias(name="LionWebVersion", asname=None)],
        level=0
    ))
    body.append(ast.ImportFrom(
            module="functools",
            names=[ast.alias(name="lru_cache", asname=None)],
            level=0
        ))
    # Decorator: @lru_cache(maxsize=1)
    decorator = ast.Call(
        func=ast.Name(id="lru_cache", ctx=ast.Load()),
        args=[],
        keywords=[ast.keyword(arg="maxsize", value=ast.Constant(value=1))]
    )

    # Function body for get_language()
    function_body = []
    function_body.append(_generate_language(language))

    for element in language.get_elements():
        if isinstance(element, Concept):
            # concept1 = Concept(...)
            function_body.append(ast.Assign(
                targets=[ast.Name(id=element.get_name(), ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Name(id="Concept", ctx=ast.Load()),
                    args=[],
                    keywords=[
                        _set_lw_version(language),
                        ast.keyword(arg="id", value=ast.Constant(value=element.id)),
                        ast.keyword(arg="name", value=ast.Constant(value=element.get_name())),
                        ast.keyword(arg="key", value=ast.Constant(value=element.get_key()))
                    ]
                )
            ))

            # language.add_element(concept1)
            function_body.append(ast.Expr(
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id="language", ctx=ast.Load()),
                        attr="add_element",
                        ctx=ast.Load()
                    ),
                    args=[ast.Name(id=element.get_name(), ctx=ast.Load())],
                    keywords=[]
                )
            ))

    # return language
    function_body.append(ast.Return(value=ast.Name(id="language", ctx=ast.Load())))

    # Define get_language function
    get_language_def = ast.FunctionDef(
        name="get_language",
        args=ast.arguments(posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]),
        body=function_body,
        decorator_list=[decorator],
        returns=ast.Name(id="Language", ctx=ast.Load()),
        type_comment=None
    )

    # Wrap function in module
    body.append(get_language_def)

    for element in language.get_elements():
        if isinstance(element, Concept):
            body.append(ast.FunctionDef(
        name=f"get_{element.get_name().lower()}",
        args=ast.arguments(posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]),
        body=[
            ast.Return(
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Call(
                            func=ast.Name(id="get_language", ctx=ast.Load()),
                            args=[],
                            keywords=[]
                        ),
                        attr="get_concept_by_name",
                        ctx=ast.Load()
                    ),
                    args=[ast.Constant(value=element.get_name())],
                    keywords=[]
                )
            )
        ],
        decorator_list=[],
        returns=ast.Name(id="Concept", ctx=ast.Load()),
        type_comment=None
    ))


    module = ast.Module(
        body=body,
        type_ignores=[]
    )

    click.echo(f"📂 Saving language to: {output}")
    generated_code = astor.to_source(module)
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)

    with Path(f"{output}/language.py").open("w", encoding="utf-8") as f:
        f.write(generated_code)
