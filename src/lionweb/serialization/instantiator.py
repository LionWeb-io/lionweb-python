from typing import TYPE_CHECKING, Callable, Dict

from lionweb.language.enumeration import Enumeration
from lionweb.language.enumeration_literal import EnumerationLiteral
from lionweb.language.field import Field
from lionweb.language.primitive_type import PrimitiveType
from lionweb.language.reference import Reference
from lionweb.language.structured_data_type import StructuredDataType
from lionweb.model.impl.dynamic_annotation_instance import \
    DynamicAnnotationInstance
from lionweb.self.lioncore import LionCore

if TYPE_CHECKING:
    from lionweb.model.node import Node
    from lionweb.serialization.data.serialized_classifier_instance import \
        SerializedClassifierInstance


class Instantiator:
    class ClassifierSpecificInstantiator:
        def instantiate(
            self,
            classifier,
            serialized_instance,
            deserialized_instances_by_id,
            properties_values,
        ):
            raise NotImplementedError

    def __init__(self):
        self.custom_deserializers: Dict[str, Callable] = {}
        self.default_node_deserializer = lambda classifier, serialized_node, deserialized_instances_by_id, properties_values: Exception(
            f"Unable to instantiate instance with classifier {classifier}"
        )

    def enable_dynamic_nodes(self):
        from lionweb.language import Annotation, Concept
        from lionweb.model.impl.dynamic_node import DynamicNode

        self.default_node_deserializer = lambda classifier, serialized_node, deserialized_instances_by_id, properties_values: (
            DynamicNode(serialized_node.id, classifier)
            if isinstance(classifier, Concept)
            else (
                DynamicAnnotationInstance(serialized_node.id, classifier)
                if isinstance(classifier, Annotation)
                else Exception("Unsupported classifier type")
            )
        )
        return self

    def instantiate(
        self,
        classifier,
        serialized_instance: "SerializedClassifierInstance",
        deserialized_instances_by_id,
        properties_values,
    ) -> "Node":
        if classifier.id in self.custom_deserializers:
            res = self.custom_deserializers[classifier.id](
                classifier,
                serialized_instance,
                deserialized_instances_by_id,
                properties_values,
            )
            if isinstance(res, Exception):
                raise res
            return res
        res = self.default_node_deserializer(
            classifier,
            serialized_instance,
            deserialized_instances_by_id,
            properties_values,
        )
        if isinstance(res, Exception):
            raise res
        return res

    def register_custom_deserializer(self, classifier_id, deserializer):
        self.custom_deserializers[classifier_id] = deserializer
        return self

    def register_lioncore_custom_deserializers(self, lion_web_version):
        from lionweb.language import (Annotation, Concept, Containment,
                                      Interface, Language, Property)

        self.custom_deserializers.update(
            {
                LionCore.get_language(lion_web_version)
                .id: lambda c, s, d, p: Language(lion_web_version=lion_web_version)
                .set_id(s.id),
                LionCore.get_concept(lion_web_version)
                .id: lambda c, s, d, p: Concept(lion_web_version=lion_web_version)
                .set_id(s.id),
                LionCore.get_interface(lion_web_version)
                .id: lambda c, s, d, p: Interface(lion_web_version=lion_web_version)
                .set_id(s.id),
                LionCore.get_property(lion_web_version).id: lambda c, s, d, p: Property(
                    lion_web_version=lion_web_version, id=s.id
                ),
                LionCore.get_reference(
                    lion_web_version
                ).id: lambda c, s, d, p: Reference(
                    lion_web_version=lion_web_version, id=s.id
                ),
                LionCore.get_containment(
                    lion_web_version
                ).id: lambda c, s, d, p: Containment(
                    lion_web_version=lion_web_version, id=s.id
                ),
                LionCore.get_primitive_type(
                    lion_web_version
                ).id: lambda c, s, d, p: PrimitiveType(
                    lion_web_version=lion_web_version, id=s.id
                ),
                LionCore.get_enumeration(lion_web_version)
                .id: lambda c, s, d, p: Enumeration(lion_web_version=lion_web_version)
                .set_id(s.id),
                LionCore.get_enumeration_literal(lion_web_version)
                .id: lambda c, s, d, p: EnumerationLiteral(
                    lion_web_version=lion_web_version
                )
                .set_id(s.id),
                LionCore.get_annotation(lion_web_version)
                .id: lambda c, s, d, p: Annotation(lion_web_version=lion_web_version)
                .set_id(s.id),
                LionCore.get_structured_data_type().id: lambda c, s, d, p: StructuredDataType(
                    id=s.id
                ),
                LionCore.get_field().id: lambda c, s, d, p: Field(id=s.id),
            }
        )
