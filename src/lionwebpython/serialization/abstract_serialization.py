from lionwebpython.api.local_classifier_instance_resolver import \
    LocalClassifierInstanceResolver
from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.serialization.classifier_resolver import ClassifierResolver
from lionwebpython.serialization.data.serialized_chunk import SerializedChunk
from lionwebpython.serialization.data.serialized_classifier_instance import \
    SerializedClassifierInstance
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
        serialized_chunk.serialization_format_version = self.lion_web_version
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
        language_key_version = f"{language.get_key()}:{language.get_version()}"
        if language_key_version not in serialized_chunk.languages:
            serialized_chunk.languages.append(language_key_version)

    def serialize_node(self, classifier_instance):
        serialized_instance = SerializedClassifierInstance()
        serialized_instance.id = classifier_instance.get_id()
        serialized_instance.classifier = (
            classifier_instance.get_classifier().get_meta_pointer()
        )
        parent = classifier_instance.get_parent()
        serialized_instance.parent_node_id = parent.get_id() if parent else None
        serialized_instance.properties = {
            prop.get_key(): self.serialize_property_value(
                prop.get_type(), classifier_instance.get_property_value(prop)
            )
            for prop in classifier_instance.get_classifier().get_all_properties()
        }
        serialized_instance.children = {
            containment.get_key(): [
                child.get_id()
                for child in classifier_instance.get_children(containment)
            ]
            for containment in classifier_instance.get_classifier().get_all_containments()
        }
        serialized_instance.references = {
            reference.get_key(): [
                (
                    rv.get_referred().get_id() if rv.get_referred() else None,
                    rv.get_resolve_info(),
                )
                for rv in classifier_instance.get_reference_values(reference)
            ]
            for reference in classifier_instance.get_classifier().get_all_references()
        }
        serialized_instance.annotations = [
            annotation.get_id() for annotation in classifier_instance.get_annotations()
        ]
        return serialized_instance

    def serialize_annotation_instance(self, annotation_instance):
        serialized_instance = SerializedClassifierInstance()
        serialized_instance.id = annotation_instance.get_id()
        serialized_instance.parent_node_id = annotation_instance.get_parent().get_id()
        serialized_instance.classifier = (
            annotation_instance.get_annotation_definition().get_meta_pointer()
        )
        serialized_instance.properties = {
            prop.get_key(): self.serialize_property_value(
                prop.get_type(), annotation_instance.get_property_value(prop)
            )
            for prop in annotation_instance.get_annotation_definition().get_all_properties()
        }
        serialized_instance.annotations = [
            annotation.get_id() for annotation in annotation_instance.get_annotations()
        ]
        return serialized_instance

    def serialize_property_value(self, data_type, value):
        if value is None:
            return None
        return self.primitive_values_serialization.serialize(data_type.get_id(), value)

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
