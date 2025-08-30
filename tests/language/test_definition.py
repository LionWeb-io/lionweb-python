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


if __name__ == "__main__":
    unittest.main()
