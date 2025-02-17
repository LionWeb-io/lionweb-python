import json
import unittest
from pathlib import Path

from serialization.library.book import Book
from serialization.library.library import Library
from serialization.library.writer import Writer
from serialization.serialization_test import SerializationTest

from lionwebpython.language import Concept, Property
from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.model.classifier_instance_utils import \
    ClassifierInstanceUtils
from lionwebpython.model.node import Node
from lionwebpython.serialization.serialization_provider import \
    SerializationProvider
from lionwebpython.serialization.serialized_json_comparison_utils import \
    SerializedJsonComparisonUtils


class SerializationOfLibraryTest(SerializationTest):

    def test_deserialize_library_to_concrete_classes(self):
        with open(
            Path(__file__).parent.parent
            / "resources"
            / "serialization"
            / "library-language.json",
            "r",
        ) as f:
            json_element = json.load(f)
        json_serialization = SerializationProvider.get_standard_json_serialization(
            LionWebVersion.V2023_1
        )
        deserialized_nodes = json_serialization.deserialize_json_to_nodes(json_element)

        library: Concept = self.concept_by_id(deserialized_nodes, "library-Library")
        library_name: Property = library.get_property_by_name("name")
        self.assertIsNotNone(library_name.get_key())

        book: Node = next(
            node for node in deserialized_nodes if node.get_id() == "library-Book"
        )
        self.assertEqual(
            "Book", ClassifierInstanceUtils.get_property_value_by_name(book, "name")
        )
        self.assertEqual(
            "library-Book",
            ClassifierInstanceUtils.get_property_value_by_name(book, "key"),
        )

        guided_book_writer: Concept = next(
            node
            for node in deserialized_nodes
            if node.get_id() == "library-GuideBookWriter"
        )
        self.assertEqual(
            "GuideBookWriter",
            ClassifierInstanceUtils.get_property_value_by_name(
                guided_book_writer, "name"
            ),
        )
        self.assertIsNotNone(guided_book_writer.get_extended_concept())

    def test_reserialize_library(self):
        input_path = (
            Path(__file__).parent.parent
            / "resources"
            / "serialization"
            / "library-language.json"
        )
        with input_path.open("r") as file:
            json_element = json.load(file)

        json_serialization = SerializationProvider.get_standard_json_serialization(
            LionWebVersion.V2023_1
        )
        deserialized_nodes = json_serialization.deserialize_json_to_nodes(json_element)
        reserialized = json_serialization.serialize_tree_to_json_element(
            deserialized_nodes[0]
        )

        SerializedJsonComparisonUtils.assert_equivalent_lionweb_json(
            json_element, reserialized
        )

    def test_serialize_library_instance(self):
        library = Library("lib-1", "Language Engineering Library")
        mv = Writer("mv", "Markus Völter")
        mb = Writer("mb", "Meinte Boersma")
        de = Book("de", "DSL Engineering", mv)
        de.set_pages(558)
        bfd = Book("bfd", "Business-Friendly DSLs", mb)
        bfd.set_pages(517)
        library.add_book(de)
        library.add_book(bfd)

        # The library MM is not using the standard primitive types but its own, so we need to specify
        # how to serialize those values
        json_serialization = SerializationProvider.get_standard_json_serialization(
            LionWebVersion.V2023_1
        )

        # Register serializers for custom primitive types
        json_serialization.primitive_values_serialization.register_serializer(
            "INhBvWyXvxwNsePuX0rdNGB_J9hi85cTb1Q0APXCyJ0", lambda value: value
        )
        json_serialization.primitive_values_serialization.register_serializer(
            "gVp8_QSmXE2k4pd-sQZgjYMoW95SLLaVIH4yMYqqbt4", lambda value: str(value)
        )

        # Serialize the library instance to JSON
        json_serialized = json_serialization.serialize_tree_to_json_element(library)

        # Read the expected JSON from the file
        with open(
            Path(__file__).parent.parent
            / "resources"
            / "serialization"
            / "langeng-library.json",
            "r",
        ) as file:
            json_read = json.load(file)

        SerializedJsonComparisonUtils.assert_equivalent_lionweb_json(
            json_read, json_serialized
        )

    def test_deserialize_language_with_duplicate_ids(self):
        with open(
            Path(__file__).parent.parent
            / "resources"
            / "serialization"
            / "library-language-with-duplicate.json",
            "r",
        ) as f:
            data = json.load(f)
        json_serialization = SerializationProvider.get_standard_json_serialization(
            LionWebVersion.V2023_1
        )
        with self.assertRaises(Exception):
            json_serialization.deserialize_json_to_nodes(data)


if __name__ == "__main__":
    unittest.main()
