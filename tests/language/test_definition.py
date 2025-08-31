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
            .property("type", placeholder_node_type, Multiplicity.OPTIONAL)
            .property(
                "message",
                LionCoreBuiltins.get_string(LionWebVersion.V2023_1),
                Multiplicity.OPTIONAL,
            )
        )

        common_element = factory.interface("CommonElement")
        factory.interface("BehaviorDeclaration", extends=common_element)
        factory.interface("Documentation", extends=common_element)
        factory.interface("EntityDeclaration", extends=common_element)
        factory.interface("EntityGroupDeclaration", extends=common_element)
        factory.interface("Expression", extends=common_element)
        factory.interface("Parameter", extends=common_element)
        factory.interface("PlaceholderElement", extends=common_element)
        factory.interface("Statement", extends=common_element)
        factory.interface("TypeAnnotation", extends=common_element)

        factory.enumeration(
            "IssueType", ["LEXICAL", "SYNTACTIC", "SEMANTIC", "TRANSLATION"]
        )

        factory.concept("Issue")

        language = factory.build()
        self.assertEqual(LionWebVersion.V2023_1, language.get_lionweb_version())
        self.assertEqual("com.strumenta.StarLasu", language.get_name())
        self.assertEqual("com-strumenta-StarLasu", language.get_id())
        self.assertEqual("com_strumenta_starlasu", language.get_key())

        # self.assertEqual(4, len(language.get_elements()))

        c = language.get_concept_by_name("ASTNode")
        self.assertEqual("ASTNode", c.get_name())
        self.assertEqual("com-strumenta-StarLasu_ASTNode", c.get_id())
        self.assertEqual("com_strumenta_starlasu_ASTNode", c.get_key())
        self.assertEqual(False, c.is_abstract())
        self.assertEqual(False, c.is_partition())
        self.assertEqual(3, len(c.get_features()))

        p = c.get_property_by_name("position")
        self.assertEqual("position", p.get_name())
        self.assertEqual("com-strumenta-StarLasu_ASTNode_position", p.get_id())
        self.assertEqual("com_strumenta_starlasu_ASTNode_position", p.get_key())
        self.assertEqual(True, p.is_optional())
        self.assertIs(language.get_primitive_type_by_name("Position"), p.type)

        r = c.get_reference_by_name("originalNode")
        self.assertEqual("originalNode", r.get_name())
        self.assertEqual("com-strumenta-StarLasu_ASTNode_originalNode", r.get_id())
        self.assertEqual("com_strumenta_starlasu_ASTNode_originalNode", r.get_key())
        self.assertEqual(True, r.is_optional())
        self.assertEqual(False, r.is_multiple())
        self.assertIs(c, r.get_type())

        r = c.get_reference_by_name("transpiledNodes")
        self.assertEqual("transpiledNodes", r.get_name())
        self.assertEqual("com-strumenta-StarLasu_ASTNode_transpiledNodes", r.get_id())
        self.assertEqual("com_strumenta_starlasu_ASTNode_transpiledNodes", r.get_key())
        self.assertEqual(True, r.is_optional())
        self.assertEqual(True, r.is_multiple())
        self.assertIs(c, r.get_type())

        pt = language.get_primitive_type_by_name("Point")
        self.assertEqual("Point", pt.get_name())
        self.assertEqual("com-strumenta-StarLasu_Point", pt.get_id())
        self.assertEqual("com_strumenta_starlasu_Point", pt.get_key())

        pt = language.get_primitive_type_by_name("Position")
        self.assertEqual("Position", pt.get_name())
        self.assertEqual("com-strumenta-StarLasu_Position", pt.get_id())
        self.assertEqual("com_strumenta_starlasu_Position", pt.get_key())

        pt = language.get_primitive_type_by_name("Char")
        self.assertEqual("Char", pt.get_name())
        self.assertEqual("com-strumenta-StarLasu_Char", pt.get_id())
        self.assertEqual("com_strumenta_starlasu_Char", pt.get_key())

        e = language.get_enumeration_by_name("PlaceholderNodeType")

        a = language.get_annotation_by_name("PlaceholderNode")
        self.assertEqual(LionCore.get_concept(LionWebVersion.V2023_1), a.get_annotates())


if __name__ == "__main__":
    unittest.main()
