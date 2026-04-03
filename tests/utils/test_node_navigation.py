import unittest

from lionweb.language import Concept
from lionweb.model.impl.dynamic_node import DynamicNode
from lionweb.utils.node_navigation import root


class TestNodeNavigation(unittest.TestCase):
    def _make_node(self, node_id: str) -> DynamicNode:
        c = Concept()
        c.set_partition(True)
        return DynamicNode(node_id, c)

    def test_root_single_root(self):
        node = self._make_node("root-1")
        result = root([node])
        self.assertIs(result, node)

    def test_root_raises_on_empty_list(self):
        with self.assertRaises(ValueError):
            root([])

    def test_root_raises_on_multiple_roots(self):
        n1 = self._make_node("n1")
        n2 = self._make_node("n2")
        with self.assertRaises(ValueError):
            root([n1, n2])


if __name__ == "__main__":
    unittest.main()
