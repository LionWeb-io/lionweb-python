import unittest

from lionwebpython.utils.common_checks import CommonChecks


class TestIDsCheck(unittest.TestCase):

    def test_positive_case(self):
        self.assertTrue(CommonChecks.is_valid_id("foo"))

    def test_empty_id_is_invalid(self):
        self.assertFalse(CommonChecks.is_valid_id(""))

    def test_ids_with_umlauts_are_invalid(self):
        self.assertFalse(CommonChecks.is_valid_id("foö"))

    def test_ids_with_accents_are_invalid(self):
        self.assertFalse(CommonChecks.is_valid_id("foò"))
        self.assertFalse(CommonChecks.is_valid_id("foó"))


if __name__ == "__main__":
    unittest.main()
