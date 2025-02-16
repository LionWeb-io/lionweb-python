from typing import List

from lionwebpython.api.local_classifier_instance_resolver import \
    LocalClassifierInstanceResolver
from lionwebpython.language.data_type import DataType
from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.model import ClassifierInstance
from lionwebpython.model.annotation_instance import AnnotationInstance
from lionwebpython.model.classifier_instance_utils import ClassifierInstanceUtils
from lionwebpython.serialization.classifier_resolver import ClassifierResolver
from lionwebpython.serialization.data.metapointer import MetaPointer
from lionwebpython.serialization.data.serialized_chunk import SerializedChunk
from lionwebpython.serialization.data.serialized_classifier_instance import \
    SerializedClassifierInstance
from lionwebpython.serialization.data.serialized_containment_value import SerializedContainmentValue
from lionwebpython.serialization.data.serialized_property_value import SerializedPropertyValue
from lionwebpython.serialization.data.serialized_reference_value import SerializedReferenceValue, \
    SerializedReferenceValueEntry
from lionwebpython.serialization.data.used_language import UsedLanguage
from lionwebpython.serialization.deserialization_exception import DeserializationException
from lionwebpython.serialization.deserialization_status import DeserializationStatus
from lionwebpython.serialization.instantiator import Instantiator
from lionwebpython.serialization.primitives_values_serialization import \
    PrimitiveValuesSerialization
from lionwebpython.serialization.unavailable_node_policy import \
    UnavailableNodePolicy


class AbstractSerialization:

    DEFAULT_SERIALIZATION_FORMAT = LionWebVersion.current_version()

    def __init__(
        self, lionweb_version: LionWebVersion = LionWebVersion.current_version()
    ):
        self.lion_web_version = lionweb_version
        self.classifier_resolver = ClassifierResolver()
        self.instantiator = Instantiator()
        self.primitive_values_serialization = PrimitiveValuesSerialization()
        self.instance_resolver = LocalClassifierInstanceResolver()
        self.unavailable_parent_policy = UnavailableNodePolicy.THROW_ERROR
        self.unavailable_children_policy = UnavailableNodePolicy.THROW_ERROR
        self.unavailable_reference_target_policy = UnavailableNodePolicy.THROW_ERROR
        self.builtins_reference_dangling = False

    def enable_dynamic_nodes(self):
        self.instantiator.enable_dynamic_nodes()
        self.primitive_values_serialization.enable_dynamic_nodes()

    def register_language(self, language):
        self.classifier_resolver.register_language(language)
        self.primitive_values_serialization.register_language(language)

    def make_builtins_reference_dangling(self):
        self.builtins_reference_dangling = True

    def serialize_tree_to_serialization_block(self, root):
        classifier_instances = set()
        self.collect_self_and_descendants(root, True, classifier_instances)
        return self.serialize_nodes_to_serialization_block(classifier_instances)

    def collect_self_and_descendants(
        self, instance, include_self=True, collection=None
    ):
        if collection is None:
            collection = set()
        if include_self:
            collection.add(instance)
        for child in instance.get_children():
            self.collect_self_and_descendants(child, True, collection)
        return collection

    def serialize_nodes_to_serialization_block(self, classifier_instances):
        serialized_chunk = SerializedChunk()
        serialized_chunk.serialization_format_version = self.lion_web_version.value
        for instance in classifier_instances:
            serialized_chunk.classifier_instances.append(self.serialize_node(instance))
            for annotation in instance.get_annotations():
                serialized_chunk.classifier_instances.append(
                    self.serialize_annotation_instance(annotation)
                )
            self.consider_language_during_serialization(
                serialized_chunk, instance.get_classifier().get_language()
            )
        return serialized_chunk

    def consider_language_during_serialization(self, serialized_chunk, language):
        self.register_language(language)
        used_language = UsedLanguage(language.get_key(), language.get_version())
        if used_language not in serialized_chunk.languages:
            serialized_chunk.languages.append(used_language)

    def serialize_node(self, classifier_instance: ClassifierInstance) -> SerializedClassifierInstance:
        serialized_instance = SerializedClassifierInstance(classifier_instance.get_id(), MetaPointer.from_language_entity(classifier_instance.get_classifier()))
        parent = classifier_instance.get_parent()
        serialized_instance.parent_node_id = parent.get_id() if parent else None
        self._serialize_properties(classifier_instance, serialized_instance)
        self._serialize_containments(classifier_instance, serialized_instance)
        self._serialize_references(classifier_instance, serialized_instance)
        self._serialize_annotations(classifier_instance, serialized_instance)
        return serialized_instance

    def serialize_annotation_instance(self, annotation_instance: AnnotationInstance) -> SerializedClassifierInstance:
        if annotation_instance is None:
            raise ValueError("AnnotationInstance should not be null")

        serialized_classifier_instance = SerializedClassifierInstance(annotation_instance.get_id(), MetaPointer.from_language_entity(
            annotation_instance.get_annotation_definition()))
        parent = annotation_instance.get_parent()
        serialized_classifier_instance.parent_node_id = parent.get_id() if parent else None
        self._serialize_properties(annotation_instance, serialized_classifier_instance)
        self._serialize_containments(annotation_instance, serialized_classifier_instance)
        self._serialize_references(annotation_instance, serialized_classifier_instance)
        self._serialize_annotations(annotation_instance, serialized_classifier_instance)

        return serialized_classifier_instance

    def _serialize_properties(self, classifier_instance: ClassifierInstance,
                              serialized_classifier_instance: SerializedClassifierInstance) -> None:
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
            property_value = SerializedPropertyValue(mp , self._serialize_property_value(
                    dt, classifier_instance.get_property_value(property=property)
                ))
            serialized_classifier_instance.add_property_value(property_value)

    def _serialize_property_value(self, data_type: DataType, value: object):
        if data_type is None:
            raise ValueError("Cannot serialize property when the dataType is null")
        if data_type.get_id() is None:
            raise ValueError("Cannot serialize property when the dataType.ID is null")
        if value is None:
            return None
        return self.primitive_values_serialization.serialize(data_type.get_id(), value)

    def _serialize_containments(self, classifier_instance: ClassifierInstance,
                                serialized_classifier_instance: SerializedClassifierInstance) -> None:
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
                [child.get_id() for child in classifier_instance.get_children(containment)])
            serialized_classifier_instance.add_containment_value(containment_value)

    def _serialize_references(self, classifier_instance: ClassifierInstance,
                              serialized_classifier_instance: SerializedClassifierInstance) -> None:
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
                    None if (
                            self.builtins_reference_dangling and
                            ClassifierInstanceUtils.is_builtin_element(rv.get_referred())
                    ) else (rv.get_referred().get_id() if rv.get_referred() else None),
                    rv.get_resolve_info()
                )
                for rv in classifier_instance.get_reference_values(reference)
            ]
            serialized_classifier_instance.add_reference_value(reference_value)

    def _serialize_annotations(self, classifier_instance: ClassifierInstance,
                              serialized_classifier_instance: SerializedClassifierInstance) -> None:
        if classifier_instance is None:
            raise ValueError("ClassifierInstance should not be null")

        serialized_classifier_instance.annotations = [
            annotation.get_id() for annotation in classifier_instance.get_annotations()
        ]

    def deserialize_serialization_block(self, serialized_chunk):
        serialized_instances = serialized_chunk.classifier_instances
        return self.deserialize_classifier_instances(
            self.lion_web_version, serialized_instances
        )

    def deserialize_classifier_instances(self, lion_web_version, serialized_instances):
        deserialized_by_id = {}
        for serialized_instance in serialized_instances:
            classifier = self.classifier_resolver.resolve_classifier(
                serialized_instance.classifier
            )
            properties_values = {
                prop_key: self.primitive_values_serialization.deserialize(
                    classifier.get_property_by_key(prop_key).get_type(),
                    serialized_instance.properties[prop_key],
                    classifier.get_property_by_key(prop_key).is_required(),
                )
                for prop_key in serialized_instance.properties
            }
            instance = self.instantiator.instantiate(
                classifier, serialized_instance, deserialized_by_id, properties_values
            )
            deserialized_by_id[serialized_instance.id] = instance

        for serialized_instance in serialized_instances:
            instance = deserialized_by_id[serialized_instance.id]
            parent_id = serialized_instance.parent_node_id
            if parent_id:
                parent_instance = deserialized_by_id.get(parent_id)
                if parent_instance and hasattr(instance, "set_parent"):
                    instance.set_parent(parent_instance)

        return list(deserialized_by_id.values())

    def _validate_serialization_block(self, serialization_block: SerializedChunk) -> None:
        if serialization_block is None:
            raise ValueError("serialization_block should not be null")
        if serialization_block.serialization_format_version is None:
            raise ValueError("The serializationFormatVersion should not be null")
        if serialization_block.serialization_format_version != self.lion_web_version.value:
            raise ValueError(
                f"Only serializationFormatVersion supported by this instance of Serialization is '{self.lion_web_version.value}' "
                f"but we found '{serialization_block.serialization_format_version}'"
            )

    def _sort_leaves_first(self, original_list: List[SerializedClassifierInstance]) -> DeserializationStatus:
        deserialization_status = DeserializationStatus(original_list, self.instance_resolver)

        # We create the list going from the roots to their children and then reverse it
        deserialization_status.put_nodes_with_null_ids_in_front()

        if self.unavailable_parent_policy == UnavailableNodePolicy.NULL_REFERENCES:
            known_ids = {ci.get_id() for ci in original_list}
            for ci in original_list:
                if ci.get_parent_node_id() not in known_ids:
                    deserialization_status.place(ci)

        elif self.unavailable_parent_policy == UnavailableNodePolicy.PROXY_NODES:
            known_ids = {ci.get_id() for ci in original_list}
            parent_ids = {n.get_parent_node_id() for n in original_list if n.get_parent_node_id() is not None}
            unknown_parent_ids = parent_ids - known_ids
            for ci in original_list:
                if ci.get_parent_node_id() in unknown_parent_ids:
                    deserialization_status.place(ci)
            for id_ in unknown_parent_ids:
                deserialization_status.create_proxy(id_)

        # Place elements with no parent or already sorted parents
        while deserialization_status.how_many_sorted() < len(original_list):
            initial_length = deserialization_status.how_many_sorted()
            for i in range(deserialization_status.how_many_to_sort()):
                node = deserialization_status.get_node_to_sort(i)
                if node.get_parent_node_id() is None or any(
                    sn.get_id() == node.get_parent_node_id() for sn in deserialization_status.stream_sorted()
                ):
                    deserialization_status.place(node)

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

