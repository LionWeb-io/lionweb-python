from typing import List, Optional, cast

from lionwebpython.language.annotation import Annotation
from lionwebpython.language.classifier import Classifier
from lionwebpython.language.concept import Concept
from lionwebpython.language.enumeration import Enumeration
from lionwebpython.language.interface import Interface
from lionwebpython.language.language import Language
from lionwebpython.language.structured_data_type import StructuredDataType
from lionwebpython.model.node import Node
from lionwebpython.utils.node_tree_validator import NodeTreeValidator
from lionwebpython.utils.validation_result import ValidationResult
from lionwebpython.utils.validator import Validator


class LanguageValidator(Validator):

    @staticmethod
    def ensure_is_valid(language: Language):
        vr = LanguageValidator().validate(language)
        if not vr.is_successful():
            raise RuntimeError(f"Invalid language: {vr.get_issues()}")

    def validate_enumeration(self, result: ValidationResult, enumeration: Enumeration):
        for lit in enumeration.get_literals():
            result.check_for_error(lit.get_name() is None, "Simple name not set", lit)
        self.validate_names_are_unique(enumeration.get_literals(), result)

    def validate_classifier(self, result: ValidationResult, classifier: Classifier):
        for feature in classifier.get_features():
            result.check_for_error(
                feature.get_name() is None, "Simple name not set", feature
            )
            result.check_for_error(
                feature.get_container() is None, "Container not set", feature
            )
            result.check_for_error(
                feature.get_container() is not None
                and isinstance(feature.get_container(), Node)
                and cast(Node, feature.get_container()).get_id() is not None
                and cast(Node, feature.get_container()).get_id() != classifier.get_id(),
                f"Features container not set correctly: set to {feature.get_container()} when {classifier} was expected",
                feature,
            )
        self.validate_names_are_unique(classifier.get_features(), result)

    def validate_concept(self, result: ValidationResult, concept: Concept):
        self.check_ancestors(concept, result)
        result.check_for_error(
            len(concept.get_implemented()) != len(set(concept.get_implemented())),
            "The same interface has been implemented multiple times",
            concept,
        )

    @staticmethod
    def is_circular(structured_data_type: StructuredDataType) -> bool:
        circular_sdt = set()
        visited = set()
        to_visit = [structured_data_type]

        while to_visit:
            sdt = to_visit.pop()
            visited.add(sdt)
            for field in sdt.get_fields():
                type = field.get_type()
                if isinstance(type, StructuredDataType):
                    new_sdt = type
                    if new_sdt in visited:
                        circular_sdt.add(new_sdt)
                    elif new_sdt is not None:
                        to_visit.append(new_sdt)

        return bool(circular_sdt)

    def validate_structural_data_type(
        self, result: ValidationResult, structured_data_type: StructuredDataType
    ):
        if self.is_circular(structured_data_type):
            result.add_error(
                "Circular references are forbidden in StructuralDataFields",
                structured_data_type,
            )

    def validate(self, language: Language) -> ValidationResult:
        result = NodeTreeValidator().validate(language)
        result.check_for_error(
            language.get_name() is None, "Qualified name not set", language
        )

        self.validate_names_are_unique(language.get_elements(), result)
        self.validate_keys_are_not_null(language, result)
        self.validate_keys_are_unique(language, result)

        for el in language.get_elements():
            result.check_for_error(el.get_name() is None, "Simple name not set", el)
            result.check_for_error(
                el.get_name() == "", "Simple name set to empty string", el
            )
            result.check_for_error(el.get_language() is None, "Language not set", el)
            result.check_for_error(
                el.get_language() is not None and el.get_language() != language,
                "Language not set correctly",
                el,
            )

            if isinstance(el, Enumeration):
                self.validate_enumeration(result, el)
            if isinstance(el, Classifier):
                self.validate_classifier(result, el)
            if isinstance(el, Concept):
                self.validate_concept(result, el)
            if isinstance(el, Interface):
                self.check_interfaces_cycles(el, result)
            if isinstance(el, Annotation):
                self.check_annotates(el, result)
            if isinstance(el, StructuredDataType):
                self.validate_structural_data_type(result, el)

        return result

    def validate_names_are_unique(self, elements, result: ValidationResult):
        elements_by_name: dict[str, List[object]] = {}
        for el in elements:
            if el.get_name():
                elements_by_name.setdefault(el.get_name(), []).append(el)

        for name, entities in elements_by_name.items():
            if len(entities) > 1:
                for el in entities:
                    result.add_error(f"Duplicate name {el.get_name()}", el)

    def validate_keys_are_not_null(self, language: Language, result: ValidationResult):
        for n in language.this_and_all_descendants():
            from lionwebpython.language.ikeyed import IKeyed

            if isinstance(n, IKeyed):
                if n.get_key() is None:
                    result.add_error("Key should not be null", n)

    def validate_keys_are_unique(self, language: Language, result: ValidationResult):
        unique_keys: dict[str, Optional[str]] = {}
        for n in language.this_and_all_descendants():
            from lionwebpython.language.ikeyed import IKeyed

            if isinstance(n, IKeyed):
                key = n.get_key()
                if key:
                    if key in unique_keys:
                        result.add_error(
                            f"Key '{key}' is duplicate. It is also used by {unique_keys[key]}",
                            n,
                        )
                    else:
                        unique_keys[key] = n.get_id()

    def is_language_valid(self, language: Language) -> bool:
        return self.validate(language).is_successful()

    def check_ancestors(self, concept: Concept, validation_result: ValidationResult):
        self.check_ancestors_helper(set(), concept, validation_result, True)

    def check_annotates(
        self, annotation: Annotation, validation_result: ValidationResult
    ):
        validation_result.check_for_error(
            annotation.get_effectively_annotated() is None,
            "An annotation should specify annotates or inherit it",
            annotation,
        )
        validation_result.check_for_error(
            annotation.get_extended_annotation() is not None
            and annotation.get_annotates() is not None
            and annotation.get_annotates()
            != cast(Annotation, annotation.get_extended_annotation()).get_annotates(),
            "When a sub annotation specifies a value for annotates, it must be the same value the super annotation specifies",
            annotation,
        )

    def check_ancestors_helper(
        self,
        already_explored,
        classifier: Classifier,
        validation_result: ValidationResult,
        examining_concept: bool,
    ):
        if isinstance(classifier, Concept):
            concept = classifier
            if concept in already_explored:
                validation_result.add_error("Cyclic hierarchy found", concept)
            else:
                already_explored.add(concept)
                extended = concept.get_extended_concept()
                if extended:
                    self.check_ancestors_helper(
                        already_explored, extended, validation_result, examining_concept
                    )
                for interf in concept.get_implemented():
                    self.check_ancestors_helper(
                        already_explored, interf, validation_result, examining_concept
                    )
        elif isinstance(classifier, Interface):
            iface = classifier
            if iface in already_explored:
                # It is ok to indirectly implement the same interface multiple times for a Concept.
                # It is instead an issue in case we are looking into interfaces.
                #
                # For example, this is fine:
                # class A extends B, implements I
                # class B implements I
                #
                # This is not fine:
                # interface I1 extends I2
                # interface I2 extends I1
                if not examining_concept:
                    validation_result.add_error("Cyclic hierarchy found", iface)
            else:
                already_explored.add(iface)
                for extended_interface in iface.get_extended_interfaces():
                    self.check_ancestors_helper(
                        already_explored,
                        extended_interface,
                        validation_result,
                        examining_concept,
                    )
        else:
            raise ValueError()

    def check_interfaces_cycles(
        self, iface: Interface, validation_result: ValidationResult
    ):
        if iface in iface.all_extended_interfaces():
            validation_result.add_error(
                "Cyclic hierarchy found: the interface extends itself", iface
            )

    def check_ancestors_helper_for_interfaces(
        self, already_explored, iface: Interface, validation_result: ValidationResult
    ):
        if iface in already_explored:
            validation_result.add_error("Cyclic hierarchy found", iface)
        else:
            already_explored.add(iface)
            for interf in iface.get_extended_interfaces():
                self.check_ancestors_helper_for_interfaces(
                    already_explored, interf, validation_result
                )
