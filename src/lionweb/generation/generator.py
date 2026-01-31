from typing import cast

import click

from lionweb.generation.language_generation import language_generation
from lionweb.language import Language
from lionweb.lionweb_version import LionWebVersion
from lionweb.serialization import create_standard_json_serialization



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
@click.argument("output", type=click.Path(exists=False, file_okay=False, writable=True))
def main(dependencies, lionweb_version: LionWebVersion, lionweb_language, output):
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
    from lionweb.generation.node_classes_generation import \
        node_classes_generation

    """Simple CLI that processes a file and writes results to a directory."""
    serialization = create_standard_json_serialization(LionWebVersion.V2023_1)

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
    language_generation(click, language, output)
    node_classes_generation(click, language, output)
    deserializer_generation(click, language, output)


if __name__ == "__main__":
    main()
