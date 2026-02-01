from typing import cast

import click

from lionweb.generation.configuration import PrimitiveTypeMappingSpec
from lionweb.generation.language_generation import (LanguageGenerator,
                                                    LanguageMappingSpec)
from lionweb.generation.node_classes_generation import NodeClassesGenerator
from lionweb.language import Language
from lionweb.lionweb_version import LionWebVersion
from lionweb.serialization import create_standard_json_serialization


class LanguageMappingSpecMappingType(click.ParamType):
    name = "LANG=PACKAGE"

    def convert(self, value, param, ctx) -> LanguageMappingSpec:
        # Accept forms like:
        #   "en=myapp.lang.en"
        #   "English = myapp.lang.en"  (spaces trimmed)
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
    name = "PRIMITIVE_TYPE=QUALIFIED_NAME"

    def convert(self, value, param, ctx) -> PrimitiveTypeMappingSpec:
        # Accept forms like:
        #   "en=myapp.lang.en"
        #   "English = myapp.lang.en"  (spaces trimmed)
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
    "lionweb-language", type=click.Path(exists=True, dir_okay=False, readable=True)
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
    dependencies,
    lionweb_version: LionWebVersion,
    lionweb_language,
    language_packages: tuple[LanguageMappingSpec, ...],
    primitive_types: tuple[PrimitiveTypeMappingSpec, ...],
    output,
):
    """
    Simple CLI command for processing LionWeb language files and generate corresponding classes to a specified
    output directory. The CLI can also consider multiple dependency files for language registration prior to handling the main
    language file.

    Arguments:
        lionweb_language (Path): Path to the LionWeb language file that needs
            processing. Must be a readable file and exists.
        output (Path): Path to the output directory where the results will be
            written. Must not exist before execution.

    Options:
        -d, --dependencies (Path): Paths to dependency files. Each file must
            exist, be readable, and not a directory. Can be specified multiple
            times.

    Raises:
        IOError: If there is an issue reading the provided files or writing
            results to the output directory.
        Exception: For any internal error encountered during processing.

    """
    from lionweb.generation.deserializer_generation import \
        deserializer_generation

    """Simple CLI that processes a file and writes results to a directory."""
    serialization = create_standard_json_serialization(lionweb_version)

    for dep in dependencies:
        click.echo(f"Processing dependency {dep}")
        with open(dep, "r", encoding="utf-8") as f:
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
