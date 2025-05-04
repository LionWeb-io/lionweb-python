from gen.language import get_book, get_library, get_writer, get_guidebookwriter, get_specialistbookwriter
from gen.node_classes import Book, Library, Writer, GuideBookWriter, SpecialistBookWriter
from lionweb.serialization import AbstractSerialization
from lionweb.serialization.data.serialized_classifier_instance import SerializedClassifierInstance


def register_deserializers(serialization: AbstractSerialization):

    def deserializer_book(classifier, serialized_instance:
        SerializedClassifierInstance, deserialized_instances_by_id,
        properties_values):
        return Book(serialized_instance.id)
    serialization.instantiator.register_custom_deserializer(get_book().id,
        deserializer=deserializer_book)

    def deserializer_library(classifier, serialized_instance:
        SerializedClassifierInstance, deserialized_instances_by_id,
        properties_values):
        return Library(serialized_instance.id)
    serialization.instantiator.register_custom_deserializer(get_library().
        id, deserializer=deserializer_library)

    def deserializer_writer(classifier, serialized_instance:
        SerializedClassifierInstance, deserialized_instances_by_id,
        properties_values):
        return Writer(serialized_instance.id)
    serialization.instantiator.register_custom_deserializer(get_writer().id,
        deserializer=deserializer_writer)

    def deserializer_guidebookwriter(classifier, serialized_instance:
        SerializedClassifierInstance, deserialized_instances_by_id,
        properties_values):
        return GuideBookWriter(serialized_instance.id)
    serialization.instantiator.register_custom_deserializer(get_guidebookwriter
        ().id, deserializer=deserializer_guidebookwriter)

    def deserializer_specialistbookwriter(classifier, serialized_instance:
        SerializedClassifierInstance, deserialized_instances_by_id,
        properties_values):
        return SpecialistBookWriter(serialized_instance.id)
    serialization.instantiator.register_custom_deserializer(
        get_specialistbookwriter().id, deserializer=
        deserializer_specialistbookwriter)
