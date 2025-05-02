import unittest

from lionweb.language.language import Language
from lionweb.model.node import Node
from lionweb.utils.language_validator import LanguageValidator
from lionweb.utils.node_tree_validator import NodeTreeValidator
from lionweb.utils.validation_result import ValidationResult


class BaseTest(unittest.TestCase):

    def assert_node_tree_is_valid(self, node: Node) -> None:
        node_tree_validator = NodeTreeValidator()
        validation_result: ValidationResult = node_tree_validator.validate(node)
        self.assertTrue(validation_result.is_successful(), str(validation_result))

    def assert_node_tree_is_not_valid(self, node: Node) -> None:
        node_tree_validator = NodeTreeValidator()
        validation_result: ValidationResult = node_tree_validator.validate(node)
        self.assertFalse(validation_result.is_successful(), str(validation_result))

    def assert_language_is_valid(self, language: Language) -> None:
        language_validator = LanguageValidator()
        validation_result: ValidationResult = language_validator.validate(language)
        self.assertTrue(validation_result.is_successful(), str(validation_result))

    def assert_language_is_not_valid(self, language: Language) -> None:
        language_validator = LanguageValidator()
        validation_result: ValidationResult = language_validator.validate(language)
        self.assertFalse(validation_result.is_successful(), str(validation_result))
