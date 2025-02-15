import unittest

from lionwebpython.api.composite_classifier_instance_resolver import \
    CompositeClassifierInstanceResolver


class CompositeClassifierInstanceResolverTest(unittest.TestCase):

    def test_empty_composite_classifier(self):
        instance_resolver = CompositeClassifierInstanceResolver()
        self.assertIsNone(instance_resolver.resolve("Foo"))
        self.assertEqual(
            str(instance_resolver), "CompositeClassifierInstanceResolver([])"
        )


if __name__ == "__main__":
    unittest.main()
