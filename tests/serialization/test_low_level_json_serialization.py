import json
import unittest
from pathlib import Path
from typing import Union

from serialization.serialization_test import SerializationTest

from lionwebpython.language import Annotation, Concept, Language
from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.model.impl.dynamic_annotation_instance import \
    DynamicAnnotationInstance
from lionwebpython.model.impl.dynamic_node import DynamicNode
from lionwebpython.self.lioncore import LionCore
from lionwebpython.serialization.data.metapointer import MetaPointer
from lionwebpython.serialization.data.serialized_reference_value import \
    SerializedReferenceValueEntry
from lionwebpython.serialization.json_serialization import JsonSerialization
from lionwebpython.serialization.low_level_json_serialization import \
    LowLevelJsonSerialization
from lionwebpython.serialization.serialized_json_comparison_utils import \
    SerializedJsonComparisonUtils


class LowLevelJsonSerializationTest(SerializationTest):

    def test_deserialize_lioncore_to_serialized_nodes(self):
        with open(
            Path(__file__).parent.parent
            / "resources"
            / "serialization"
            / "lioncore.json",
            "r",
        ) as file:
            json_element = json.load(file)

        json_serialization = LowLevelJsonSerialization()
        serialized_chunk = json_serialization.deserialize_serialization_block(
            json_element
        )
        deserialized_instances = serialized_chunk.get_classifier_instances()

        lioncore = deserialized_instances[0]
        self.assertEqual(
            MetaPointer("LionCore-M3", "2023.1", "Language"), lioncore.classifier
        )
        self.assertEqual("-id-LionCore-M3", lioncore.id)
        self.assertEqual(
            "LionCore_M3",
            lioncore.get_property_value_by_key("LionCore-builtins-INamed-name"),
        )
        self.assertEqual(16, len(lioncore.get_children()))
        self.assertIsNone(lioncore.parent_node_id)

    def test_deserialize_library_language_to_serialized_nodes(self):
        with open(
            Path(__file__).parent.parent
            / "resources"
            / "serialization"
            / "library-language.json",
            "r",
        ) as file:
            json_element = json.load(file)

        json_serialization = LowLevelJsonSerialization()
        serialized_chunk = json_serialization.deserialize_serialization_block(
            json_element
        )
        book = serialized_chunk.get_instance_by_id("library-Book")
        self.assertEqual(
            "Book", book.get_property_value_by_key("LionCore-builtins-INamed-name")
        )

        guided_book_writer = serialized_chunk.get_instance_by_id(
            "library-GuideBookWriter"
        )
        self.assertEqual(
            "GuideBookWriter",
            guided_book_writer.get_property_value_by_key(
                "LionCore-builtins-INamed-name"
            ),
        )
        self.assertEqual(
            [
                SerializedReferenceValueEntry(
                    reference="library-Writer", resolve_info="Writer"
                )
            ],
            guided_book_writer.get_reference_values_by_key("Concept-extends"),
        )
        self.assertEqual(
            [
                SerializedReferenceValueEntry(
                    reference="library-Writer", resolve_info="Writer"
                )
            ],
            guided_book_writer.get_reference_values(
                MetaPointer.from_feature(
                    LionCore.get_concept(LionWebVersion.V2023_1).get_reference_by_name(
                        "extends"
                    )
                )
            ),
        )
        self.assertEqual(
            ["library-GuideBookWriter-countries"],
            guided_book_writer.get_containment_values(
                MetaPointer.from_feature(
                    LionCore.get_concept(
                        LionWebVersion.V2023_1
                    ).get_containment_by_name("features")
                )
            ),
        )

    def test_reserialize_library_language(self):
        self.maxDiff = None
        self.assert_file_is_reserialized_correctly(
            Path(__file__).parent.parent
            / "resources"
            / "serialization"
            / "library-language.json"
        )

    def test_reserialize_bobs_library(self):
        self.assert_file_is_reserialized_correctly(
            Path(__file__).parent.parent
            / "resources"
            / "serialization"
            / "bobslibrary.json"
        )

    def test_reserialize_language_engineering_library(self):
        self.assert_file_is_reserialized_correctly(
            Path(__file__).parent.parent
            / "resources"
            / "serialization"
            / "langeng-library.json"
        )

    def test_serialize_annotations(self):
        lang = Language("l", "l", "l", "1")
        a1 = Annotation(language=lang, name="a1", id="a1", key="a1")
        a2 = Annotation(language=lang, name="a2", id="a2", key="a2")
        c = Concept(language=lang, name="c", id="c", key="c")

        n1 = DynamicNode("n1", c)
        DynamicAnnotationInstance("a1_1", a1, n1)
        DynamicAnnotationInstance("a1_2", a1, n1)
        DynamicAnnotationInstance("a2_3", a2, n1)

        hjs = JsonSerialization()
        hjs.enable_dynamic_nodes()

        je = hjs.serialize_nodes_to_json_element([n1])
        deserialized_nodes = hjs.deserialize_json_to_nodes(je)
        self.assertEqual(1, len(deserialized_nodes))
        self.assert_instances_are_equal(n1, deserialized_nodes[0])

    def test_unexpected_property(self):
        json_str = """{
          "serializationFormatVersion": "1",
          "languages": [],
          "nodes": [],
          "info": "should not be here"
        }"""
        lljs = LowLevelJsonSerialization()
        with self.assertRaises(Exception):
            lljs.deserialize_serialization_block(json.loads(json_str))

    def assert_file_is_reserialized_correctly(self, file_path: Union[str, Path]):
        with open(file_path, "r") as file:
            json_element = json.load(file)

        json_serialization = LowLevelJsonSerialization()
        serialized_chunk = json_serialization.deserialize_serialization_block(
            json_element
        )
        reserialized = json_serialization.serialize_to_json_element(serialized_chunk)

        SerializedJsonComparisonUtils.assert_equivalent_lionweb_json(
            json_element, reserialized
        )


if __name__ == "__main__":
    unittest.main()
