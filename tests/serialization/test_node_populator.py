import json
import unittest

from lionweb.language.lioncore_builtins import LionCoreBuiltins
from lionweb.lionweb_version import LionWebVersion
from lionweb.model.classifier_instance_utils import \
    get_only_reference_value_by_reference_name
from lionweb.model.impl.dynamic_node import DynamicNode
from lionweb.self.lioncore import LionCore
from lionweb.serialization.deserialization_exception import \
    DeserializationException
from lionweb.serialization.deserialization_status import DeserializationStatus
from lionweb.serialization.low_level_json_serialization import \
    LowLevelJsonSerialization
from lionweb.serialization.node_populator import NodePopulator
from lionweb.serialization.serialization_provider import SerializationProvider


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
            get_only_reference_value_by_reference_name(node, "type").get_referred(),
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
            get_only_reference_value_by_reference_name(node, "type").get_referred(),
        )


if __name__ == "__main__":
    unittest.main()
