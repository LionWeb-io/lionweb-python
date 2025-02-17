import json
import unittest

from serialization.my_node_with_properties import MyNodeWithProperties
from serialization.my_node_with_properties2023 import MyNodeWithProperties2023
from serialization.serialization_test import SerializationTest

from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.serialization.json_utils import JsonArray
from lionwebpython.serialization.serialization_provider import \
    SerializationProvider
from lionwebpython.serialization.serialized_json_comparison_utils import \
    SerializedJsonComparisonUtils


class TestSerializationOfPrimitiveValues(SerializationTest):

    def test_serialize_boolean(self):
        node = MyNodeWithProperties("n1")
        node.set_p1(True)

        expected = json.loads(
            """{
          "serializationFormatVersion": "2024.1",
          "languages": [
              {"key": "mylanguage", "version":"1"},
              {"key": "LionCore-builtins", "version":"2024.1"}
           ],
          "nodes": [
            {
              "id": "n1",
              "classifier": {
                "language": "mylanguage",
                "version": "1",
                "key": "concept-MyNodeWithProperties"
              },
              "properties": [
                {"property": {"language": "mylanguage", "version": "1", "key": "p1"}, "value": "true"}
              ],
              "containments": [], "references": [], "annotations": [], "parent": null
            }
          ]
        }"""
        )

        json_serialization = SerializationProvider.get_standard_json_serialization()
        serialized = json_serialization.serialize_nodes_to_json_element([node])
        SerializedJsonComparisonUtils.assert_equivalent_lionweb_json(
            expected, serialized
        )

    def test_deserialize_boolean(self):
        node = MyNodeWithProperties("n1")
        node.set_p1(True)

        serialized = json.loads(
            """{
          "serializationFormatVersion": "2024.1",
          "languages": [],
          "nodes": [
            {
              "id": "n1",
              "classifier": {
                "language": "mylanguage",
                "version": "1",
                "key": "concept-MyNodeWithProperties"
              },
              "properties": [
                {"property": {"language": "mylanguage", "version": "1", "key": "p1"}, "value": "true"},
                {"property": {"language": "mylanguage", "version": "1", "key": "p2"}, "value": null},
                {"property": {"language": "mylanguage", "version": "1", "key": "p3"}, "value": null}
              ],
              "containments": [], "references": [], "annotations": [], "parent": null
            }
          ]
        }"""
        )

        json_serialization = SerializationProvider.get_standard_json_serialization()
        json_serialization.classifier_resolver.register_language(
            MyNodeWithProperties.LANGUAGE
        )
        json_serialization.instantiator.register_custom_deserializer(
            MyNodeWithProperties.CONCEPT.get_id(),
            lambda concept, serialized_node, deserialized_nodes_by_id, properties_value: MyNodeWithProperties(
                serialized_node.get_id()
            ),
        )
        deserialized = json_serialization.deserialize_json_to_nodes(serialized)
        self.assertEqual([node], deserialized)

    def test_serialize_string(self):
        node = MyNodeWithProperties("n1")
        node.set_p3("qwerty")

        expected = json.loads(
            """{
          "serializationFormatVersion": "2024.1",
          "languages": [
              {"key": "mylanguage", "version":"1"},
              {"key": "LionCore-builtins", "version":"2024.1"}
          ],
          "nodes": [
            {
              "id": "n1",
              "classifier": {
                "language": "mylanguage",
                "version": "1",
                "key": "concept-MyNodeWithProperties"
              },
              "properties": [
                {"property": {"language": "mylanguage", "version": "1", "key": "p3"}, "value": "qwerty"}
              ],
              "containments": [], "references": [], "annotations": [], "parent": null
            }
          ]
        }"""
        )

        json_serialization = SerializationProvider.get_standard_json_serialization()
        serialized = json_serialization.serialize_nodes_to_json_element(node)
        SerializedJsonComparisonUtils.assert_equivalent_lionweb_json(
            expected, serialized
        )

    def test_deserialize_string(self):
        node = MyNodeWithProperties("n1")
        node.set_p3("qwerty")

        serialized = json.loads(
            """{
          "serializationFormatVersion": "2024.1",
          "languages": [],
          "nodes": [
            {
              "id": "n1",
              "classifier": {
                "language": "mylanguage",
                "version": "1",
                "key": "concept-MyNodeWithProperties"
              },
              "properties": [
                {"property": {"language": "mylanguage", "version": "1", "key": "p3"}, "value": "qwerty"}
              ],
              "containments": [], "references": [], "annotations": [], "parent": null
            }
          ]
        }"""
        )

        json_serialization = SerializationProvider.get_standard_json_serialization()
        json_serialization.classifier_resolver.register_language(
            MyNodeWithProperties.LANGUAGE
        )
        json_serialization.instantiator.register_custom_deserializer(
            MyNodeWithProperties.CONCEPT.get_id(),
            lambda concept, serialized_node, deserialized_nodes_by_id, properties_value: MyNodeWithProperties(
                serialized_node.get_id()
            ),
        )
        deserialized = json_serialization.deserialize_json_to_nodes(serialized)
        self.assertEqual([node], deserialized)

    def test_serialize_integer(self):
        node = MyNodeWithProperties("n1")
        node.set_p2(2904)

        expected = json.loads(
            """{
            "serializationFormatVersion": "2024.1",
            "languages": [
                {"key": "mylanguage", "version": "1"},
                {"key": "LionCore-builtins", "version": "2024.1"}
            ],
            "nodes": [
                {
                    "id": "n1",
                    "classifier": {
                        "language": "mylanguage",
                        "version": "1",
                        "key": "concept-MyNodeWithProperties"
                    },
                    "properties": [
                        {"property": {"language": "mylanguage", "version": "1", "key": "p2"}, "value": "2904"}
                    ],
                    "containments": [], "references": [], "annotations": [], "parent": null
                }
            ]
        }"""
        )

        json_serialization = SerializationProvider.get_standard_json_serialization()
        serialized = json_serialization.serialize_nodes_to_json_element(node)
        SerializedJsonComparisonUtils.assert_equivalent_lionweb_json(
            expected, serialized
        )

    def test_deserialize_integer(self):
        node = MyNodeWithProperties("n1")
        node.set_p1(False)
        node.set_p2(2904)
        serialized = """{
            "serializationFormatVersion": "2024.1",
            "languages": [],
            "nodes": [
                {
                    "id": "n1",
                    "classifier": {
                        "language": "mylanguage",
                        "version": "1",
                        "key": "concept-MyNodeWithProperties"
                    },
                    "properties": [
                        {"property": {"language": "mylanguage", "version": "1", "key": "p1"}, "value": "false"},
                        {"property": {"language": "mylanguage", "version": "1", "key": "p2"}, "value": "2904"},
                        {"property": {"language": "mylanguage", "version": "1", "key": "p3"}, "value": null}
                    ],
                    "containments": [],
                    "references": [],
                    "annotations": [],
                    "parent": null
                }
            ]
        }"""

        json_serialization = SerializationProvider.get_standard_json_serialization()
        json_serialization.classifier_resolver.register_language(
            MyNodeWithProperties.LANGUAGE
        )

        def custom_deserializer(
            concept, serialized_node, deserialized_nodes_by_id, properties_value
        ):
            return MyNodeWithProperties(serialized_node.get_id())

        json_serialization.instantiator.register_custom_deserializer(
            MyNodeWithProperties.CONCEPT.get_id(), custom_deserializer
        )

        deserialized = json_serialization.deserialize_json_to_nodes(
            json.loads(serialized)
        )
        self.assertEqual(deserialized, [node])

    def test_serialize_json(self):
        node = MyNodeWithProperties2023("n1")
        node.set_p4([1, "foo"])

        expected = json.loads(
            """{
            "serializationFormatVersion": "2023.1",
            "languages": [
                {"key": "mylanguage", "version": "1"},
                {"key": "LionCore-builtins", "version": "2023.1"}
            ],
            "nodes": [
                {
                    "id": "n1",
                    "classifier": {
                        "language": "mylanguage",
                        "version": "1",
                        "key": "concept-MyNodeWithProperties"
                    },
                    "properties": [
                        {"property": {"language": "mylanguage", "version": "1", "key": "p4"}, "value": "[1, \\\"foo\\\"]"}
                    ],
                    "containments": [],
                    "references": [],
                    "annotations": [],
                    "parent": null
                }
            ]
        }"""
        )

        json_serialization = SerializationProvider.get_standard_json_serialization(
            LionWebVersion.V2023_1
        )
        serialized = json_serialization.serialize_nodes_to_json_element(node)
        SerializedJsonComparisonUtils.assert_equivalent_lionweb_json(
            expected, serialized
        )

    def test_deserialize_json(self):
        node = MyNodeWithProperties2023("n1")
        ja: JsonArray = []
        ja.append(1)
        ja.append("foo")
        assert node.get_p1() is None
        node.set_p4(ja)
        serialized = json.loads(
            """{
            "serializationFormatVersion": "2023.1",
            "languages": [],
            "nodes": [
                {
                    "id": "n1",
                    "classifier": {
                        "language": "mylanguage",
                        "version": "1",
                        "key": "concept-MyNodeWithProperties"
                    },
                    "properties": [
                        {"property": {"language": "mylanguage", "version": "1", "key": "p1"}, "value": null},
                        {"property": {"language": "mylanguage", "version": "1", "key": "p2"}, "value": null},
                        {"property": {"language": "mylanguage", "version": "1", "key": "p3"}, "value": null},
                        {"property": {"language": "mylanguage", "version": "1", "key": "p4"}, "value": "[1, \\\"foo\\\"]"}
                    ],
                    "containments": [],
                    "references": [],
                    "annotations": [],
                    "parent": null
                }
            ]
        }"""
        )
        json_serialization = SerializationProvider.get_standard_json_serialization(
            LionWebVersion.V2023_1
        )

        json_serialization.classifier_resolver.register_language(
            MyNodeWithProperties2023.LANGUAGE
        )

        def custom_deserializer(
            concept, serialized_node, deserialized_nodes_by_id, properties_value
        ):
            return MyNodeWithProperties2023(serialized_node.get_id())

        json_serialization.instantiator.register_custom_deserializer(
            MyNodeWithProperties2023.CONCEPT.get_id(), custom_deserializer
        )

        deserialized = json_serialization.deserialize_json_to_nodes(serialized)
        assert deserialized == [node]


if __name__ == "__main__":
    unittest.main()
