import json
from io import TextIOWrapper
from typing import List
from urllib.request import urlopen

from lionwebpython.language import Language
from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.serialization.abstract_serialization import \
    AbstractSerialization


class JsonSerialization(AbstractSerialization):
    def __init__(
        self, lionweb_version: LionWebVersion = LionWebVersion.current_version()
    ):
        super().__init__(lionweb_version=lionweb_version)

    @staticmethod
    def save_language_to_file(language: Language, file_path: str):
        content = JsonSerialization().serialize_trees_to_json_string(language)
        with open(file_path, "w") as f:
            f.write(content)

    def load_language_from_file(self, file_path: str) -> Language:
        with open(file_path, "r") as f:
            content = f.read()
        return self.deserialize_to_nodes(content)

    def load_language_from_input_stream(self, input_stream):
        # """
        # Load a single Language from an InputStream. If the InputStream contains more than one language,
        # an exception is thrown.
        # """
        # json_serialization = get_standard_json_serialization(get_lion_web_version())
        # nodes = json_serialization.deserialize_to_nodes(input_stream)
        # languages = [node for node in nodes if isinstance(node, Language)]
        #
        # if len(languages) != 1:
        #     raise ValueError("Expected exactly one Language, found: {}".format(len(languages)))
        #
        # return languages[0]
        raise ValueError("NOT YET TRANSLATED")

    def serialize_tree_to_json_element(self, classifier_instance):
        instances = self.collect_descendants(classifier_instance)
        return self.serialize_nodes_to_json_element(instances)

    def serialize_trees_to_json_element(self, *roots):
        all_nodes = set()
        for root in roots:
            nodes = self.collect_descendants(root)
            all_nodes.update(nodes)
        return self.serialize_nodes_to_json_element(list(all_nodes))

    def serialize_nodes_to_json_element(self, classifier_instances: List):
        serialization_block = self.serialize_nodes_to_serialization_block(
            classifier_instances
        )
        return json.dumps(serialization_block, indent=2)

    def serialize_tree_to_json_string(self, classifier_instance):
        return json.dumps(
            self.serialize_tree_to_json_element(classifier_instance), indent=2
        )

    def serialize_trees_to_json_string(self, *classifier_instances):
        return json.dumps(
            self.serialize_trees_to_json_element(*classifier_instances), indent=2
        )

    def serialize_nodes_to_json_string(self, classifier_instances: List):
        return json.dumps(
            self.serialize_nodes_to_json_element(classifier_instances), indent=2
        )

    def collect_descendants(self, node):
        """Collects a node and its descendants."""
        nodes = set()

        def traverse(n):
            nodes.add(n)
            for child in getattr(n, "children", []):
                traverse(child)

        traverse(node)
        return nodes

    def serialize_nodes_to_serialization_block(self, classifier_instances):
        """Convert classifier instances to a serialization block."""
        serialized_chunk = {
            "serializationFormatVersion": self.lion_web_version,
            "nodes": [],
            "languages": [],
        }
        languages = set()

        for instance in classifier_instances:
            serialized_node = {
                "id": instance.get("id"),
                "classifier": instance.get("classifier"),
                "parent": instance.get("parent"),
                "properties": instance.get("properties", {}),
                "containments": instance.get("containments", []),
                "references": instance.get("references", []),
                "annotations": instance.get("annotations", []),
            }
            serialized_chunk["nodes"].append(serialized_node)
            languages.add(instance.get("language"))

        serialized_chunk["languages"] = list(languages)
        return serialized_chunk

    def deserialize_to_nodes(self, json_content: str):
        if isinstance(json_content, TextIOWrapper):
            content = json_content.read()
        else:
            content = json_content
        json_data = json.loads(content)
        nodes = json_data.get("nodes", [])
        return [self.deserialize_node(node) for node in nodes]

    def deserialize_node(self, node_data):
        node_id = node_data.get("id")
        classifier = node_data.get("classifier")
        properties = node_data.get("properties", {})
        children = node_data.get("containments", [])
        references = node_data.get("references", [])
        annotations = node_data.get("annotations", [])

        node = {
            "id": node_id,
            "classifier": classifier,
            "properties": properties,
            "children": children,
            "references": references,
            "annotations": annotations,
        }
        return node

    def deserialize_to_nodes_from_url(self, url: str):
        with urlopen(url) as response:
            content = response.read().decode("utf-8")
        return self.deserialize_to_nodes(content)
