import json
import unittest

from lionwebpython.language import Language, Annotation, Concept
from lionwebpython.model.impl.dynamic_annotation_instance import DynamicAnnotationInstance
from lionwebpython.model.impl.dynamic_node import DynamicNode
from lionwebpython.serialization.data.metapointer import MetaPointer
from lionwebpython.serialization.json_serialization import JsonSerialization
from lionwebpython.serialization.low_level_json_serialization import LowLevelJsonSerialization


class LowLevelJsonSerializationTest(unittest.TestCase):

    def test_deserialize_lioncore_to_serialized_nodes(self):
        with open("./resources/serialization/lioncore.json", "r") as file:
            json_element = json.load(file)

        json_serialization = LowLevelJsonSerialization()
        serialized_chunk = json_serialization.deserialize_serialization_block(json_element)
        deserialized_instances = serialized_chunk.get_classifier_instances()

        lioncore = deserialized_instances[0]
        self.assertEqual(MetaPointer("LionCore-M3", "2023.1", "Language"), lioncore.classifier)
        self.assertEqual("-id-LionCore-M3", lioncore.id)
        self.assertEqual("LionCore_M3", lioncore.get_property_value("LionCore-builtins-INamed-name"))
        self.assertEqual(16, len(lioncore.children))
        self.assertIsNone(lioncore.parent_node_id)

    def test_deserialize_library_language_to_serialized_nodes(self):
        with open("./resources/serialization/library-language.json", "r") as file:
            json_element = json.load(file)

        json_serialization = LowLevelJsonSerialization()
        serialized_chunk = json_serialization.deserialize_serialization_block(json_element)
        book = serialized_chunk.get_instance_by_id("library-Book")
        self.assertEqual("Book", book.get_property_value("LionCore-builtins-INamed-name"))

        guided_book_writer = serialized_chunk.get_instance_by_id("library-GuideBookWriter")
        self.assertEqual("GuideBookWriter", guided_book_writer.get_property_value("LionCore-builtins-INamed-name"))
        self.assertEqual([{"reference": "library-Writer", "info": "Writer"}], guided_book_writer.get_reference_values("Concept-extends"))
        self.assertEqual(["library-GuideBookWriter-countries"], guided_book_writer.get_containment_values("Concept-features"))

    def test_reserialize_library_language(self):
        self.assert_file_is_reserialized_correctly("./resources/serialization/library-language.json")

    def test_reserialize_bobs_library(self):
        self.assert_file_is_reserialized_correctly("./resources/serialization/bobslibrary.json")

    def test_reserialize_language_engineering_library(self):
        self.assert_file_is_reserialized_correctly("./resources/serialization/langeng-library.json")

    def test_serialize_annotations(self):
        l = Language("l", "l", "l", "1")
        a1 = Annotation(l, "a1", "a1", "a1")
        a2 = Annotation(l, "a2", "a2", "a2")
        c = Concept(l, "c", "c", "c")

        n1 = DynamicNode("n1", c)
        a1_1 = DynamicAnnotationInstance("a1_1", a1, n1)
        a1_2 = DynamicAnnotationInstance("a1_2", a1, n1)
        a2_3 = DynamicAnnotationInstance("a2_3", a2, n1)

        hjs = JsonSerialization()
        hjs.enable_dynamic_nodes()

        je = hjs.serialize_nodes_to_json_element(n1)
        deserialized_nodes = hjs.deserialize_to_nodes(je)
        self.assertEqual(1, len(deserialized_nodes))
        self.assert_instances_are_equal(n1, deserialized_nodes[0])

    def test_unexpected_property(self):
        json_str = '''{
          "serializationFormatVersion": "1",
          "languages": [],
          "nodes": [],
          "info": "should not be here"
        }'''
        lljs = LowLevelJsonSerialization()
        with self.assertRaises(Exception):
            lljs.deserialize_serialization_block(json.loads(json_str))

    def assert_file_is_reserialized_correctly(self, file_path: str):
        with open(file_path, "r") as file:
            json_element = json.load(file)

        json_serialization = LowLevelJsonSerialization()
        serialized_chunk = json_serialization.deserialize_serialization_block(json_element)
        reserialized = json_serialization.serialize_to_json_element(serialized_chunk)

        self.assertEqual(json_element, reserialized)

if __name__ == '__main__':
    unittest.main()
