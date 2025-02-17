import unittest
from typing import TYPE_CHECKING, List

from lionwebpython.language import Concept, Property
from lionwebpython.model import ClassifierInstance
from lionwebpython.model.node import Node
from lionwebpython.serialization.json_utils import JsonArray, JsonObject
from lionwebpython.utils.model_comparator import ModelComparator

if TYPE_CHECKING:
    from lionwebpython.model.impl.dynamic_node import DynamicNode


class SerializationTest(unittest.TestCase):

    def get_nodes_by_concept(
        self, nodes: JsonArray, concept_key: str
    ) -> List[JsonObject]:
        """Get nodes matching a specific concept key."""
        return [
            node
            for node in nodes
            if node.get("classifier", {}).get("key") == concept_key
        ]

    def dynamic_node_by_id(seld, nodes: List["Node"], node_id: str) -> "DynamicNode":
        """Retrieve a DynamicNode by ID."""
        for node in nodes:
            if node.get_id() == node_id:
                return node
        raise ValueError(f"No DynamicNode found with ID: {node_id}")

    def concept_by_id(self, nodes: List["Node"], node_id: str) -> "Concept":
        """Retrieve a Concept by ID."""
        for node in nodes:
            if not isinstance(node, Node):
                raise ValueError(f"A Node instance was expected, but we got {node}")
            if node.get_id() == node_id:
                return node
        raise ValueError(f"No Concept found with ID: {node_id}")

    def property_by_id(nodes: List["Node"], node_id: str) -> "Property":
        """Retrieve a Property by ID."""
        for node in nodes:
            if node.get_id() == node_id:
                return node
        raise ValueError(f"No Property found with ID: {node_id}")

    def assert_instances_are_equal(
        self, a: "ClassifierInstance", b: "ClassifierInstance"
    ) -> None:
        """Assert that two classifier instances are equal."""
        model_comparator = ModelComparator()
        comparison_result = model_comparator.compare(a, b)
        if not comparison_result.are_equivalent():
            raise AssertionError(str(comparison_result))
