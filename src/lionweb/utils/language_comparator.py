from typing import Optional, cast

from lionweb.utils.model_comparator import ComparisonResult

from lionweb.language.classifier import Classifier
from lionweb.model import ClassifierInstance
from lionweb.model.annotation_instance import AnnotationInstance
from lionweb.model.node import Node
from lionweb.model.reference_value import ReferenceValue


class LanguageComparator:
    def compare(self, node_a: Node, node_b: Node):
        comparison_result = ComparisonResult()
        self._compare_nodes(node_a, node_b, comparison_result, "<root>")
        return comparison_result

    def _compare_properties(
        self,
        concept: Classifier,
        node_a: ClassifierInstance,
        node_b: ClassifierInstance,
        comparison_result: ComparisonResult,
        context: str,
    ):
        for property in concept.all_properties():
            value_a = node_a.get_property_value(property=property)
            value_b = node_b.get_property_value(property=property)
            if value_a != value_b:
                comparison_result.mark_different_property_value(
                    context,
                    cast(str, node_a.id),
                    property.qualified_name(),
                    value_a,
                    value_b,
                )

    def _compare_references(
        self,
        concept: Classifier,
        node_a: ClassifierInstance,
        node_b: ClassifierInstance,
        comparison_result: ComparisonResult,
        context: str,
    ):
        for reference in concept.all_references():
            value_a = node_a.get_reference_values(reference)
            value_b = node_b.get_reference_values(reference)
            if len(value_a) != len(value_b):
                comparison_result.mark_different_number_of_references(
                    context,
                    cast(str, node_a.id),
                    reference.qualified_name(),
                    len(value_a),
                    len(value_b),
                )
            else:
                for i, (ref_a, ref_b) in enumerate(zip(value_a, value_b)):
                    if not isinstance(ref_a, ReferenceValue):
                        raise ValueError()
                    if not isinstance(ref_b, ReferenceValue):
                        raise ValueError()
                    if ref_a.get_referred_id() != ref_b.get_referred_id():
                        comparison_result.mark_different_referred_id(
                            context,
                            cast(str, node_a.id),
                            reference.qualified_name(),
                            i,
                            ref_a.get_referred_id(),
                            ref_b.get_referred_id(),
                        )
                    if ref_a.resolve_info != ref_b.resolve_info:
                        comparison_result.mark_different_resolve_info(
                            context,
                            cast(str, node_a.id),
                            reference.qualified_name(),
                            i,
                            ref_a.resolve_info,
                            ref_b.resolve_info,
                        )

    def _compare_containments(
        self,
        concept: Classifier,
        node_a: ClassifierInstance,
        node_b: ClassifierInstance,
        comparison_result: ComparisonResult,
        context: str,
    ):
        for containment in concept.all_containments():
            value_a = node_a.get_children(containment)
            value_b = node_b.get_children(containment)
            if len(value_a) != len(value_b):
                comparison_result.mark_different_number_of_children(
                    context,
                    cast(str, node_a.id),
                    containment.qualified_name(),
                    len(value_a),
                    len(value_b),
                )
            else:
                for i, (child_a, child_b) in enumerate(zip(value_a, value_b)):
                    self._compare_nodes(
                        child_a,
                        child_b,
                        comparison_result,
                        f"{context}/{containment.get_name()}[{i}]",
                    )

    def _compare_annotations(
        self,
        concept: Classifier,
        node_a: ClassifierInstance,
        node_b: ClassifierInstance,
        comparison_result: ComparisonResult,
        context: str,
    ):
        if len(node_a.get_annotations()) != len(node_b.get_annotations()):
            comparison_result.mark_different_number_of_annotations(
                context, len(node_a.get_annotations()), len(node_b.get_annotations())
            )
        for i, (a, b) in enumerate(
            zip(node_a.get_annotations(), node_b.get_annotations())
        ):
            if a.id != b.id:
                comparison_result.mark_different_annotation(context, i)

    def _compare_nodes(
        self,
        node_a: Node,
        node_b: Node,
        comparison_result: ComparisonResult,
        context: str,
    ):
        if node_a.id != node_b.id:
            comparison_result.mark_different_ids(
                context, cast(str, node_a.id), cast(str, node_b.id)
            )
        else:
            if node_a.get_classifier().id == node_b.get_classifier().id:
                concept = node_a.get_classifier()
                self._compare_properties(
                    concept, node_a, node_b, comparison_result, context
                )
                self._compare_references(
                    concept, node_a, node_b, comparison_result, context
                )
                self._compare_containments(
                    concept, node_a, node_b, comparison_result, context
                )
                self._compare_annotations(
                    concept, node_a, node_b, comparison_result, context
                )
            else:
                comparison_result.mark_different_concept(
                    context,
                    cast(str, node_a.id),
                    cast(str, node_a.get_classifier().id),
                    cast(str, node_b.get_classifier().id),
                )

    def _compare_annotation_instances(
        self,
        node_a: AnnotationInstance,
        node_b: AnnotationInstance,
        comparison_result: ComparisonResult,
        context: str,
    ):
        if node_a.id != node_b.id:
            comparison_result.mark_different_ids(
                context, cast(str, node_a.id), cast(str, node_b.id)
            )
        else:
            if (
                node_a.get_annotation_definition().id
                == node_b.get_annotation_definition().id
            ):
                concept = node_a.get_annotation_definition()
                if (
                    cast(Node, node_a.get_parent()).id
                    != cast(Node, node_b.get_parent()).id
                ):
                    comparison_result.mark_different_annotated(
                        context, cast(str, node_a.id), cast(str, node_b.id)
                    )

                self._compare_properties(
                    concept, node_a, node_b, comparison_result, context
                )
                self._compare_references(
                    concept, node_a, node_b, comparison_result, context
                )
                self._compare_containments(
                    concept, node_a, node_b, comparison_result, context
                )
                self._compare_annotations(
                    concept, node_a, node_b, comparison_result, context
                )
            else:
                comparison_result.mark_different_concept(
                    context,
                    cast(str, node_a.id),
                    cast(str, node_a.get_classifier().id),
                    cast(str, node_b.get_classifier().id),
                )
