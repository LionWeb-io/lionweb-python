import unittest

from lionweb.language import Reference


class ReferenceTest(unittest.TestCase):

    def test_key_property(self):
        r1 = Reference()
        r1.key = "k1"
        self.assertEqual("k1", r1.key)
        self.assertEqual("k1", r1.get_key())
        self.assertEqual("k1", r1.get_property_value(property_name="key"))

        r2 = Reference()
        r2.set_key("k2")
        self.assertEqual("k2", r2.key)
        self.assertEqual("k2", r2.get_key())
        self.assertEqual("k2", r2.get_property_value(property_name="key"))

        r3 = Reference()
        r3.set_property_value(property_name="key", value="k3")
        self.assertEqual("k3", r3.key)
        self.assertEqual("k3", r3.get_key())
        self.assertEqual("k3", r3.get_property_value(property_name="key"))


if __name__ == "__main__":
    unittest.main()
