import json
from pathlib import Path

from lionweb.lionweb_version import LionWebVersion
from lionweb.model import ClassifierInstance
from lionweb.model.node import Node
from lionweb.serialization.abstract_serialization import AbstractSerialization
from lionweb.serialization.low_level_json_serialization import (
    JsonElement,
    LowLevelJsonSerialization,
)


class JsonSerialization(AbstractSerialization):
    """LionWeb (de)serialization to/from the standard JSON wire format."""

    def __init__(self, lionweb_version: LionWebVersion = LionWebVersion.current_version()) -> None:
        super().__init__(lionweb_version=lionweb_version)

    def serialize_trees_to_json_element(self, roots: list[ClassifierInstance]) -> JsonElement:
        from lionweb.model.impl.proxy_node import ProxyNode

        nodes_ids: set[str] = set()
        all_nodes: list[ClassifierInstance] = []

        for root in roots:
            classifier_instances: list[ClassifierInstance] = list()
            ClassifierInstance.collect_self_and_descendants(root, True, classifier_instances)

            for node in classifier_instances:
                id = node.id
                if not id:
                    raise ValueError()
                # We support serialization of incorrect nodes, so we allow nodes without an ID
                if id is not None:
                    if id not in nodes_ids:
                        all_nodes.append(node)
                        nodes_ids.add(id)
                else:
                    all_nodes.append(node)

        # Filter out ProxyNode instances before serialization
        filtered_nodes = [node for node in all_nodes if not isinstance(node, ProxyNode)]
        return self.serialize_nodes_to_json_element(filtered_nodes)

    def serialize_nodes_to_json_element(
        self, classifier_instances: list[ClassifierInstance] | ClassifierInstance
    ) -> JsonElement:
        if isinstance(classifier_instances, ClassifierInstance):
            classifier_instances = [classifier_instances]
        serialization_block = self.serialize_nodes_to_serialization_chunk(classifier_instances)
        return LowLevelJsonSerialization().serialize_to_json_element(serialization_block)

    def serialize_tree_to_json_string(self, classifier_instance: ClassifierInstance) -> str:
        return json.dumps(self.serialize_tree_to_json_element(classifier_instance), indent=2)

    def serialize_trees_to_json_string(self, classifier_instances: list[ClassifierInstance]) -> str:
        return json.dumps(self.serialize_trees_to_json_element(classifier_instances), indent=2)

    def serialize_nodes_to_json_string(self, classifier_instances: list[ClassifierInstance]) -> str:
        return json.dumps(self.serialize_nodes_to_json_element(classifier_instances), indent=2)

    def serialize_tree_to_json_element(
        self, classifier_instance: ClassifierInstance
    ) -> JsonElement:
        from lionweb.model.impl.proxy_node import ProxyNode

        if isinstance(classifier_instance, ProxyNode):
            raise ValueError("Proxy nodes cannot be serialized")

        classifier_instances = set[ClassifierInstance]()
        ClassifierInstance.collect_self_and_descendants(
            classifier_instance, True, classifier_instances
        )

        filtered_instances = [n for n in classifier_instances if not isinstance(n, ProxyNode)]
        return self.serialize_nodes_to_json_element(filtered_instances)

    def deserialize_json_to_nodes(self, json_element: JsonElement) -> list[Node]:
        return [
            ci
            for ci in self.deserialize_to_classifier_instances(json_element)
            if isinstance(ci, Node)
        ]

    def deserialize_path_to_nodes(self, source: Path) -> list[Node]:
        return self.deserialize_string_to_nodes(source.read_text())

    def deserialize_string_to_nodes(self, json_str: str) -> list[Node]:
        return self.deserialize_json_to_nodes(json.loads(json_str))

    def deserialize_to_classifier_instances(self, json_element: JsonElement):
        serialization_block = LowLevelJsonSerialization().deserialize_serialization_block(
            json_element
        )
        self._validate_serialization_chunk(serialization_block)
        return self.deserialize_serialization_chunk(serialization_block)
