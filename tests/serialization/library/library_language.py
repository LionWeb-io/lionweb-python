import json
import os

from lionwebpython.language import Concept
from lionwebpython.language.language import Language
from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.serialization.serialization_provider import \
    SerializationProvider


class LibraryLanguage:
    LIBRARY_MM: Language
    LIBRARY: "Concept"
    BOOK: "Concept"
    WRITER: "Concept"
    GUIDE_BOOK_WRITER: "Concept"

    @staticmethod
    def initialize():
        file_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "resources",
            "serialization",
            "library-language.json",
        )
        with open(file_path, "r") as file:
            json_element = json.load(file)

        json_serialization = SerializationProvider.get_standard_json_serialization(
            LionWebVersion.V2023_1
        )
        deserialized_nodes = json_serialization.deserialize_json_to_nodes(json_element)

        LibraryLanguage.LIBRARY_MM = next(
            (node for node in deserialized_nodes if isinstance(node, Language)), None
        )
        LibraryLanguage.LIBRARY = LibraryLanguage.LIBRARY_MM.get_concept_by_name(
            "Library"
        )
        LibraryLanguage.BOOK = LibraryLanguage.LIBRARY_MM.get_concept_by_name("Book")
        LibraryLanguage.WRITER = LibraryLanguage.LIBRARY_MM.get_concept_by_name(
            "Writer"
        )
        LibraryLanguage.GUIDE_BOOK_WRITER = (
            LibraryLanguage.LIBRARY_MM.get_concept_by_name("GuideBookWriter")
        )

        for feature in LibraryLanguage.LIBRARY.all_features():
            if feature.get_key() is None:
                raise ValueError(
                    f"Feature {feature} in {feature.container} should not have a null key"
                )


# Initialize at import time
LibraryLanguage.initialize()
