import unittest

from lionwebpython.self.lioncore import LionCore
from lionwebpython.utils.language_validator import LanguageValidator


class LionCoreTest(unittest.TestCase):

    def test_lion_core_is_valid(self):
        vr = LanguageValidator().validate(LionCore.get_instance())
        if not vr.is_successful():
            raise RuntimeError(f"LionCore Language is not valid: {vr}")

    def test_check_property(self):
        property_concept = LionCore.get_property()
        name = property_concept.get_property_by_name("name")
        self.assertIsNotNone(name)
        self.assertEqual("LionCore-builtins-INamed-name", name.get_key())
        self.assertEqual("LionCore-builtins", name.get_declaring_language().get_key())

        key = property_concept.get_property_by_name("key")
        self.assertIsNotNone(key)

    def test_check_language(self):
        language_concept = LionCore.get_language()
        name = language_concept.get_property_by_name("name")
        self.assertIsNotNone(name)
        self.assertEqual("LionCore-builtins-INamed-name", name.get_key())
        self.assertEqual("LionCore-builtins", name.get_declaring_language().get_key())

        version = language_concept.get_property_by_name("version")
        self.assertIsNotNone(version)

    def test_check_sdt_fields_are_required(self):
        sdt = LionCore.get_structured_data_type()
        fields = sdt.get_containment_by_name("fields")
        self.assertTrue(fields.is_required())
        self.assertFalse(fields.is_optional())


if __name__ == "__main__":
    unittest.main()
