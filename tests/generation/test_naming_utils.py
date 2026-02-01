import ast
import unittest
from unittest.mock import Mock

from lionweb.generation.naming_utils import (calculate_field_name,
                                             dotted_name_expr, to_snake_case,
                                             to_type_name, to_var_name)
from lionweb.language import Feature


class TestDottedNameExpr(unittest.TestCase):
    def test_single_name(self):
        result = dotted_name_expr("foo")
        self.assertIsInstance(result, ast.Name)
        self.assertEqual(result.id, "foo")

    def test_dotted_name(self):
        result = dotted_name_expr("foo.bar.baz")
        self.assertIsInstance(result, ast.Attribute)
        self.assertEqual(result.attr, "baz")
        self.assertIsInstance(result.value, ast.Attribute)
        self.assertEqual(result.value.attr, "bar")
        self.assertIsInstance(result.value.value, ast.Name)
        self.assertEqual(result.value.value.id, "foo")

    def test_empty_string(self):
        with self.assertRaises(ValueError) as cm:
            dotted_name_expr("")
        self.assertIn("Invalid dotted name", str(cm.exception))

    def test_empty_part(self):
        with self.assertRaises(ValueError) as cm:
            dotted_name_expr("foo..bar")
        self.assertIn("Invalid dotted name", str(cm.exception))

    def test_trailing_dot(self):
        with self.assertRaises(ValueError) as cm:
            dotted_name_expr("foo.bar.")
        self.assertIn("Invalid dotted name", str(cm.exception))


class TestCalculateFieldName(unittest.TestCase):
    def test_normal_field_name(self):
        feature = Mock(spec=Feature)
        feature.get_name.return_value = "myField"
        result = calculate_field_name(feature)
        self.assertEqual(result, "myField")

    def test_keyword_field_name(self):
        feature = Mock(spec=Feature)
        feature.get_name.return_value = "class"
        result = calculate_field_name(feature)
        self.assertEqual(result, "class_")

    def test_multiple_keywords(self):
        keywords = ["if", "else", "for", "while", "import", "return", "def", "class"]
        for kw in keywords:
            feature = Mock(spec=Feature)
            feature.get_name.return_value = kw
            result = calculate_field_name(feature)
            self.assertEqual(result, f"{kw}_")


class TestToSnakeCase(unittest.TestCase):
    def test_camel_case(self):
        self.assertEqual(to_snake_case("CamelCase"), "camel_case")

    def test_pascal_case(self):
        self.assertEqual(to_snake_case("PascalCase"), "pascal_case")

    def test_mixed_case(self):
        self.assertEqual(to_snake_case("XMLParser"), "xml_parser")

    def test_already_snake_case(self):
        self.assertEqual(to_snake_case("snake_case"), "snake_case")

    def test_single_word(self):
        self.assertEqual(to_snake_case("word"), "word")

    def test_uppercase_word(self):
        self.assertEqual(to_snake_case("WORD"), "word")

    def test_multiple_consecutive_capitals(self):
        self.assertEqual(to_snake_case("HTTPResponse"), "http_response")

    def test_with_numbers(self):
        self.assertEqual(to_snake_case("value123ABC"), "value123_abc")

    def test_none_value(self):
        with self.assertRaises(ValueError) as cm:
            to_snake_case(None)
        self.assertIn("Name should not be None", str(cm.exception))

    def test_empty_string(self):
        with self.assertRaises(ValueError) as cm:
            to_snake_case("")
        self.assertIn("Name should not be None", str(cm.exception))


class TestToVarName(unittest.TestCase):
    def test_camel_case(self):
        self.assertEqual(to_var_name("CamelCase"), "camel_case")

    def test_pascal_case(self):
        self.assertEqual(to_var_name("PascalCase"), "pascal_case")

    def test_already_snake_case(self):
        self.assertEqual(to_var_name("snake_case"), "snake_case")

    def test_keyword_conversion(self):
        self.assertEqual(to_var_name("Class"), "class_")
        self.assertEqual(to_var_name("For"), "for_")
        self.assertEqual(to_var_name("If"), "if_")

    def test_non_keyword(self):
        self.assertEqual(to_var_name("MyVariable"), "my_variable")

    def test_with_numbers(self):
        self.assertEqual(to_var_name("value123ABC"), "value123_abc")

    def test_single_word(self):
        self.assertEqual(to_var_name("word"), "word")

    def test_none_value(self):
        with self.assertRaises(ValueError) as cm:
            to_var_name(None)
        self.assertIn("Name should not be None", str(cm.exception))

    def test_mixed_case_with_acronym(self):
        self.assertEqual(to_var_name("XMLParser"), "xml_parser")


class TestToTypeName(unittest.TestCase):
    def test_lowercase_word(self):
        self.assertEqual(to_type_name("mytype"), "Mytype")

    def test_camel_case(self):
        self.assertEqual(to_type_name("camelCase"), "CamelCase")

    def test_already_capitalized(self):
        self.assertEqual(to_type_name("MyType"), "MyType")

    def test_single_character(self):
        self.assertEqual(to_type_name("a"), "A")

    def test_uppercase_word(self):
        self.assertEqual(to_type_name("TYPE"), "TYPE")

    def test_none_value(self):
        with self.assertRaises(ValueError) as cm:
            to_type_name(None)
        self.assertIn("Name should not be None", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
