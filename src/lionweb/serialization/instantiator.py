from collections.abc import Callable
from typing import TYPE_CHECKING

from lionweb.language.enumeration import Enumeration
from lionweb.language.enumeration_literal import EnumerationLiteral
from lionweb.language.field import Field
from lionweb.language.primitive_type import PrimitiveType
from lionweb.language.reference import Reference
from lionweb.language.structured_data_type import StructuredDataType
from lionweb.model.impl.dynamic_annotation_instance import DynamicAnnotationInstance

if TYPE_CHECKING:
    from lionweb.lionweb_version import LionWebVersion
    from lionweb.model.node import Node
    from lionweb.serialization.data.serialized_classifier_instance import (
        SerializedClassifierInstance,
    )


class InstantiationError(Exception):
    """Raised when no deserializer is able to instantiate a node for a given classifier.

    Args:
        classifier: The classifier for which instantiation failed.
    """

    def __init__(self, classifier):
        super().__init__(f"Unable to instantiate instance with classifier {classifier}")
        self.classifier = classifier


class Instantiator:
    """Creates deserialized node instances from their serialized form.

    Instantiation can be customized per-classifier via
    :meth:`register_custom_deserializer`, or a default dynamic-node based
    deserializer can be enabled via :meth:`enable_dynamic_nodes`.
    """

    class ClassifierSpecificInstantiator:
        def instantiate(
            self,
            classifier,
            serialized_instance,
            deserialized_instances_by_id,
            properties_values,
        ):
            raise NotImplementedError

    def __init__(self) -> None:
        self.custom_deserializers: dict[str, Callable] = {}
        self.default_node_deserializer = (
            lambda classifier, serialized_node, deserialized_instances_by_id, properties_values: (
                InstantiationError(classifier)
            )
        )

    def enable_dynamic_nodes(self) -> "Instantiator":
        """Enable a default deserializer that produces dynamic nodes/annotation instances.

        Returns:
            This instantiator, to allow chaining.
        """
        from lionweb.language import Annotation, Concept
        from lionweb.model.impl.dynamic_node import DynamicNode

        self.default_node_deserializer = (
            lambda classifier, serialized_node, deserialized_instances_by_id, properties_values: (
                DynamicNode(serialized_node.id, classifier)
                if isinstance(classifier, Concept)
                else (
                    DynamicAnnotationInstance(serialized_node.id, classifier)
                    if isinstance(classifier, Annotation)
                    else Exception("Unsupported classifier type")
                )
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
        """Instantiate a node from its serialized form using the registered deserializers.

        Args:
            classifier: The classifier (concept or annotation) of the instance.
            serialized_instance: The serialized classifier instance to instantiate from.
            deserialized_instances_by_id: Already-deserialized instances, keyed by ID.
            properties_values: The deserialized property values, keyed by property.

        Returns:
            The instantiated node.

        Raises:
            Exception: Whatever exception (e.g. :class:`InstantiationError`) the
                resolved deserializer produces when it cannot instantiate the node.
        """
        if classifier.id in self.custom_deserializers:
            res = self.custom_deserializers[classifier.id](
                classifier,
                serialized_instance,
                deserialized_instances_by_id,
                properties_values,
            )
        else:
            res = self.default_node_deserializer(
                classifier,
                serialized_instance,
                deserialized_instances_by_id,
                properties_values,
            )
        if isinstance(res, Exception):
            raise res
        return res

    def register_custom_deserializer(self, classifier_id, deserializer) -> "Instantiator":
        """Register a custom deserializer for a specific classifier ID.

        Args:
            classifier_id: The ID of the classifier the deserializer handles.
            deserializer: A callable producing a node from
                ``(classifier, serialized_instance, deserialized_instances_by_id, properties_values)``.

        Returns:
            This instantiator, to allow chaining.
        """
        self.custom_deserializers[classifier_id] = deserializer
        return self

    def register_lioncore_custom_deserializers(self, lion_web_version: "LionWebVersion") -> None:
        """Register custom deserializers for all LionCore meta-language elements.

        Args:
            lion_web_version: The LionWeb version whose LionCore elements should be handled.
        """
        from lionweb.language import Annotation, Concept, Containment, Interface, Language, Property
        from lionweb.self.lioncore import LionCore

        self.custom_deserializers.update(
            {
                LionCore.get_language(lion_web_version).id: lambda c, s, d, p: Language(
                    lion_web_version=lion_web_version
                ).set_id(s.id),
                LionCore.get_concept(lion_web_version).id: lambda c, s, d, p: Concept(
                    lion_web_version=lion_web_version
                ).set_id(s.id),
                LionCore.get_interface(lion_web_version).id: lambda c, s, d, p: Interface(
                    lion_web_version=lion_web_version
                ).set_id(s.id),
                LionCore.get_property(lion_web_version).id: lambda c, s, d, p: Property(
                    lion_web_version=lion_web_version, id=s.id
                ),
                LionCore.get_reference(lion_web_version).id: lambda c, s, d, p: Reference(
                    lion_web_version=lion_web_version, id=s.id
                ),
                LionCore.get_containment(lion_web_version).id: lambda c, s, d, p: Containment(
                    lion_web_version=lion_web_version, id=s.id
                ),
                LionCore.get_primitive_type(lion_web_version).id: lambda c, s, d, p: PrimitiveType(
                    lion_web_version=lion_web_version, id=s.id
                ),
                LionCore.get_enumeration(lion_web_version).id: lambda c, s, d, p: Enumeration(
                    lion_web_version=lion_web_version
                ).set_id(s.id),
                LionCore.get_enumeration_literal(lion_web_version).id: lambda c, s, d, p: (
                    EnumerationLiteral(lion_web_version=lion_web_version).set_id(s.id)
                ),
                LionCore.get_annotation(lion_web_version).id: lambda c, s, d, p: Annotation(
                    lion_web_version=lion_web_version
                ).set_id(s.id),
                LionCore.get_structured_data_type().id: lambda c, s, d, p: StructuredDataType(
                    id=s.id
                ),
                LionCore.get_field().id: lambda c, s, d, p: Field(id=s.id),
            }
        )
