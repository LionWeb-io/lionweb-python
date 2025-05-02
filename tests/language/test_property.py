import unittest

from lionweb.language import Property


class PropertyTest(unittest.TestCase):

    def test_key_property(self):
        p1 = Property()
        p1.key = "k1"
        self.assertEqual("k1", p1.key)
        self.assertEqual("k1", p1.get_key())
        self.assertEqual("k1", p1.get_property_value(property_name="key"))

        p2 = Property()
        p2.set_key("k2")
        self.assertEqual("k2", p2.key)
        self.assertEqual("k2", p2.get_key())
        self.assertEqual("k2", p2.get_property_value(property_name="key"))

        p3 = Property()
        p3.set_property_value(property_name="key", value="k3")
        self.assertEqual("k3", p3.key)
        self.assertEqual("k3", p3.get_key())
        self.assertEqual("k3", p3.get_property_value(property_name="key"))


if __name__ == "__main__":
    unittest.main()
