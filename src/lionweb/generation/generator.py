from typing import cast

import click

from lionweb.generation.language_generation import language_generation
from lionweb.language import Language
from lionweb.lionweb_version import LionWebVersion
from lionweb.serialization.serialization_provider import SerializationProvider


@click.command()
@click.option(
    "-d",
    "--dependencies",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    multiple=True,
)
@click.argument(
    "lionweb-language", type=click.Path(exists=True, dir_okay=False, readable=True)
)
@click.argument("output", type=click.Path(exists=False, file_okay=False, writable=True))
def main(dependencies, lionweb_language, output):
    from lionweb.generation.deserializer_generation import \
        deserializer_generation
    from lionweb.generation.node_classes_generation import \
        node_classes_generation

    """Simple CLI that processes a file and writes results to a directory."""
    serialization = SerializationProvider.get_standard_json_serialization(
        LionWebVersion.V2023_1
    )

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
