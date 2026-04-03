import unittest

from lionweb.serialization.data.raw_reference_value import RawReferenceValue


class TestRawReferenceValue(unittest.TestCase):
    def test_creation(self):
        rv = RawReferenceValue(referred_id="node-1", resolve_info="SomeName")
        self.assertEqual(rv.referred_id, "node-1")
        self.assertEqual(rv.resolve_info, "SomeName")

    def test_equality(self):
        rv1 = RawReferenceValue(referred_id="node-1", resolve_info="SomeName")
        rv2 = RawReferenceValue(referred_id="node-1", resolve_info="SomeName")
        self.assertEqual(rv1, rv2)

    def test_inequality(self):
        rv1 = RawReferenceValue(referred_id="node-1", resolve_info="A")
        rv2 = RawReferenceValue(referred_id="node-2", resolve_info="A")
        self.assertNotEqual(rv1, rv2)

    def test_repr(self):
        rv = RawReferenceValue(referred_id="node-1", resolve_info="SomeName")
        self.assertIn("node-1", repr(rv))
        self.assertIn("SomeName", repr(rv))


if __name__ == "__main__":
    unittest.main()
