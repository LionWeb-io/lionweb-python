import unittest

from lionwebpython.language.language import Language


class LanguageTest(unittest.TestCase):

    def test_add_dependency(self):
        m1 = Language("m1")
        m2 = Language("m2")
        m3 = Language("m3")

        self.assertEqual([], m1.depends_on())
        m1.add_dependency(m2)
        self.assertEqual([m2], m1.depends_on())
        m1.add_dependency(m3)
        self.assertEqual([m2, m3], m1.depends_on())


if __name__ == "__main__":
    unittest.main()
