import json
from typing import List, cast

from lionwebpython.serialization.data.metapointer import MetaPointer
from lionwebpython.serialization.data.serialized_chunk import SerializedChunk
from lionwebpython.serialization.data.serialized_classifier_instance import \
    SerializedClassifierInstance
from lionwebpython.serialization.data.serialized_containment_value import \
    SerializedContainmentValue
from lionwebpython.serialization.data.serialized_property_value import \
    SerializedPropertyValue
from lionwebpython.serialization.data.serialized_reference_value import \
    SerializedReferenceValue
from lionwebpython.serialization.data.used_language import UsedLanguage
from lionwebpython.serialization.deserialization_exception import \
    DeserializationException
from lionwebpython.serialization.json_utils import (JsonArray, JsonElement,
                                                    JsonObject)
from lionwebpython.serialization.serialization_utils import SerializationUtils


class LowLevelJsonSerialization:
    def deserialize_serialization_block(
        self, json_element: JsonElement
    ) -> SerializedChunk:
        serialized_chunk = SerializedChunk()
        if isinstance(json_element, dict):
            self._check_no_extra_keys(
                json_element, ["nodes", "serializationFormatVersion", "languages"]
            )
            self._read_serialization_format_version(serialized_chunk, json_element)
            self._read_languages(serialized_chunk, json_element)
            self._deserialize_classifier_instances(serialized_chunk, json_element)
            return serialized_chunk
        else:
            raise ValueError(
                f"We expected a JSON object, we got instead: {json_element}"
            )

    def serialize_to_json_element(
        self, serialized_chunk: SerializedChunk
    ) -> JsonObject:
        serialized_nodes = []
        for node in serialized_chunk.get_classifier_instances():
            node_json = {
                "id": node.get_id(),
                "classifier": self._serialize_metapointer_to_json_element(
                    node.get_classifier()
                ),
                "properties": [],
                "containments": [],
                "references": [],
                "annotations": [
                    annotation_id for annotation_id in node.get_annotations()
                ],
                "parent": node.get_parent_node_id(),
            }

            for property_value in node.get_properties():
                property_json = {
                    "property": self._serialize_metapointer_to_json_element(
                        property_value.get_meta_pointer()
                    ),
                    "value": property_value.get_value(),
                }
                node_json["properties"].append(property_json)

            for children_value in node.get_containments():
                children_json = {
                    "containment": self._serialize_metapointer_to_json_element(
                        children_value.get_meta_pointer()
                    ),
                    "children": SerializationUtils.to_json_array(
                        children_value.get_value()
                    ),
                }
                node_json["containments"].append(children_json)

            for reference_value in node.get_references():
                reference_json = {
                    "reference": self._serialize_metapointer_to_json_element(
                        reference_value.get_meta_pointer()
                    ),
                    "targets": SerializationUtils.to_json_array_of_reference_values(
                        reference_value.get_value()
                    ),
                }
                node_json["references"].append(reference_json)

            serialized_nodes.append(node_json)

        return {
            "serializationFormatVersion": serialized_chunk.serialization_format_version,
            "languages": [
                self._serialize_language_to_json_element(lang)
                for lang in serialized_chunk.languages
            ],
            "nodes": serialized_nodes,
        }

    def _serialize_language_to_json_element(
        self, language_key_version: UsedLanguage
    ) -> JsonObject:
        json_object = {
            "key": language_key_version.get_key(),
            "version": language_key_version.get_version(),
        }
        return cast(JsonObject, json_object)

    def _serialize_metapointer_to_json_element(
        self, meta_pointer: MetaPointer
    ) -> JsonObject:
        return {
            "language": meta_pointer.language,
            "version": meta_pointer.version,
            "key": meta_pointer.key,
        }

    def serialize_to_json_string(self, serialized_chunk: SerializedChunk) -> str:
        return json.dumps(
            self.serialize_to_json_element(serialized_chunk),
            indent=2,
        )

    def deserialize_serialization_block_from_string(
        self,
        json_string: str,
    ) -> SerializedChunk:
        try:
            json_element = json.loads(json_string)
            return self.deserialize_serialization_block(json_element)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")

    def deserialize_serialization_block_from_file(
        self, file_path: str
    ) -> SerializedChunk:
        try:
            with open(file_path, "r") as file:
                json_element = json.load(file)
                return self.deserialize_serialization_block(json_element)
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in file: {e}")

    def _check_no_extra_keys(
        self, json_object: JsonObject, expected_keys: List[str]
    ) -> None:
        extra_keys = set(json_object.keys())
        extra_keys -= set(expected_keys)
        if extra_keys:
            raise ValueError(
                f"Extra keys found: {extra_keys}. Expected keys: {expected_keys}"
            )

    def _read_serialization_format_version(
        self, serialized_chunk: SerializedChunk, top_level: JsonObject
    ) -> None:
        if "serializationFormatVersion" not in top_level:
            raise ValueError("serializationFormatVersion not specified")
        serialization_format_version = top_level.get("serializationFormatVersion")
        if not isinstance(serialization_format_version, str):
            raise ValueError(
                f"serializationFormatVersion should be a string instead it is {serialization_format_version}"
            )
        serialized_chunk.serialization_format_version = serialization_format_version

    @staticmethod
    def require_is_string(value, desc: str):
        if not isinstance(value, str):
            raise ValueError(f"{desc} should be a string value")

    def _read_languages(
        self, serialized_chunk: SerializedChunk, top_level: JsonObject
    ) -> None:
        if "languages" not in top_level:
            raise ValueError("languages not specified")
        languages = top_level.get("languages")
        if isinstance(languages, list):
            for element in languages:
                try:
                    language_key_version = UsedLanguage()
                    if isinstance(element, dict):
                        extra_keys = set(element.keys()) - {"key", "version"}
                        if extra_keys:
                            raise ValueError(
                                f"Unexpected keys in language object: {extra_keys}"
                            )
                        if "key" not in element or "version" not in element:
                            raise ValueError(
                                f"Language should have keys 'key' and 'version'. Found: {element}"
                            )
                        if not isinstance(element.get("key"), str) or not isinstance(
                            element.get("version"), str
                        ):
                            raise ValueError(
                                "Both 'key' and 'version' should be strings"
                            )
                        language_key_version.key = element.get("key")
                        language_key_version.version = element.get("version")
                    else:
                        raise ValueError(
                            f"Language should be an object. Found: {element}"
                        )
                    serialized_chunk.add_language(language_key_version)
                except Exception as e:
                    raise RuntimeError(f"Issue while deserializing {element}") from e
        else:
            raise ValueError(f"We expected a list, we got instead: {languages}")

    def _deserialize_classifier_instances(
        self, serialized_chunk: SerializedChunk, top_level: JsonObject
    ) -> None:
        if "nodes" not in top_level:
            raise ValueError("nodes not specified")
        nodes = top_level.get("nodes")
        if isinstance(nodes, list):
            for element in nodes:
                try:
                    instance = self._deserialize_classifier_instance(element)
                    serialized_chunk.add_classifier_instance(instance)
                except DeserializationException as e:
                    raise DeserializationException(
                        "Issue while deserializing classifier instances"
                    ) from e
                except Exception as e:
                    raise DeserializationException(
                        f"Issue while deserializing {element}"
                    ) from e
        else:
            raise ValueError(f"We expected a list, we got instead: {nodes}")

    def _deserialize_classifier_instance(
        self, json_element: JsonElement
    ) -> SerializedClassifierInstance:
        if not isinstance(json_element, dict):
            raise ValueError(
                f"Malformed JSON. Object expected but found {json_element}"
            )
        try:
            mp = SerializationUtils.try_to_get_meta_pointer_property(
                json_element, "classifier"
            )
            if mp is None:
                raise ValueError(f"MetaPointer not found in {json_element}")
            serialized_classifier_instance = SerializedClassifierInstance(
                SerializationUtils.try_to_get_string_property(json_element, "id"), mp
            )
            serialized_classifier_instance.set_parent_node_id(
                SerializationUtils.try_to_get_string_property(json_element, "parent")
            )

            properties = cast(JsonArray, json_element.get("properties", []))
            for property_entry in properties:
                property_obj = cast(JsonObject, property_entry)
                mp = SerializationUtils.try_to_get_meta_pointer_property(
                    property_obj, "property"
                )
                if mp is None:
                    raise ValueError(
                        f"MetaPointer not found for property {property_obj}"
                    )
                serialized_classifier_instance.add_property_value(
                    SerializedPropertyValue(
                        mp,
                        SerializationUtils.try_to_get_string_property(
                            property_obj, "value"
                        ),
                    )
                )

            containments: JsonArray
            if "children" in json_element:
                containments = cast(JsonArray, json_element.get("children", []))
            elif "containments" in json_element:
                containments = cast(JsonArray, json_element.get("containments", []))
            else:
                raise RuntimeError(
                    f"Node is missing containments entry: {json_element}"
                )

            for containment_entry in containments:
                containment_obj = cast(JsonObject, containment_entry)
                ids = SerializationUtils.try_to_get_array_of_ids(
                    containment_obj, "children"
                )
                if ids is None:
                    ids = []
                mp = SerializationUtils.try_to_get_meta_pointer_property(
                    containment_obj, "containment"
                )
                if mp is None:
                    raise ValueError(
                        f"MetaPointer not found in containment {containment_obj}"
                    )
                serialized_classifier_instance.add_containment_value(
                    SerializedContainmentValue(mp, ids)
                )

            references = cast(JsonObject, json_element.get("references", []))
            for reference_entry in references:
                reference_obj = cast(JsonObject, reference_entry)
                serialized_classifier_instance.add_reference_value(
                    SerializedReferenceValue(
                        SerializationUtils.try_to_get_meta_pointer_property(
                            reference_obj, "reference"
                        ),
                        SerializationUtils.try_to_get_array_of_references_property(
                            reference_obj, "targets"
                        ),
                    )
                )

            annotations_ja = cast(JsonArray, json_element.get("annotations"))
            if annotations_ja is not None:
                serialized_classifier_instance.set_annotations(
                    [cast(str, annotation_entry) for annotation_entry in annotations_ja]
                )

            return serialized_classifier_instance

        except DeserializationException as e:
            raise DeserializationException(
                f"Issue occurred while deserializing {json_element}"
            ) from e
