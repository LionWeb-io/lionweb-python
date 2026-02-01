"""
CLI tool for generating Python code from LionWeb language definitions.

This module provides a command-line interface for processing LionWeb language files
and generating corresponding Python classes, including language definitions, node classes,
and deserializers.
"""

from pathlib import Path
from typing import List, cast

import click

from lionweb.generation.configuration import PrimitiveTypeMappingSpec
from lionweb.generation.language_generation import (LanguageGenerator,
                                                    LanguageMappingSpec)
from lionweb.generation.node_classes_generation import NodeClassesGenerator
from lionweb.language import Language
from lionweb.lionweb_version import LionWebVersion
from lionweb.serialization import create_standard_json_serialization


class LanguageMappingSpecMappingType(click.ParamType):
    """
    Click parameter type for parsing language mapping specifications.

    Accepts string input in the format "LANG=PACKAGE" where LANG is either a
    LionWeb language name or ID, and PACKAGE is the Python package path.

    Example: "MyLionWebLanguageName=myapp.lang.foo"
    """

    name = "LANG=PACKAGE"

    def convert(self, value, param, ctx) -> LanguageMappingSpec:
        # Accept forms like:
        #   "MyLionWebLanguageName=myapp.lang.foo"
        #   "my_lionweb_language_id=myapp.lang.foo"
        if not isinstance(value, str):
            self.fail("Expected a string.", param, ctx)

        if "=" not in value:
            self.fail(
                "Expected format LANG=PACKAGE (e.g. 'en=myapp.lang.en').",
                param,
                ctx,
            )

        lang, package = (part.strip() for part in value.split("=", 1))
        if not lang:
            self.fail("LANG part cannot be empty.", param, ctx)
        if not package:
            self.fail("PACKAGE part cannot be empty.", param, ctx)

        return LanguageMappingSpec(lang=lang, package=package)


class PrimitiveTypeMappingSpecMappingType(click.ParamType):
    """
    Click parameter type for parsing primitive type mapping specifications.

    Accepts string input in the format "PRIMITIVE_TYPE=QUALIFIED_NAME" where
    PRIMITIVE_TYPE is a LionWeb primitive type name or ID, and QUALIFIED_NAME
    is the fully qualified Python type name.

    Example: "date=myapp.foo.Date"
    """

    name = "PRIMITIVE_TYPE=QUALIFIED_NAME"

    def convert(self, value, param, ctx) -> PrimitiveTypeMappingSpec:
        if not isinstance(value, str):
            self.fail("Expected a string.", param, ctx)

        if "=" not in value:
            self.fail(
                "Expected format PRIMITIVE_TYPE=QUALIFIED_NAME (e.g. 'date=myapp.foo.Date').",
                param,
                ctx,
            )

        primitive_type, qualified_name = (part.strip() for part in value.split("=", 1))
        if not primitive_type:
            self.fail("PRIMITIVE_TYPE part cannot be empty.", param, ctx)
        if not qualified_name:
            self.fail("QUALIFIED_NAME part cannot be empty.", param, ctx)

        return PrimitiveTypeMappingSpec(
            primitive_type=primitive_type, qualified_name=qualified_name
        )


LANG_MAPPING = LanguageMappingSpecMappingType()
PRIMITIVE_TYPE_MAPPING = PrimitiveTypeMappingSpecMappingType()


@click.command()
@click.option(
    "-d",
    "--dependencies",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    help="Path to a LionWeb language files necessary to use as dependencies to open the target languages. "
    "Can be specified multiple times.",
    multiple=True,
)
@click.option(
    "--lionweb-version",
    "--lwv",
    default=LionWebVersion.V2023_1,
    help="LionWeb version to use for processing. Defaults to 2023.1.",
    type=LionWebVersion,
    multiple=False,
)
@click.argument(
    "lionweb-language",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    help="Path to the LionWeb language file that needs processing. Must be a readable file and exists.",
)
@click.option(
    "--language-packages",
    "--lp",
    "language_packages",
    type=LANG_MAPPING,
    multiple=True,
    metavar="LANG=PACKAGE",
    help="Map a language ID or name to the Python package that provides it. Repeatable.",
)
@click.option(
    "--primitive-types",
    "--pt",
    "primitive_types",
    type=PRIMITIVE_TYPE_MAPPING,
    multiple=True,
    metavar="PRIMITIVE_TYPE=QUALIFIED_NAME",
    help="Map a primitive type ID or name to the Python type that provides it. Repeatable.",
)
@click.argument("output", type=click.Path(exists=False, file_okay=False, writable=True))
def main(
    dependencies: List[Path],
    lionweb_version: LionWebVersion,
    lionweb_language: Path,
    language_packages: tuple[LanguageMappingSpec, ...],
    primitive_types: tuple[PrimitiveTypeMappingSpec, ...],
    output,
):
    """
    Process LionWeb language files and generate corresponding Python classes.

    This CLI command reads a LionWeb language definition file and generates Python code
    including language definitions, node classes, and deserializers. Dependency files can
    be provided to register additional languages before processing the main language file.

    Args:
        dependencies: List of paths to dependency LionWeb language files. Each file is
            processed and registered before the main language file.
        lionweb_version: The LionWeb version to use for deserialization (defaults to 2023.1).
        lionweb_language: Path to the main LionWeb language file to process.
        language_packages: Tuple of language mapping specifications that map language IDs or names
            to Python package paths (e.g., "MyLanguage=myapp.lang.mylang").
        primitive_types: Tuple of primitive type mapping specifications that map primitive type
            IDs or names to Python type paths (e.g., "date=myapp.types.Date").
        output: Path to the output directory where generated Python files will be written.

    Raises:
        IOError: If there is an issue reading the provided files or writing results to the
            output directory.
        Exception: For any internal error encountered during processing.

    Examples:
        $ python -m lionweb.generation.generator -d deps.json input.json output/
        $ python -m lionweb.generation.generator --lp "MyLang=myapp.lang" input.json output/
    """
    from lionweb.generation.deserializer_generation import \
        deserializer_generation

    serialization = create_standard_json_serialization(lionweb_version)

    for dep in dependencies:
        click.echo(f"Processing dependency {dep}")
        with open(file=dep, mode="r", encoding="utf-8") as f:
            content = f.read()
            language = cast(
                Language, serialization.deserialize_string_to_nodes(content)[0]
            )
            serialization.register_language(language=language)
            serialization.classifier_resolver.register_language(language)
            serialization.instance_resolver.add_tree(language)

    click.echo(f"📄 Processing file: {lionweb_language}")
    with open(lionweb_language, "r", encoding="utf-8") as f:
        content = f.read()
        language = cast(Language, serialization.deserialize_string_to_nodes(content)[0])
    LanguageGenerator(language_packages, primitive_types).language_generation(
        click, language, output
    )
    NodeClassesGenerator(language_packages, primitive_types).node_classes_generation(
        click, language, output
    )
    deserializer_generation(click, language, output)


if __name__ == "__main__":
    main()
