import unittest

from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.self.lioncore import LionCore


class BuiltinIDsAndKeysTest(unittest.TestCase):

    def test_M3ElementsHasExpectedIDsIn2023_1(self):
        self.assertEqual(
            "-id-Concept", LionCore.get_concept(LionWebVersion.V2023_1).get_id()
        )
        self.assertEqual(
            "-id-Concept-abstract",
            LionCore.get_concept(LionWebVersion.V2023_1)
            .get_property_by_name("abstract")
            .get_id(),
        )
        self.assertEqual(
            "-id-Concept-extends",
            LionCore.get_concept(LionWebVersion.V2023_1)
            .get_reference_by_name("extends")
            .get_id(),
        )
        self.assertEqual(
            "-id-Concept-implements",
            LionCore.get_concept(LionWebVersion.V2023_1)
            .get_reference_by_name("implements")
            .get_id(),
        )

        self.assertEqual(
            "-id-Interface", LionCore.get_interface(LionWebVersion.V2023_1).get_id()
        )
        self.assertEqual(
            "-id-Interface-extends",
            LionCore.get_interface(LionWebVersion.V2023_1)
            .get_reference_by_name("extends")
            .get_id(),
        )

        self.assertEqual(
            "-id-Containment", LionCore.get_containment(LionWebVersion.V2023_1).get_id()
        )
        self.assertEqual(
            "-id-DataType", LionCore.get_data_type(LionWebVersion.V2023_1).get_id()
        )
        self.assertEqual(
            "-id-Enumeration", LionCore.get_enumeration(LionWebVersion.V2023_1).get_id()
        )

        self.assertEqual(
            "-id-Enumeration-literals",
            LionCore.get_enumeration(LionWebVersion.V2023_1)
            .get_containment_by_name("literals")
            .get_id(),
        )

        self.assertEqual(
            "-id-EnumerationLiteral",
            LionCore.get_enumeration_literal(LionWebVersion.V2023_1).get_id(),
        )
        self.assertEqual(
            "-id-Feature", LionCore.get_feature(LionWebVersion.V2023_1).get_id()
        )

        self.assertEqual(
            "-id-Feature-optional",
            LionCore.get_feature(LionWebVersion.V2023_1)
            .get_property_by_name("optional")
            .get_id(),
        )

        self.assertEqual(
            "-id-Classifier", LionCore.get_classifier(LionWebVersion.V2023_1).get_id()
        )

        self.assertEqual(
            "-id-Classifier-features",
            LionCore.get_classifier(LionWebVersion.V2023_1)
            .get_containment_by_name("features")
            .get_id(),
        )

        self.assertEqual("-id-Link", LionCore.get_link(LionWebVersion.V2023_1).get_id())
        self.assertEqual(
            "-id-Link-multiple",
            LionCore.get_link(LionWebVersion.V2023_1)
            .get_property_by_name("multiple")
            .get_id(),
        )
        self.assertEqual(
            "-id-Link-type",
            LionCore.get_link(LionWebVersion.V2023_1)
            .get_reference_by_name("type")
            .get_id(),
        )

        self.assertEqual(
            "-id-Language", LionCore.get_language(LionWebVersion.V2023_1).get_id()
        )
        self.assertEqual(
            "LionCore-builtins-INamed-name",
            LionCore.get_language(LionWebVersion.V2023_1)
            .get_property_by_name("name")
            .get_id(),
        )
        self.assertEqual(
            "-id-IKeyed-key",
            LionCore.get_language(LionWebVersion.V2023_1)
            .get_property_by_name("key")
            .get_id(),
        )
        self.assertEqual(
            "-id-Language-dependsOn",
            LionCore.get_language(LionWebVersion.V2023_1)
            .get_reference_by_name("dependsOn")
            .get_id(),
        )
        self.assertEqual(
            "-id-Language-entities",
            LionCore.get_language(LionWebVersion.V2023_1)
            .get_containment_by_name("entities")
            .get_id(),
        )

    def test_M3ElementsHasExpectedIDsIn2024_1(self):
        self.assertEqual(
            "-id-Concept-2024-1", LionCore.get_concept(LionWebVersion.V2024_1).get_id()
        )
        self.assertEqual(
            "-id-Concept-abstract-2024-1",
            LionCore.get_concept(LionWebVersion.V2024_1)
            .get_property_by_name("abstract")
            .get_id(),
        )

        self.assertEqual(
            "-id-Concept-extends-2024-1",
            LionCore.get_concept(LionWebVersion.V2024_1)
            .get_reference_by_name("extends")
            .get_id(),
        )

        self.assertEqual(
            "-id-Interface-2024-1",
            LionCore.get_interface(LionWebVersion.V2024_1).get_id(),
        )

        self.assertEqual(
            "-id-Containment-2024-1",
            LionCore.get_containment(LionWebVersion.V2024_1).get_id(),
        )

        self.assertEqual(
            "-id-DataType-2024-1",
            LionCore.get_data_type(LionWebVersion.V2024_1).get_id(),
        )

        self.assertEqual(
            "-id-Enumeration-2024-1",
            LionCore.get_enumeration(LionWebVersion.V2024_1).get_id(),
        )
        self.assertEqual(
            "-id-Enumeration-literals-2024-1",
            LionCore.get_enumeration(LionWebVersion.V2024_1)
            .get_containment_by_name("literals")
            .get_id(),
        )

        self.assertEqual(
            "-id-EnumerationLiteral-2024-1",
            LionCore.get_enumeration_literal(LionWebVersion.V2024_1).get_id(),
        )

        self.assertEqual(
            "-id-Feature-2024-1", LionCore.get_feature(LionWebVersion.V2024_1).get_id()
        )

        self.assertEqual(
            "-id-Feature-optional-2024-1",
            LionCore.get_feature(LionWebVersion.V2024_1)
            .get_property_by_name("optional")
            .get_id(),
        )

    def test_M3ElementsHasExpectedKeys(self):
        self.assertEqual("Concept", LionCore.get_concept().get_key())
        self.assertEqual(
            "Concept-abstract",
            LionCore.get_concept().get_property_by_name("abstract").get_key(),
        )
        self.assertEqual(
            "Concept-extends",
            LionCore.get_concept().get_reference_by_name("extends").get_key(),
        )
        self.assertEqual("Interface", LionCore.get_interface().get_key())
        self.assertEqual(
            "Interface-extends",
            LionCore.get_interface().get_reference_by_name("extends").get_key(),
        )

        self.assertEqual("Containment", LionCore.get_containment().get_key())

        self.assertEqual("DataType", LionCore.get_data_type().get_key())

        self.assertEqual("Enumeration", LionCore.get_enumeration().get_key())
        self.assertEqual(
            "Enumeration-literals",
            LionCore.get_enumeration().get_containment_by_name("literals").get_key(),
        )

        self.assertEqual(
            "EnumerationLiteral", LionCore.get_enumeration_literal().get_key()
        )

        self.assertEqual("Feature", LionCore.get_feature().get_key())
        self.assertEqual(
            "Feature-optional",
            LionCore.get_feature().get_property_by_name("optional").get_key(),
        )

        self.assertEqual("Classifier", LionCore.get_classifier().get_key())
        self.assertEqual(
            "Classifier-features",
            LionCore.get_classifier().get_containment_by_name("features").get_key(),
        )

        self.assertEqual("Link", LionCore.get_link().get_key())
        self.assertEqual(
            "Link-multiple",
            LionCore.get_link().get_property_by_name("multiple").get_key(),
        )
        self.assertEqual(
            "Link-type", LionCore.get_link().get_reference_by_name("type").get_key()
        )

        self.assertEqual("Language", LionCore.get_language().get_key())
        self.assertEqual(
            "LionCore-builtins-INamed-name",
            LionCore.get_language().get_property_by_name("name").get_key(),
        )
        self.assertEqual(
            "IKeyed-key", LionCore.get_language().get_property_by_name("key").get_key()
        )
        self.assertEqual(
            "Language-dependsOn",
            LionCore.get_language().get_reference_by_name("dependsOn").get_key(),
        )
        self.assertEqual(
            "Language-entities",
            LionCore.get_language().get_containment_by_name("entities").get_key(),
        )

        self.assertEqual("LanguageEntity", LionCore.get_language_entity().get_key())

        self.assertEqual("PrimitiveType", LionCore.get_primitive_type().get_key())

        self.assertEqual("Property", LionCore.get_property().get_key())
        self.assertEqual(
            "Property-type",
            LionCore.get_property().get_reference_by_name("type").get_key(),
        )

        self.assertEqual("Reference", LionCore.get_reference().get_key())


if __name__ == "__main__":
    unittest.main()
