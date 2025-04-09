from typing import TYPE_CHECKING, Dict, List

from lionwebpython.language.data_type import DataType
from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.model import ClassifierInstance
from lionwebpython.model.classifier_instance_utils import \
    ClassifierInstanceUtils
from lionwebpython.model.has_settable_parent import HasSettableParent
from lionwebpython.serialization.classifier_resolver import ClassifierResolver
from lionwebpython.serialization.data.metapointer import MetaPointer
from lionwebpython.serialization.data.serialized_chunk import SerializedChunk
from lionwebpython.serialization.data.serialized_classifier_instance import \
    SerializedClassifierInstance
from lionwebpython.serialization.data.serialized_containment_value import \
    SerializedContainmentValue
from lionwebpython.serialization.data.serialized_property_value import \
    SerializedPropertyValue
from lionwebpython.serialization.data.serialized_reference_value import (
    SerializedReferenceValue, SerializedReferenceValueEntry)
from lionwebpython.serialization.data.used_language import UsedLanguage
from lionwebpython.serialization.deserialization_exception import \
    DeserializationException
from lionwebpython.serialization.deserialization_status import \
    DeserializationStatus
from lionwebpython.serialization.instantiator import Instantiator
from lionwebpython.serialization.primitives_values_serialization import \
    PrimitiveValuesSerialization
from lionwebpython.serialization.unavailable_node_policy import \
    UnavailableNodePolicy

if TYPE_CHECKING:
    from lionwebpython.model.annotation_instance import AnnotationInstance


class AbstractSerialization:

    DEFAULT_SERIALIZATION_FORMAT = LionWebVersion.current_version()

    def __init__(
        self, lionweb_version: LionWebVersion = LionWebVersion.current_version()
    ):
        from lionwebpython.api.local_classifier_instance_resolver import \
            LocalClassifierInstanceResolver

        self.lion_web_version = lionweb_version
        self.classifier_resolver = ClassifierResolver()
        self.instantiator = Instantiator()
        self.primitive_values_serialization = PrimitiveValuesSerialization()
        self.instance_resolver = LocalClassifierInstanceResolver()
        self.unavailable_parent_policy = UnavailableNodePolicy.THROW_ERROR
        self.unavailable_children_policy = UnavailableNodePolicy.THROW_ERROR
        self.unavailable_reference_target_policy = UnavailableNodePolicy.THROW_ERROR
        self.builtins_reference_dangling = False
        self.keep_null_properties = False

    def enable_dynamic_nodes(self):
        self.instantiator.enable_dynamic_nodes()
        self.primitive_values_serialization.enable_dynamic_nodes()

    def register_language(self, language):
        self.classifier_resolver.register_language(language)
        self.primitive_values_serialization.register_language(language)

    def make_builtins_reference_dangling(self):
        self.builtins_reference_dangling = True

    def serialize_tree_to_serialization_block(self, root):
        classifier_instances = []
        self.collect_self_and_descendants(root, True, classifier_instances)
        return self.serialize_nodes_to_serialization_block(classifier_instances)

    def collect_self_and_descendants(
        self, instance: ClassifierInstance, include_self=True, collection=None
    ):
        if collection is None:
            collection = []
        if include_self:
            collection.append(instance)
        for child in instance.get_children():
            self.collect_self_and_descendants(child, True, collection)
        return collection

    def serialize_nodes_to_serialization_block(self, classifier_instances):
        serialized_chunk = SerializedChunk()
        serialized_chunk.serialization_format_version = self.lion_web_version.value

        for classifier_instance in classifier_instances:
            if classifier_instance is None:
                raise ValueError("nodes should not contain null values")

            serialized_chunk.add_classifier_instance(
                self.serialize_node(classifier_instance)
            )

            # Handle annotations
            for annotation_instance in classifier_instance.get_annotations():
                if annotation_instance not in classifier_instances:
                    serialized_chunk.add_classifier_instance(
                        self.serialize_annotation_instance(annotation_instance)
                    )
                    self._consider_language_during_serialization(
                        serialized_chunk,
                        annotation_instance.get_classifier().get_language(),
                    )

            # Validate classifier and its language
            classifier = classifier_instance.get_classifier()
            if classifier is None:
                raise ValueError(
                    "A node should have a concept in order to be serialized"
                )

            language = classifier.get_language()
            if language is None:
                raise ValueError(
                    f"A Concept should be part of a Language in order to be serialized. Concept {classifier} is not"
                )

            self._consider_language_during_serialization(serialized_chunk, language)

            # Add all features' declaring languages
            for feature in classifier.all_features():
                self._consider_language_during_serialization(
                    serialized_chunk, feature.get_declaring_language()
                )

            # Add all properties' type languages
            for prop in classifier.all_properties():
                self._consider_language_during_serialization(
                    serialized_chunk, prop.get_type().get_language()
                )

            # Add all links' type languages
            for link in classifier.all_links():
                self._consider_language_during_serialization(
                    serialized_chunk, link.get_type().get_language()
                )

        return serialized_chunk

    def _consider_language_during_serialization(self, serialized_chunk, language):
        self.register_language(language)
        used_language = UsedLanguage(language.get_key(), language.get_version())
        if used_language not in serialized_chunk.languages:
            serialized_chunk.languages.append(used_language)

    def serialize_node(
        self, classifier_instance: ClassifierInstance
    ) -> SerializedClassifierInstance:
        serialized_instance = SerializedClassifierInstance(
            classifier_instance.id,
            MetaPointer.from_language_entity(classifier_instance.get_classifier()),
        )
        parent = classifier_instance.get_parent()
        serialized_instance.parent_node_id = parent.id if parent else None
        self._serialize_properties(classifier_instance, serialized_instance)
        self._serialize_containments(classifier_instance, serialized_instance)
        self._serialize_references(classifier_instance, serialized_instance)
        self._serialize_annotations(classifier_instance, serialized_instance)
        return serialized_instance

    def serialize_annotation_instance(
        self, annotation_instance: "AnnotationInstance"
    ) -> SerializedClassifierInstance:
        if annotation_instance is None:
            raise ValueError("AnnotationInstance should not be null")

        serialized_classifier_instance = SerializedClassifierInstance(
            annotation_instance.id,
            MetaPointer.from_language_entity(
                annotation_instance.get_annotation_definition()
            ),
        )
        parent = annotation_instance.get_parent()
        serialized_classifier_instance.parent_node_id = parent.id if parent else None
        self._serialize_properties(annotation_instance, serialized_classifier_instance)
        self._serialize_containments(
            annotation_instance, serialized_classifier_instance
        )
        self._serialize_references(annotation_instance, serialized_classifier_instance)
        self._serialize_annotations(annotation_instance, serialized_classifier_instance)

        return serialized_classifier_instance

    def _serialize_properties(
        self,
        classifier_instance: ClassifierInstance,
        serialized_classifier_instance: SerializedClassifierInstance,
    ) -> None:
        for property in classifier_instance.get_classifier().all_properties():
            c = property.get_container()
            if c is None:
                raise ValueError()
            language = c.get_language()
            if language is None:
                raise ValueError()
            mp = MetaPointer.from_keyed(property, language)
            dt = property.get_type()
            if dt is None:
                raise ValueError()
            property_value = classifier_instance.get_property_value(property=property)
            if property_value is not None or self.keep_null_properties:
                serialized_property_value = SerializedPropertyValue(
                    mp,
                    self._serialize_property_value(dt, property_value),
                )
                serialized_classifier_instance.add_property_value(
                    serialized_property_value
                )

    def _serialize_property_value(self, data_type: DataType, value: object):
        if data_type is None:
            raise ValueError("Cannot serialize property when the dataType is null")
        if data_type.id is None:
            raise ValueError("Cannot serialize property when the dataType.ID is null")
        if value is None:
            return None
        return self.primitive_values_serialization.serialize(data_type.id, value)

    def _serialize_containments(
        self,
        classifier_instance: ClassifierInstance,
        serialized_classifier_instance: SerializedClassifierInstance,
    ) -> None:
        if classifier_instance is None:
            raise ValueError("ClassifierInstance should not be null")

        for containment in classifier_instance.get_classifier().all_containments():
            container = containment.get_container()
            if container is None:
                raise ValueError()
            language = container.get_language()
            if language is None:
                raise ValueError()
            containment_value = SerializedContainmentValue(
                MetaPointer.from_keyed(containment, language),
                [child.id for child in classifier_instance.get_children(containment)],
            )
            serialized_classifier_instance.add_containment_value(containment_value)

    def _serialize_references(
        self,
        classifier_instance: ClassifierInstance,
        serialized_classifier_instance: SerializedClassifierInstance,
    ) -> None:
        if classifier_instance is None:
            raise ValueError("ClassifierInstance should not be null")

        for reference in classifier_instance.get_classifier().all_references():
            reference_value = SerializedReferenceValue()
            classifier = reference.get_container()
            if classifier is None:
                raise ValueError()
            language = classifier.get_language()
            if language is None:
                raise ValueError()
            reference_value.meta_pointer = MetaPointer.from_keyed(reference, language)
            reference_value.value = [
                SerializedReferenceValueEntry(
                    reference=(
                        None
                        if (
                            self.builtins_reference_dangling
                            and ClassifierInstanceUtils.is_builtin_element(
                                rv.get_referred()
                            )
                        )
                        else (rv.get_referred().id if rv.get_referred() else None)
                    ),
                    resolve_info=rv.get_resolve_info(),
                )
                for rv in classifier_instance.get_reference_values(reference)
            ]
            serialized_classifier_instance.add_reference_value(reference_value)

    def _serialize_annotations(
        self,
        classifier_instance: ClassifierInstance,
        serialized_classifier_instance: SerializedClassifierInstance,
    ) -> None:
        if classifier_instance is None:
            raise ValueError("ClassifierInstance should not be null")

        serialized_classifier_instance.annotations = [
            annotation.id for annotation in classifier_instance.get_annotations()
        ]

    def deserialize_serialization_block(self, serialized_chunk: SerializedChunk):
        serialized_instances = serialized_chunk.classifier_instances
        return self._deserialize_classifier_instances(
            self.lion_web_version, serialized_instances
        )

    def _deserialize_classifier_instances(
        self,
        lion_web_version: LionWebVersion,
        serialized_classifier_instances: List[SerializedClassifierInstance],
    ) -> (List)[ClassifierInstance]:
        from lionwebpython.api.composite_classifier_instance_resolver import \
            CompositeClassifierInstanceResolver
        from lionwebpython.model.annotation_instance import AnnotationInstance
        from lionwebpython.model.impl.proxy_node import ProxyNode
        from lionwebpython.serialization.map_based_resolver import \
            MapBasedResolver
        from lionwebpython.serialization.node_populator import NodePopulator

        if lion_web_version is None:
            raise ValueError("lion_web_version should not be null")

        # We want to deserialize the nodes starting from the leaves. This is useful because in certain
        # cases we may want to use the children as constructor parameters of the parent
        deserialization_status = self._sort_leaves_first(
            serialized_classifier_instances
        )
        sorted_serialized_instances = deserialization_status.sorted_list

        if len(sorted_serialized_instances) != len(serialized_classifier_instances):
            raise ValueError("Mismatch in number of nodes to deserialize")

        deserialized_by_id: Dict[str, ClassifierInstance] = {}
        serialized_to_instance_map = {}

        for n in sorted_serialized_instances:
            instantiated = self._instantiate_from_serialized(
                lion_web_version, n, deserialized_by_id
            )
            id = n.id
            if id and id in deserialized_by_id:
                raise ValueError(f"Duplicate ID found: {id}")
            if id is None:
                raise ValueError()

            deserialized_by_id[id] = instantiated
            serialized_to_instance_map[n] = instantiated

        if len(sorted_serialized_instances) != len(serialized_to_instance_map):
            raise ValueError(
                f"We got {len(sorted_serialized_instances)} nodes to deserialize, but we deserialized {len(serialized_to_instance_map)}"
            )

        classifier_instance_resolver = CompositeClassifierInstanceResolver(
            MapBasedResolver(deserialized_by_id),
            deserialization_status.get_proxies_instance_resolver(),
            self.instance_resolver,
        )

        node_populator = NodePopulator(
            self, classifier_instance_resolver, deserialization_status, lion_web_version
        )

        for node in serialized_classifier_instances:
            classifier_instance = serialized_to_instance_map[node]
            node_populator.populate_classifier_instance(classifier_instance, node)

            parent_node_id = node.parent_node_id
            parent = (
                classifier_instance_resolver.resolve(parent_node_id)
                if parent_node_id
                else None
            )
            if (
                isinstance(parent, ProxyNode)
                and self.unavailable_parent_policy == UnavailableNodePolicy.PROXY_NODES
            ):
                if isinstance(classifier_instance, HasSettableParent):
                    classifier_instance.set_parent(parent)
                else:
                    raise NotImplementedError(
                        f"Cannot set parent for {classifier_instance}"
                    )

            if isinstance(classifier_instance, AnnotationInstance):
                if node is None:
                    raise ValueError(
                        "Dangling annotation instance found (annotated node is null)"
                    )
                parent_node_id = node.parent_node_id
                parent_instance = (
                    deserialized_by_id.get(parent_node_id) if parent_node_id else None
                )
                if parent_instance:
                    parent_instance.add_annotation(classifier_instance)
                else:
                    raise ValueError(
                        f"Cannot resolve annotated node {classifier_instance.get_parent()}"
                    )

        nodes_with_original_sorting = [
            serialized_to_instance_map[sn] for sn in serialized_classifier_instances
        ]
        nodes_with_original_sorting.extend(deserialization_status.proxies)

        return nodes_with_original_sorting

    def _validate_serialization_block(
        self, serialization_block: SerializedChunk
    ) -> None:
        if serialization_block is None:
            raise ValueError("serialization_block should not be null")
        if serialization_block.serialization_format_version is None:
            raise ValueError("The serializationFormatVersion should not be null")
        if (
            serialization_block.serialization_format_version
            != self.lion_web_version.value
        ):
            raise ValueError(
                f"Only serializationFormatVersion supported by this instance of Serialization is '{self.lion_web_version.value}' "
                f"but we found '{serialization_block.serialization_format_version}'"
            )

    def _sort_leaves_first(
        self, original_list: List[SerializedClassifierInstance]
    ) -> DeserializationStatus:
        """
        This method returned a sorted version of the original list, so that leaves nodes comes first,
        or in other words that a parent never precedes its children.
        """
        deserialization_status = DeserializationStatus(
            original_list, self.instance_resolver
        )

        # We create the list going from the roots to their children and then reverse it
        deserialization_status.put_nodes_with_null_ids_in_front()

        if self.unavailable_parent_policy == UnavailableNodePolicy.NULL_REFERENCES:
            known_ids = {ci.id for ci in original_list}
            for ci in original_list:
                if ci.get_parent_node_id() not in known_ids:
                    deserialization_status.place(ci)

        elif self.unavailable_parent_policy == UnavailableNodePolicy.PROXY_NODES:
            known_ids = {ci.id for ci in original_list}
            parent_ids = {
                n.get_parent_node_id()
                for n in original_list
                if n.get_parent_node_id() is not None
            }
            unknown_parent_ids = parent_ids - known_ids
            for ci in original_list:
                if ci.get_parent_node_id() in unknown_parent_ids:
                    deserialization_status.place(ci)
            for id_ in unknown_parent_ids:
                deserialization_status.create_proxy(id_)

        # Place elements with no parent or already sorted parents
        while deserialization_status.how_many_sorted() < len(original_list):
            initial_length = deserialization_status.how_many_sorted()

            i = 0
            while i < deserialization_status.how_many_to_sort():
                node = deserialization_status.get_node_to_sort(i)
                if node.get_parent_node_id() is None or any(
                    sn.id == node.get_parent_node_id()
                    for sn in deserialization_status.stream_sorted()
                ):
                    deserialization_status.place(node)
                    i -= 1
                i += 1

            if initial_length == deserialization_status.how_many_sorted():
                if deserialization_status.how_many_sorted() == 0:
                    raise DeserializationException(
                        f"No root found, we cannot deserialize this tree. Original list: {original_list}"
                    )
                else:
                    raise DeserializationException(
                        f"Something is not right: we are unable to complete sorting the list {original_list}. Probably there is a containment loop"
                    )

        deserialization_status.reverse()
        return deserialization_status

    def _instantiate_from_serialized(
        self,
        lion_web_version: LionWebVersion,
        serialized_classifier_instance: SerializedClassifierInstance,
        deserialized_by_id: Dict[str, ClassifierInstance],
    ) -> ClassifierInstance:
        if lion_web_version is None:
            raise ValueError("lionWebVersion should not be null")

        serialized_classifier = serialized_classifier_instance.get_classifier()
        if serialized_classifier is None:
            raise RuntimeError(
                f"No metaPointer available for {serialized_classifier_instance}"
            )

        classifier = self.classifier_resolver.resolve_classifier(serialized_classifier)

        # Prepare properties values for instantiator
        properties_values = {}
        for (
            serialized_property_value
        ) in serialized_classifier_instance.get_properties():
            property = classifier.get_property_by_meta_pointer(
                serialized_property_value.meta_pointer
            )
            if property is None:
                available_properties = [
                    MetaPointer.from_feature(p) for p in classifier.all_properties()
                ]
                raise RuntimeError(
                    f"Property with metaPointer {serialized_property_value.meta_pointer} not found in classifier {classifier}. Available properties: {available_properties}"
                )
            if property.get_type() is None:
                raise RuntimeError("Property type should not be null")
            deserialized_value = self.primitive_values_serialization.deserialize(
                property.get_type(),
                serialized_property_value.value,
                property.is_required(),
            )
            properties_values[property] = deserialized_value

        classifier_instance = self.instantiator.instantiate(
            classifier,
            serialized_classifier_instance,
            deserialized_by_id,
            properties_values,
        )
        if not isinstance(classifier_instance, ClassifierInstance):
            raise ValueError()

        # Ensure that properties values are set correctly
        for property, deserialized_value in properties_values.items():
            if deserialized_value != classifier_instance.get_property_value(
                property=property
            ):
                classifier_instance.set_property_value(
                    property=property, value=deserialized_value
                )

        return classifier_instance
