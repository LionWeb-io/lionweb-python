import unittest

from lionweb import LionWebVersion
from lionweb.language import Language, Multiplicity

from lionweb.language import LanguageFactory


class DefinitionTest(unittest.TestCase):

    def test_language_definition(self):
        factory = LanguageFactory(lw_version=LionWebVersion.V2023_1,
                                  name="com.strumenta.StarLasu",
                                  id="com-strumenta-StarLasu",
                                  key="com_strumenta_starlasu")
        factory.primitive_type("Char")
        factory.primitive_type("Point")
        position = factory.primitive_type("Position")

        ast_node = factory.concept("ASTNode")
        (ast_node
         .property("position", position, Multiplicity.OPTIONAL)
         .reference("originalNode", ast_node, Multiplicity.OPTIONAL)
         .reference("transpiledNodes", ast_node, Multiplicity.ZERO_OR_MORE))

        language = factory.build()
        self.assertEqual(LionWebVersion.V2023_1, language.get_lionweb_version())
        self.assertEqual("com.strumenta.StarLasu", language.get_name())
        self.assertEqual("com-strumenta-StarLasu", language.get_id())
        self.assertEqual("com_strumenta_starlasu", language.get_key())

        self.assertEqual(4, len(language.get_elements()))

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
        self.assertIs(language.get_primitive_type_by_name('Position'), p.type)

        r = c.get_reference_by_name("originalNode")
        self.assertEqual("originalNode", r.get_name())
        self.assertEqual("com-strumenta-StarLasu_ASTNode_originalNode", r.get_id())
        self.assertEqual("com_strumenta_starlasu_ASTNode_originalNode", r.get_key())
        self.assertEqual(True, r.is_optional())
        self.assertEqual(False, r.is_multiple())
        self.assertIs(c, r.type)

        r = c.get_reference_by_name("transpiledNodes")
        self.assertEqual("transpiledNodes", r.get_name())
        self.assertEqual("com-strumenta-StarLasu_ASTNode_transpiledNodes", r.get_id())
        self.assertEqual("com_strumenta_starlasu_ASTNode_transpiledNodes", r.get_key())
        self.assertEqual(True, r.is_optional())
        self.assertEqual(True, r.is_multiple())
        self.assertIs(c, r.type)

        pt = language.get_primitive_type_by_name('Point')
        self.assertEqual("Point", pt.get_name())
        self.assertEqual("com-strumenta-StarLasu_Point", pt.get_id())
        self.assertEqual("com_strumenta_starlasu_Point", pt.get_key())

        # TODO check primitive types


if __name__ == "__main__":
    unittest.main()
