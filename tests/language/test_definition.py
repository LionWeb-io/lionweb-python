import unittest

from lionweb import LionWebVersion
from lionweb.language import LanguageFactory, LionCoreBuiltins, Multiplicity
from lionweb.self.lioncore import LionCore


class DefinitionTest(unittest.TestCase):

    def test_language_definition(self):
        factory = LanguageFactory(
            lw_version=LionWebVersion.V2023_1,
            name="com.strumenta.StarLasu",
            id="com-strumenta-StarLasu",
            key="com_strumenta_starlasu",
        )
        factory.primitive_type("Char")
        factory.primitive_type("Point")
        position = factory.primitive_type("Position")

        ast_node = factory.concept("ASTNode")
        (
            ast_node.property("position", position, Multiplicity.OPTIONAL)
            .reference("originalNode", ast_node, Multiplicity.OPTIONAL)
            .reference("transpiledNodes", ast_node, Multiplicity.ZERO_OR_MORE)
        )
        placeholder_node_type = factory.enumeration(
            "PlaceholderNodeType",
            ["MissingASTTransformation", "FailingASTTransformation"],
        )
        (
            factory.annotation(
                "PlaceholderNode", LionCore.get_concept(LionWebVersion.V2023_1)
            )
            .reference("originalNode", ast_node, Multiplicity.OPTIONAL)
            .property("type", placeholder_node_type, Multiplicity.REQUIRED)
            .property(
                "message",
                LionCoreBuiltins.get_string(LionWebVersion.V2023_1),
                Multiplicity.REQUIRED,
            )
        )

        common_element = factory.interface("CommonElement")
        factory.interface("BehaviorDeclaration", extends=[common_element])
        factory.interface("Documentation", extends=[common_element])
        factory.interface("EntityDeclaration", extends=[common_element])
        factory.interface("EntityGroupDeclaration", extends=[common_element])
        factory.interface("Expression", extends=[common_element])
        factory.interface("Parameter", extends=[common_element])
        factory.interface("PlaceholderElement", extends=[common_element])
        factory.interface("Statement", extends=[common_element])
        factory.interface("TypeAnnotation", extends=[common_element])

        issue_type = factory.enumeration(
            "IssueType", ["LEXICAL", "SYNTACTIC", "SEMANTIC", "TRANSLATION"]
        )
        issue_severity = factory.enumeration(
            "IssueSeverity", ["ERROR", "WARNING", "INFO"]
        )

        (
            factory.concept("Issue")
            .property("message", LionCoreBuiltins.get_string(LionWebVersion.V2023_1))
            .property("type", issue_type)
            .property("severity", issue_severity)
            .property("position", position, Multiplicity.OPTIONAL)
        )

        language = factory.build()
        self.assertEqual(LionWebVersion.V2023_1, language.get_lionweb_version())
        self.assertEqual("com.strumenta.StarLasu", language.name)
        self.assertEqual("com-strumenta-StarLasu", language.id)
        self.assertEqual("com_strumenta_starlasu", language.key)
        self.assertEqual("1", language.version)

        self.assertEqual(19, len(language.elements))

        c = language.get_concept_by_name("ASTNode")
        self.assertEqual("ASTNode", c.name)
        self.assertEqual("com-strumenta-StarLasu_ASTNode", c.id)
        self.assertEqual("com_strumenta_starlasu_ASTNode", c.key)
        self.assertEqual(False, c.abstract)
        self.assertEqual(False, c.partition)
        self.assertEqual(3, len(c.features))

        p = c.get_property_by_name("position")
        self.assertEqual("position", p.name)
        self.assertEqual("com-strumenta-StarLasu_ASTNode_position", p.id)
        self.assertEqual("com_strumenta_starlasu_ASTNode_position", p.key)
        self.assertEqual(True, p.optional)
        self.assertIs(language.get_primitive_type_by_name("Position"), p.type)

        r = c.get_reference_by_name("originalNode")
        self.assertEqual("originalNode", r.name)
        self.assertEqual("com-strumenta-StarLasu_ASTNode_originalNode", r.id)
        self.assertEqual("com_strumenta_starlasu_ASTNode_originalNode", r.key)
        self.assertEqual(True, r.optional)
        self.assertEqual(False, r.multiple)
        self.assertIs(c, r.type)

        r = c.get_reference_by_name("transpiledNodes")
        self.assertEqual("transpiledNodes", r.name)
        self.assertEqual("com-strumenta-StarLasu_ASTNode_transpiledNodes", r.id)
        self.assertEqual("com_strumenta_starlasu_ASTNode_transpiledNodes", r.key)
        self.assertEqual(True, r.optional)
        self.assertEqual(True, r.multiple)
        self.assertIs(c, r.type)

        pt = language.get_primitive_type_by_name("Point")
        self.assertEqual("Point", pt.name)
        self.assertEqual("com-strumenta-StarLasu_Point", pt.id)
        self.assertEqual("com_strumenta_starlasu_Point", pt.key)

        pt = language.get_primitive_type_by_name("Position")
        self.assertEqual("Position", pt.name)
        self.assertEqual("com-strumenta-StarLasu_Position", pt.id)
        self.assertEqual("com_strumenta_starlasu_Position", pt.key)

        pt = language.get_primitive_type_by_name("Char")
        self.assertEqual("Char", pt.name)
        self.assertEqual("com-strumenta-StarLasu_Char", pt.id)
        self.assertEqual("com_strumenta_starlasu_Char", pt.key)

        e = language.get_enumeration_by_name("PlaceholderNodeType")
        self.assertEqual(2, len(e.literals))
        self.assertEqual(
            "com-strumenta-StarLasu_PlaceholderNodeType_MissingASTTransformation",
            e.get_literal_by_name("MissingASTTransformation").id,
        )
        self.assertEqual(
            "com-strumenta-StarLasu_PlaceholderNodeType_FailingASTTransformation",
            e.get_literal_by_name("FailingASTTransformation").id,
        )

        a = language.get_annotation_by_name("PlaceholderNode")
        self.assertEqual(LionCore.get_concept(LionWebVersion.V2023_1), a.annotates)

        r = a.get_reference_by_name("originalNode")
        self.assertEqual(True, r.optional)
        self.assertEqual(False, r.multiple)
        self.assertIs(language.get_concept_by_name("ASTNode"), r.type)

        p = a.get_property_by_name("type")
        self.assertEqual(False, p.optional)
        self.assertEqual(
            language.get_enumeration_by_name("PlaceholderNodeType"), p.type
        )

        p = a.get_property_by_name("message")
        self.assertEqual(False, p.optional)
        self.assertEqual(LionCoreBuiltins.get_string(LionWebVersion.V2023_1), p.type)

        i = language.get_interface_by_name("CommonElement")
        self.assertEqual([], i.extended_interfaces)

        i = language.get_interface_by_name("BehaviorDeclaration")
        self.assertEqual(
            [language.get_interface_by_name("CommonElement")],
            i.extended_interfaces,
        )

        e = language.get_enumeration_by_name("IssueType")
        self.assertEqual(4, len(e.literals))

        e = language.get_enumeration_by_name("IssueSeverity")
        self.assertEqual(3, len(e.literals))

        c = language.get_concept_by_name("Issue")
        p = c.get_property_by_name("type")
        self.assertEqual(False, p.optional)
        self.assertEqual(language.get_enumeration_by_name("IssueType"), p.type)
        p = c.get_property_by_name("message")
        self.assertEqual(False, p.optional)
        self.assertEqual(LionCoreBuiltins.get_string(LionWebVersion.V2023_1), p.type)
        p = c.get_property_by_name("severity")
        self.assertEqual(False, p.optional)
        self.assertEqual(language.get_enumeration_by_name("IssueSeverity"), p.type)
        p = c.get_property_by_name("position")
        self.assertEqual(True, p.optional)
        self.assertEqual(language.get_primitive_type_by_name("Position"), p.type)


if __name__ == "__main__":
    unittest.main()
