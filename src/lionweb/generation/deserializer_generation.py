import ast
from _ast import stmt
from pathlib import Path
from typing import List, cast

import astor  # type: ignore

from lionweb.generation.ASTBuilder import ASTBuilder
from lionweb.generation.base_generator import BaseGenerator
from lionweb.generation.configuration import (LanguageMappingSpec,
                                              PrimitiveTypeMappingSpec)
from lionweb.generation.generation_utils import make_function_def
from lionweb.generation.naming_utils import getter_name
from lionweb.language import Concept, Language


class DeserializerGenerator(BaseGenerator, ASTBuilder):

    def __init__(
        self,
        language_packages: tuple[LanguageMappingSpec, ...],
        primitive_types: tuple[PrimitiveTypeMappingSpec, ...],
    ):
        super().__init__(language_packages, primitive_types)

    def deserializer_generation(self, click, language: Language, output):
        module_body = []

        # Import statements
        concepts = [e for e in language.get_elements() if isinstance(e, Concept)]
        if len(concepts) > 0:
            module_body.append(
                ast.ImportFrom(
                    module=".language",
                    names=[
                        ast.alias(name=getter_name(c.name), asname=None)
                        for c in concepts
                    ],
                    level=0,
                )
            )
            for c in concepts:
                module_body.append(
                    ast.ImportFrom(
                        module=f".{self._get_safe_filename(c)[:-3]}",
                        names=[ast.alias(name=cast(str, c.get_name()), asname=None)],
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
                    make_function_def(
                        name=f"deserializer_{concept_name.lower()}",
                        args=ast.arguments(
                            posonlyargs=[],
                            args=[
                                ast.arg(arg="classifier"),
                                ast.arg(
                                    arg="serialized_instance",
                                    annotation=ast.Name(
                                        id="SerializedClassifierInstance",
                                        ctx=ast.Load(),
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
                                            id=getter_name(concept_name), ctx=ast.Load()
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

        if len(register_func_body) == 0:
            register_func_body.append(ast.Pass())
        register_func = make_function_def(
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
