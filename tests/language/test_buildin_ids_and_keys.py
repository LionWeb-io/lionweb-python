import unittest

from lionweb.lionweb_version import LionWebVersion
from lionweb.self.lioncore import LionCore


class BuiltinIDsAndKeysTest(unittest.TestCase):

    def test_M3ElementsHasExpectedIDsIn2023_1(self):
        self.assertEqual("-id-Concept", LionCore.get_concept(LionWebVersion.V2023_1).id)
        self.assertEqual(
            "-id-Concept-abstract",
            LionCore.get_concept(LionWebVersion.V2023_1)
            .get_property_by_name("abstract")
            .id,
        )
        self.assertEqual(
            "-id-Concept-extends",
            LionCore.get_concept(LionWebVersion.V2023_1)
            .get_reference_by_name("extends")
            .id,
        )
        self.assertEqual(
            "-id-Concept-implements",
            LionCore.get_concept(LionWebVersion.V2023_1)
            .get_reference_by_name("implements")
            .id,
        )

        self.assertEqual(
            "-id-Interface", LionCore.get_interface(LionWebVersion.V2023_1).id
        )
        self.assertEqual(
            "-id-Interface-extends",
            LionCore.get_interface(LionWebVersion.V2023_1)
            .get_reference_by_name("extends")
            .id,
        )

        self.assertEqual(
            "-id-Containment", LionCore.get_containment(LionWebVersion.V2023_1).id
        )
        self.assertEqual(
            "-id-DataType", LionCore.get_data_type(LionWebVersion.V2023_1).id
        )
        self.assertEqual(
            "-id-Enumeration", LionCore.get_enumeration(LionWebVersion.V2023_1).id
        )

        self.assertEqual(
            "-id-Enumeration-literals",
            LionCore.get_enumeration(LionWebVersion.V2023_1)
            .get_containment_by_name("literals")
            .id,
        )

        self.assertEqual(
            "-id-EnumerationLiteral",
            LionCore.get_enumeration_literal(LionWebVersion.V2023_1).id,
        )
        self.assertEqual("-id-Feature", LionCore.get_feature(LionWebVersion.V2023_1).id)

        self.assertEqual(
            "-id-Feature-optional",
            LionCore.get_feature(LionWebVersion.V2023_1)
            .get_property_by_name("optional")
            .id,
        )

        self.assertEqual(
            "-id-Classifier", LionCore.get_classifier(LionWebVersion.V2023_1).id
        )

        self.assertEqual(
            "-id-Classifier-features",
            LionCore.get_classifier(LionWebVersion.V2023_1)
            .get_containment_by_name("features")
            .id,
        )

        self.assertEqual("-id-Link", LionCore.get_link(LionWebVersion.V2023_1).id)
        self.assertEqual(
            "-id-Link-multiple",
            LionCore.get_link(LionWebVersion.V2023_1)
            .get_property_by_name("multiple")
            .id,
        )
        self.assertEqual(
            "-id-Link-type",
            LionCore.get_link(LionWebVersion.V2023_1).get_reference_by_name("type").id,
        )

        self.assertEqual(
            "-id-Language", LionCore.get_language(LionWebVersion.V2023_1).id
        )
        self.assertEqual(
            "LionCore-builtins-INamed-name",
            LionCore.get_language(LionWebVersion.V2023_1)
            .get_property_by_name("name")
            .id,
        )
        self.assertEqual(
            "-id-IKeyed-key",
            LionCore.get_language(LionWebVersion.V2023_1)
            .get_property_by_name("key")
            .id,
        )
        self.assertEqual(
            "-id-Language-dependsOn",
            LionCore.get_language(LionWebVersion.V2023_1)
            .get_reference_by_name("dependsOn")
            .id,
        )
        self.assertEqual(
            "-id-Language-entities",
            LionCore.get_language(LionWebVersion.V2023_1)
            .get_containment_by_name("entities")
            .id,
        )

    def test_M3ElementsHasExpectedIDsIn2024_1(self):
        self.assertEqual(
            "-id-Concept-2024-1", LionCore.get_concept(LionWebVersion.V2024_1).id
        )
        self.assertEqual(
            "-id-Concept-abstract-2024-1",
            LionCore.get_concept(LionWebVersion.V2024_1)
            .get_property_by_name("abstract")
            .id,
        )

        self.assertEqual(
            "-id-Concept-extends-2024-1",
            LionCore.get_concept(LionWebVersion.V2024_1)
            .get_reference_by_name("extends")
            .id,
        )

        self.assertEqual(
            "-id-Interface-2024-1",
            LionCore.get_interface(LionWebVersion.V2024_1).id,
        )

        self.assertEqual(
            "-id-Containment-2024-1",
            LionCore.get_containment(LionWebVersion.V2024_1).id,
        )

        self.assertEqual(
            "-id-DataType-2024-1",
            LionCore.get_data_type(LionWebVersion.V2024_1).id,
        )

        self.assertEqual(
            "-id-Enumeration-2024-1",
            LionCore.get_enumeration(LionWebVersion.V2024_1).id,
        )
        self.assertEqual(
            "-id-Enumeration-literals-2024-1",
            LionCore.get_enumeration(LionWebVersion.V2024_1)
            .get_containment_by_name("literals")
            .id,
        )

        self.assertEqual(
            "-id-EnumerationLiteral-2024-1",
            LionCore.get_enumeration_literal(LionWebVersion.V2024_1).id,
        )

        self.assertEqual(
            "-id-Feature-2024-1", LionCore.get_feature(LionWebVersion.V2024_1).id
        )

        self.assertEqual(
            "-id-Feature-optional-2024-1",
            LionCore.get_feature(LionWebVersion.V2024_1)
            .get_property_by_name("optional")
            .id,
        )

    def test_M3ElementsHasExpectedKeys(self):
        self.assertEqual("Concept", LionCore.get_concept().key)
        self.assertEqual(
            "Concept-abstract",
            LionCore.get_concept().get_property_by_name("abstract").key,
        )
        self.assertEqual(
            "Concept-extends",
            LionCore.get_concept().get_reference_by_name("extends").key,
        )
        self.assertEqual("Interface", LionCore.get_interface().key)
        self.assertEqual(
            "Interface-extends",
            LionCore.get_interface().get_reference_by_name("extends").key,
        )

        self.assertEqual("Containment", LionCore.get_containment().key)

        self.assertEqual("DataType", LionCore.get_data_type().key)

        self.assertEqual("Enumeration", LionCore.get_enumeration().key)
        self.assertEqual(
            "Enumeration-literals",
            LionCore.get_enumeration().get_containment_by_name("literals").key,
        )

        self.assertEqual("EnumerationLiteral", LionCore.get_enumeration_literal().key)

        self.assertEqual("Feature", LionCore.get_feature().key)
        self.assertEqual(
            "Feature-optional",
            LionCore.get_feature().get_property_by_name("optional").key,
        )

        self.assertEqual("Classifier", LionCore.get_classifier().key)
        self.assertEqual(
            "Classifier-features",
            LionCore.get_classifier().get_containment_by_name("features").key,
        )

        self.assertEqual("Link", LionCore.get_link().key)
        self.assertEqual(
            "Link-multiple",
            LionCore.get_link().get_property_by_name("multiple").key,
        )
        self.assertEqual(
            "Link-type", LionCore.get_link().get_reference_by_name("type").key
        )

        self.assertEqual("Language", LionCore.get_language().key)
        self.assertEqual(
            "LionCore-builtins-INamed-name",
            LionCore.get_language().get_property_by_name("name").key,
        )
        self.assertEqual(
            "IKeyed-key", LionCore.get_language().get_property_by_name("key").key
        )
        self.assertEqual(
            "Language-dependsOn",
            LionCore.get_language().get_reference_by_name("dependsOn").key,
        )
        self.assertEqual(
            "Language-entities",
            LionCore.get_language().get_containment_by_name("entities").key,
        )

        self.assertEqual("LanguageEntity", LionCore.get_language_entity().key)

        self.assertEqual("PrimitiveType", LionCore.get_primitive_type().key)

        self.assertEqual("Property", LionCore.get_property().key)
        self.assertEqual(
            "Property-type",
            LionCore.get_property().get_reference_by_name("type").key,
        )

        self.assertEqual("Reference", LionCore.get_reference().key)


if __name__ == "__main__":
    unittest.main()
