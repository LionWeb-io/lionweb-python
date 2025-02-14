from lionwebpython.model.classifier_instance_utils import \
    ClassifierInstanceUtils
from lionwebpython.model.node import Node
from lionwebpython.utils.common_checks import CommonChecks
from lionwebpython.utils.validation_result import ValidationResult
from lionwebpython.utils.validator import Validator


class NodeTreeValidator(Validator):
    def validate(self, element: Node) -> ValidationResult:
        validation_result = ValidationResult()
        self._validate_node_and_descendants(element, validation_result)
        self._validate_ids_are_unique(element, validation_result)
        return validation_result

    def _validate_node_and_descendants(
        self, node: Node, validation_result: ValidationResult
    ) -> None:
        if node.get_id() is not None:
            # It does not make sense to make the same ID as null and invalid
            validation_result.check_for_error(
                not CommonChecks.is_valid_id(node.get_id()), "Invalid ID", node
            )

        if node.is_root():
            validation_result.check_for_error(
                not node.get_classifier().is_partition(),
                "A root node should be an instance of a Partition concept",
                node,
            )

        for containment in node.get_classifier().all_containments():
            actual_n_children = len(node.get_children(containment))
            validation_result.check_for_error(
                containment.is_required() and actual_n_children == 0,
                f"Containment {containment.get_name()} is required but no children are specified",
                node,
            )
            validation_result.check_for_error(
                containment.is_single() and actual_n_children > 1,
                f"Containment {containment.get_name()} is single but it has {actual_n_children} children",
                node,
            )

        for child in ClassifierInstanceUtils.get_children(node):
            self._validate_node_and_descendants(child, validation_result)

    def _validate_ids_are_unique(self, node: Node, result: ValidationResult) -> None:
        unique_ids: dict[str, Node] = {}
        for n in node.this_and_all_descendants():
            node_id = n.get_id()
            if node_id is not None:
                if node_id in unique_ids:
                    result.add_error(
                        f"ID {node_id} is duplicate. It is also used by {unique_ids[node_id]}",
                        n,
                    )
                else:
                    unique_ids[node_id] = n
            else:
                result.add_error("ID null found", n)
