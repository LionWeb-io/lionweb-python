import unittest

from lionwebpython.language import Containment
from lionwebpython.language.enumeration_literal import EnumerationLiteral


class M3NodeTest(unittest.TestCase):

    def test_to_string_enumeration_literal_without_id(self):
        literal = EnumerationLiteral()
        self.assertEqual(str(literal), "EnumerationLiteral[None]")

    def test_to_string_enumeration_literal_including_id(self):
        literal = EnumerationLiteral()
        literal.set_id("123")
        self.assertEqual(str(literal), "EnumerationLiteral[123]")

    def test_to_string_containment_without_id(self):
        containment = Containment()
        self.assertEqual("Containment[None]", str(containment))

    def test_to_string_containment_including_id(self):
        containment = Containment()
        containment.set_id("asdf")
        self.assertEqual("Containment[asdf]", str(containment))


if __name__ == "__main__":
    unittest.main()
