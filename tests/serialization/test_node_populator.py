import json
import unittest

from lionwebpython.language.lioncore_builtins import LionCoreBuiltins
from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.model.classifier_instance_utils import \
    ClassifierInstanceUtils
from lionwebpython.model.impl.dynamic_node import DynamicNode
from lionwebpython.self.lioncore import LionCore
from lionwebpython.serialization.deserialization_exception import \
    DeserializationException
from lionwebpython.serialization.deserialization_status import \
    DeserializationStatus
from lionwebpython.serialization.low_level_json_serialization import \
    LowLevelJsonSerialization
from lionwebpython.serialization.node_populator import NodePopulator
from lionwebpython.serialization.serialization_provider import \
    SerializationProvider


class NodePopulatorTest(unittest.TestCase):

    def test_populate_reference_to_builtins_value_with_correct_id(self):
        serialization = SerializationProvider.get_standard_json_serialization(
            LionWebVersion.V2024_1
        )
        deserialization_status = DeserializationStatus(
            [], serialization.instance_resolver
        )
        node_populator = NodePopulator(
            serialization, serialization.instance_resolver, deserialization_status
        )

        chunk = LowLevelJsonSerialization().deserialize_serialization_block(
            json.loads(
                """{
          "serializationFormatVersion": "2024.1",
          "languages": [],
          "nodes": [
            {
              "id": "my-node",
              "classifier": {
                "language": "LionCore-M3",
                "version": "2024.1",
                "key": "Property"
              },
              "properties": [],
              "containments": [],
              "references": [
                {
                  "reference": {
                    "language": "LionCore-M3",
                    "version": "2024.1",
                    "key": "Property-type"
                  },
                  "targets": [
                    {
                      "resolveInfo": "LionWeb.LionCore_builtins.Boolean",
                      "reference": "LionCore-builtins-Boolean-2024-1"
                    }
                  ]
                }
              ],
              "parent": "io-lionweb-Properties-BooleanValue"
            }
          ]
        }"""
            )
        )

        serialized_node = chunk.get_classifier_instances()[0]
        node = DynamicNode("my-node", LionCore.get_property())
        node_populator.populate_classifier_instance(node, serialized_node)

        self.assertEqual(
            LionCoreBuiltins.get_boolean(),
            ClassifierInstanceUtils.get_only_reference_value_by_reference_name(
                node, "type"
            ).get_referred(),
        )

    def test_populate_reference_to_builtins_value_with_incorrect_id(self):
        serialization = SerializationProvider.get_standard_json_serialization(
            LionWebVersion.V2024_1
        )
        deserialization_status = DeserializationStatus(
            [], serialization.instance_resolver
        )
        node_populator = NodePopulator(
            serialization, serialization.instance_resolver, deserialization_status
        )

        chunk = LowLevelJsonSerialization().deserialize_serialization_block(
            json.loads(
                """{
          "serializationFormatVersion": "2024.1",
          "languages": [],
          "nodes": [
            {
              "id": "my-node",
              "classifier": {
                "language": "LionCore-M3",
                "version": "2024.1",
                "key": "Property"
              },
              "properties": [],
              "containments": [],
              "references": [
                {
                  "reference": {
                    "language": "LionCore-M3",
                    "version": "2024.1",
                    "key": "Property-type"
                  },
                  "targets": [
                    {
                      "resolveInfo": "LionWeb.LionCore_builtins.Boolean",
                      "reference": "invalid-id"
                    }
                  ]
                }
              ],
              "parent": "io-lionweb-Properties-BooleanValue"
            }
          ]
        }"""
            )
        )

        serialized_node = chunk.get_classifier_instances()[0]
        with self.assertRaises(DeserializationException):
            node = DynamicNode("my-node", LionCore.get_property())
            node_populator.populate_classifier_instance(node, serialized_node)

    def test_populate_reference_to_builtins_value_with_no_id(self):
        serialization = SerializationProvider.get_standard_json_serialization(
            LionWebVersion.V2024_1
        )
        deserialization_status = DeserializationStatus(
            [], serialization.instance_resolver
        )
        node_populator = NodePopulator(
            serialization, serialization.instance_resolver, deserialization_status
        )

        chunk = LowLevelJsonSerialization().deserialize_serialization_block(
            json.loads(
                """{
          "serializationFormatVersion": "2024.1",
          "languages": [],
          "nodes": [
            {
              "id": "my-node",
              "classifier": {
                "language": "LionCore-M3",
                "version": "2024.1",
                "key": "Property"
              },
              "properties": [],
              "containments": [],
              "references": [
                {
                  "reference": {
                    "language": "LionCore-M3",
                    "version": "2024.1",
                    "key": "Property-type"
                  },
                  "targets": [
                    {
                      "resolveInfo": "LionWeb.LionCore_builtins.Boolean",
                      "reference": null
                    }
                  ]
                }
              ],
              "parent": "io-lionweb-Properties-BooleanValue"
            }
          ]
        }"""
            )
        )

        serialized_node = chunk.get_classifier_instances()[0]
        node = DynamicNode("my-node", LionCore.get_property())
        node_populator.populate_classifier_instance(node, serialized_node)

        self.assertEqual(
            LionCoreBuiltins.get_boolean(),
            ClassifierInstanceUtils.get_only_reference_value_by_reference_name(
                node, "type"
            ).get_referred(),
        )


if __name__ == "__main__":
    unittest.main()
