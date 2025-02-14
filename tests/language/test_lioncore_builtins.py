import unittest

from lionwebpython.language.lioncore_builtins import LionCoreBuiltins
from lionwebpython.language.primitive_type import PrimitiveType
from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.utils.language_validator import LanguageValidator


class LionCoreBuiltinsTest(unittest.TestCase):

    def test_string_primitive_type(self):
        string = LionCoreBuiltins.get_instance().get_element_by_name("String")
        self.assertIsInstance(string, PrimitiveType)
        self.assertEqual("String", string.get_name())
        self.assertEqual("LionCore_builtins.String", string.qualified_name())

    def test_primitive_types_have_agreed_ids_v2023(self):
        self.assertEqual(
            "LionCore-builtins-String",
            LionCoreBuiltins.get_string(LionWebVersion.V2023_1).get_id(),
        )
        self.assertEqual(
            "LionCore-builtins-Boolean",
            LionCoreBuiltins.get_boolean(LionWebVersion.V2023_1).get_id(),
        )
        self.assertEqual(
            "LionCore-builtins-Integer",
            LionCoreBuiltins.get_integer(LionWebVersion.V2023_1).get_id(),
        )
        self.assertEqual(
            "LionCore-builtins-JSON",
            LionCoreBuiltins.get_json(LionWebVersion.V2023_1).get_id(),
        )

    def test_primitive_types_have_agreed_ids_v2024(self):
        self.assertEqual(
            "LionCore-builtins-String-2024-1",
            LionCoreBuiltins.get_string(LionWebVersion.V2024_1).get_id(),
        )
        self.assertEqual(
            "LionCore-builtins-Boolean-2024-1",
            LionCoreBuiltins.get_boolean(LionWebVersion.V2024_1).get_id(),
        )
        self.assertEqual(
            "LionCore-builtins-Integer-2024-1",
            LionCoreBuiltins.get_integer(LionWebVersion.V2024_1).get_id(),
        )
        with self.assertRaises(ValueError):
            LionCoreBuiltins.get_json(LionWebVersion.V2024_1)

    def test_lion_core_builtins_is_valid(self):
        vr = LanguageValidator().validate(LionCoreBuiltins.get_instance())
        if not vr.is_successful():
            raise RuntimeError(f"LionCoreBuiltins Language is not valid: {vr}")


if __name__ == "__main__":
    unittest.main()
