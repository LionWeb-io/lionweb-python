import unittest

from lionwebpython.language import Concept
from lionwebpython.model.impl.dynamic_node import DynamicNode
from lionwebpython.utils.issue import Issue
from lionwebpython.utils.issue_severity import IssueSeverity
from lionwebpython.utils.node_tree_validator import NodeTreeValidator


class NodeTreeValidatorTest(unittest.TestCase):

    def test_everything_correct_case(self):
        c = Concept()
        c.set_partition(True)
        node = DynamicNode("abc", c)
        vr = NodeTreeValidator().validate(node)
        self.assertTrue(vr.is_successful())
        self.assertEqual(set(), vr.get_issues())

    def test_a_node_without_id_is_not_valid(self):
        c = Concept()
        c.set_partition(True)
        node = DynamicNode(None, c)
        vr = NodeTreeValidator().validate(node)
        self.assertFalse(vr.is_successful())
        self.assertEqual(
            {Issue(IssueSeverity.ERROR, "ID null found", node)}, vr.get_issues()
        )

    def test_a_node_with_invalid_id_is_not_valid(self):
        c = Concept()
        c.set_partition(True)
        node = DynamicNode("@@@", c)
        vr = NodeTreeValidator().validate(node)
        self.assertFalse(vr.is_successful())
        self.assertEqual(
            {Issue(IssueSeverity.ERROR, "Invalid ID", node)}, vr.get_issues()
        )

    def test_root_node_which_is_not_partition(self):
        non_partition_concept = Concept()
        non_partition_concept.set_partition(False)
        node = DynamicNode("N1", non_partition_concept)
        vr = NodeTreeValidator().validate(node)
        self.assertFalse(vr.is_successful())
        self.assertEqual(
            {
                Issue(
                    IssueSeverity.ERROR,
                    "A root node should be an instance of a Partition concept",
                    node,
                )
            },
            vr.get_issues(),
        )

    def test_root_node_which_is_partition(self):
        partition_concept = Concept()
        partition_concept.set_partition(True)
        node = DynamicNode("N1", partition_concept)
        vr = NodeTreeValidator().validate(node)
        self.assertTrue(vr.is_successful())


if __name__ == "__main__":
    unittest.main()
