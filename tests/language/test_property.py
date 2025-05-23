import unittest

from lionweb.language import Property


class PropertyTest(unittest.TestCase):

    def test_key_property(self):
        p1 = Property()
        p1.key = "k1"
        self.assertEqual("k1", p1.key)
        self.assertEqual("k1", p1.get_key())
        self.assertEqual("k1", p1.get_property_value(property="key"))

        p2 = Property()
        p2.key = "k2"
        self.assertEqual("k2", p2.key)
        self.assertEqual("k2", p2.get_key())
        self.assertEqual("k2", p2.get_property_value(property="key"))

        p3 = Property()
        p3.set_property_value(property="key", value="k3")
        self.assertEqual("k3", p3.key)
        self.assertEqual("k3", p3.get_key())
        self.assertEqual("k3", p3.get_property_value(property="key"))

    def test_optional_property(self):
        p1 = Property()
        p1.optional = True
        self.assertTrue(p1.optional)
        self.assertTrue(p1.get_property_value(property="optional"))

        p2 = Property()
        p2.optional = False
        self.assertFalse(p2.optional)
        self.assertFalse(p2.get_property_value(property="optional"))

    def test_type_property(self):
        from lionweb.language.lioncore_builtins import LionCoreBuiltins
        from lionweb.lionweb_version import LionWebVersion

        p1 = Property()
        p1.type = LionCoreBuiltins.get_string(LionWebVersion.current_version())
        self.assertEqual(
            LionCoreBuiltins.get_string(LionWebVersion.current_version()), p1.type
        )

        p2 = Property()
        p2.type = None
        self.assertIsNone(p2.type)


if __name__ == "__main__":
    unittest.main()
