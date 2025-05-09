import unittest

from lionweb.language import Containment


class ContainmentTest(unittest.TestCase):

    def test_key_property(self):
        c1 = Containment()
        c1.key = "k1"
        self.assertEqual("k1", c1.key)
        self.assertEqual("k1", c1.get_key())
        self.assertEqual("k1", c1.get_property_value(property="key"))

        c2 = Containment()
        c2.set_key("k2")
        self.assertEqual("k2", c2.key)
        self.assertEqual("k2", c2.get_key())
        self.assertEqual("k2", c2.get_property_value(property="key"))

        c3 = Containment()
        c3.set_property_value(property="key", value="k3")
        self.assertEqual("k3", c3.key)
        self.assertEqual("k3", c3.get_key())
        self.assertEqual("k3", c3.get_property_value(property="key"))


if __name__ == "__main__":
    unittest.main()
