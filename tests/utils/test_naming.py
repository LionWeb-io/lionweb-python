import unittest
from lionwebpython.utils.naming import Naming
from lionwebpython.utils.invalid_name import InvalidName


class TestNaming(unittest.TestCase):

    def test_valid_simple_name(self):
        Naming.validate_name("myID123")

    def test_invalid_simple_name_starting_with_digits(self):
        with self.assertRaises(InvalidName):
            Naming.validate_name("1myID")

    def test_valid_qualified_name(self):
        Naming.validate_qualified_name("myID123.a.b")


if __name__ == "__main__":
    unittest.main()