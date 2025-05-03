from abc import ABC
from dataclasses import dataclass
from typing import Optional
from enum import Enum
from pylasu.model.metamodel import Expression as StarLasuExpression, PlaceholderElement as StarLasuPlaceholderElement, Named as StarLasuNamed, TypeAnnotation as StarLasuTypeAnnotation, Parameter as StarLasuParameter, Statement as StarLasuStatement, EntityDeclaration as StarLasuEntityDeclaration, BehaviorDeclaration as StarLasuBehaviorDeclaration, Documentation as StarLasuDocumentation
from pylasu.model import Node
from .ast import Book, Library, Writer, GuideBookWriter, SpecialistBookWriter
from primitive_types import 
from lionwebpython.serialization.json_serialization import JsonSerialization


def _deserialize_book(classifier, serialized_instance,
    deserialized_instances_by_id, properties_values) ->Book:
    return Book(title='title', pages='pages', author='author')


def _deserialize_library(classifier, serialized_instance,
    deserialized_instances_by_id, properties_values) ->Library:
    return Library(name='name', books='books')


def _deserialize_writer(classifier, serialized_instance,
    deserialized_instances_by_id, properties_values) ->Writer:
    return Writer(name='name')


def _deserialize_guide_book_writer(classifier, serialized_instance,
    deserialized_instances_by_id, properties_values) ->GuideBookWriter:
    return GuideBookWriter(countries='countries', name='name')


def _deserialize_specialist_book_writer(classifier, serialized_instance,
    deserialized_instances_by_id, properties_values) ->SpecialistBookWriter:
    return SpecialistBookWriter(subject='subject', name='name')


def register_deserializers(json_serialization: JsonSerialization):
    json_serialization.instantiator.register_custom_deserializer('library-Book'
        , _deserialize_book)
    json_serialization.instantiator.register_custom_deserializer(
        'library-Library', _deserialize_library)
    json_serialization.instantiator.register_custom_deserializer(
        'library-Writer', _deserialize_writer)
    json_serialization.instantiator.register_custom_deserializer(
        'library-GuideBookWriter', _deserialize_guide_book_writer)
    json_serialization.instantiator.register_custom_deserializer(
        'library-SpecialistBookWriter', _deserialize_specialist_book_writer)
