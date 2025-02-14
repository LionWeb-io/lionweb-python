import unittest

from lionwebpython.language.enumeration import Enumeration
from lionwebpython.language.enumeration_literal import EnumerationLiteral


class EnumerationTest(unittest.TestCase):

    def test_literal_parent_is_enum_constructor(self):
        enm = Enumeration()
        enm.set_name("MyEnum")

        lit = EnumerationLiteral(enumeration=enm, name="Lit1")

        self.assertIs(enm, lit.get_parent())
        self.assertIs(enm, lit.get_enumeration())

    def test_literal_parent_is_enum_set_parent(self):
        enm = Enumeration()
        enm.set_name("MyEnum")

        lit = EnumerationLiteral()
        lit.set_parent(enm)

        self.assertIs(enm, lit.get_parent())
        self.assertIs(enm, lit.get_enumeration())

    def test_literal_parent_is_enum_set_enumeration(self):
        enm = Enumeration()
        enm.set_name("MyEnum")

        lit = EnumerationLiteral()
        lit.set_enumeration(enm)

        self.assertIs(enm, lit.get_parent())
        self.assertIs(enm, lit.get_enumeration())


if __name__ == "__main__":
    unittest.main()
