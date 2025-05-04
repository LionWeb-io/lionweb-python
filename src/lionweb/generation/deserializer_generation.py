import ast
from _ast import stmt
from pathlib import Path
from typing import List, cast

import astor  # type: ignore

from lionweb.language import Concept, Language


def deserializer_generation(click, language: Language, output):
    module_body = []

    # Import statements
    module_body.append(
        ast.ImportFrom(
            module="gen.language",
            names=[
                ast.alias(name=f"get_{cast(str, c.get_name()).lower()}", asname=None)
                for c in language.get_elements()
                if isinstance(c, Concept)
            ],
            level=0,
        )
    )
    module_body.append(
        ast.ImportFrom(
            module="gen.node_classes",
            names=[
                ast.alias(name=cast(str, c.get_name()), asname=None)
                for c in language.get_elements()
                if isinstance(c, Concept)
            ],
            level=0,
        )
    )
    module_body.append(
        ast.ImportFrom(
            module="lionweb.serialization",
            names=[ast.alias(name="AbstractSerialization", asname=None)],
            level=0,
        )
    )
    module_body.append(
        ast.ImportFrom(
            module="lionweb.serialization.data.serialized_classifier_instance",
            names=[ast.alias(name="SerializedClassifierInstance", asname=None)],
            level=0,
        )
    )

    register_func_body: List[stmt] = []
    for language_element in language.get_elements():
        if isinstance(language_element, Concept):
            concept_name = cast(str, language_element.get_name())
            # deserializer() inner function
            register_func_body.append(
                ast.FunctionDef(
                    name=f"deserializer_{concept_name.lower()}",
                    args=ast.arguments(
                        posonlyargs=[],
                        args=[
                            ast.arg(arg="classifier"),
                            ast.arg(
                                arg="serialized_instance",
                                annotation=ast.Name(
                                    id="SerializedClassifierInstance", ctx=ast.Load()
                                ),
                            ),
                            ast.arg(arg="deserialized_instances_by_id"),
                            ast.arg(arg="properties_values"),
                        ],
                        kwonlyargs=[],
                        kw_defaults=[],
                        defaults=[],
                    ),
                    body=[
                        ast.Return(
                            value=ast.Call(
                                func=ast.Name(id=concept_name, ctx=ast.Load()),
                                args=[
                                    ast.Attribute(
                                        value=ast.Name(
                                            id="serialized_instance", ctx=ast.Load()
                                        ),
                                        attr="id",
                                        ctx=ast.Load(),
                                    )
                                ],
                                keywords=[],
                            )
                        )
                    ],
                    decorator_list=[],
                    returns=None,
                )
            )

            # register_deserializers() function
            register_func_body.append(
                ast.Expr(
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Attribute(
                                value=ast.Name(id="serialization", ctx=ast.Load()),
                                attr="instantiator",
                                ctx=ast.Load(),
                            ),
                            attr="register_custom_deserializer",
                            ctx=ast.Load(),
                        ),
                        args=[
                            ast.Attribute(
                                value=ast.Call(
                                    func=ast.Name(
                                        id=f"get_{concept_name.lower()}", ctx=ast.Load()
                                    ),
                                    args=[],
                                    keywords=[],
                                ),
                                attr="id",
                                ctx=ast.Load(),
                            )
                        ],
                        keywords=[
                            ast.keyword(
                                arg="deserializer",
                                value=ast.Name(
                                    id=f"deserializer_{concept_name.lower()}",
                                    ctx=ast.Load(),
                                ),
                            )
                        ],
                    )
                )
            )

    register_func = ast.FunctionDef(
        name="register_deserializers",
        args=ast.arguments(
            posonlyargs=[],
            args=[
                ast.arg(
                    arg="serialization",
                    annotation=ast.Name(id="AbstractSerialization", ctx=ast.Load()),
                )
            ],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
        ),
        body=register_func_body,
        decorator_list=[],
        returns=None,
    )

    # Final module
    module = ast.Module(body=module_body + [register_func], type_ignores=[])

    generated_code = astor.to_source(module)
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)
    click.echo(f"📂 Saving deserializer to: {output}")
    with Path(f"{output}/deserializer.py").open("w", encoding="utf-8") as f:
        f.write(generated_code)
