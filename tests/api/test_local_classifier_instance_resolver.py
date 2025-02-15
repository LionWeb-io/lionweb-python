import unittest

from lionwebpython.api.local_classifier_instance_resolver import \
    LocalClassifierInstanceResolver
from lionwebpython.language import Concept
from lionwebpython.model.impl.dynamic_node import DynamicNode
from lionwebpython.model.impl.proxy_node import ProxyNode


class LocalClassifierInstanceResolverTest(unittest.TestCase):

    def test_resolve_or_proxy_when_cannot_be_solved(self):
        concept = Concept()
        lcir = LocalClassifierInstanceResolver()
        lcir.add(DynamicNode("123", concept))

        self.assertEqual(
            ProxyNode("unexistingID"), lcir.resolve_or_proxy("unexistingID")
        )

    def test_resolve_or_proxy_when_can_be_solved(self):
        concept = Concept()
        lcir = LocalClassifierInstanceResolver()
        n123 = DynamicNode("123", concept)
        lcir.add(n123)

        self.assertIs(n123, lcir.resolve_or_proxy("123"))

    def test_vararg_constructor(self):
        concept = Concept()
        n123 = DynamicNode("123", concept)
        n456 = DynamicNode("456", concept)
        n789 = DynamicNode("789", concept)

        lcir = LocalClassifierInstanceResolver(n123, n456, n789)

        self.assertIsNone(lcir.resolve("unexistingID"))
        self.assertIs(n123, lcir.resolve_or_proxy("123"))
        self.assertIs(n456, lcir.resolve_or_proxy("456"))
        self.assertIs(n789, lcir.resolve_or_proxy("789"))

    def test_list_constructor(self):
        concept = Concept()
        n123 = DynamicNode("123", concept)
        n456 = DynamicNode("456", concept)
        n789 = DynamicNode("789", concept)

        instances = [n123, n456, n789]
        lcir = LocalClassifierInstanceResolver(*instances)

        self.assertIsNone(lcir.resolve("unexistingID"))
        self.assertIs(n123, lcir.resolve_or_proxy("123"))
        self.assertIs(n456, lcir.resolve_or_proxy("456"))
        self.assertIs(n789, lcir.resolve_or_proxy("789"))


if __name__ == "__main__":
    unittest.main()
