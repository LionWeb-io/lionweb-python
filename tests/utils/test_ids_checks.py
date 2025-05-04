import unittest

from lionweb.utils import is_valid_id


class TestIDsCheck(unittest.TestCase):

    def test_positive_case(self):
        self.assertTrue(is_valid_id("foo"))

    def test_empty_id_is_invalid(self):
        self.assertFalse(is_valid_id(""))

    def test_ids_with_umlauts_are_invalid(self):
        self.assertFalse(is_valid_id("foö"))

    def test_ids_with_accents_are_invalid(self):
        self.assertFalse(is_valid_id("foò"))
        self.assertFalse(is_valid_id("foó"))


if __name__ == "__main__":
    unittest.main()
