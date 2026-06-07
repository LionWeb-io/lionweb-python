from typing import Any, cast

from lionweb.serialization.data import LanguageVersion
from lionweb.serialization.data.metapointer import MetaPointer
from lionweb.serialization.data.serialized_reference_value import SerializedReferenceValueEntry
from lionweb.serialization.deserialization_exception import DeserializationException
from lionweb.serialization.low_level_json_serialization import JsonObject


class SerializationUtils:
    """Helpers for extracting typed values from raw, low-level JSON structures
    used in LionWeb serialization."""

    @staticmethod
    def get_as_string_or_none(element: object) -> str | None:
        if element is None or element == "null":
            return None
        return str(element)

    @staticmethod
    def try_to_get_string_property(json_object: dict, property_name: str) -> str | None:
        if property_name not in json_object:
            return None
        value = json_object.get(property_name)
        if isinstance(value, str):
            return value
        return None

    @staticmethod
    def try_to_get_meta_pointer_property(
        json_object: dict, property_name: str
    ) -> MetaPointer | None:
        if property_name not in json_object:
            return None
        value = cast(dict[Any, Any], json_object.get(property_name))
        language_k: str | None = cast(
            str | None,
            SerializationUtils.try_to_get_string_property(value, "language"),
        )
        language_v: str | None = cast(
            str | None,
            SerializationUtils.try_to_get_string_property(value, "version"),
        )
        language_version = LanguageVersion(language_k, language_v)
        if isinstance(value, dict):
            return MetaPointer(
                language_version=language_version,
                key=SerializationUtils.try_to_get_string_property(value, "key"),
            )
        return None

    @staticmethod
    def try_to_get_array_of_ids(
        json_object: JsonObject, property_name: str
    ) -> list[str | None] | None:
        if property_name not in json_object:
            return None
        value = json_object.get(property_name)
        if isinstance(value, list):
            result: list[str | None] = []
            for e in value:
                if e is None:
                    raise DeserializationException(
                        "Unable to deserialize child identified by Null ID"
                    )
                result.append(str(e))
            return result
        return None

    @staticmethod
    def try_to_get_array_of_references_property(
        json_object: JsonObject, property_name: str
    ) -> list[SerializedReferenceValueEntry]:
        if property_name not in json_object:
            return []
        value = json_object.get(property_name)
        if isinstance(value, list):
            entries: list[SerializedReferenceValueEntry] = []
            for e in value:
                if isinstance(e, dict):
                    entries.append(
                        SerializedReferenceValueEntry(
                            reference=SerializationUtils.try_to_get_string_property(e, "reference"),
                            resolve_info=SerializationUtils.try_to_get_string_property(
                                e, "resolveInfo"
                            ),
                        )
                    )
            return entries
        return []

    @staticmethod
    def to_json_array(string_list: list[str]) -> list[str]:
        return string_list

    @staticmethod
    def to_json_array_of_reference_values(
        entries: list[SerializedReferenceValueEntry],
    ) -> list[dict[str, str | None]]:
        json_array = []
        for entry in entries:
            entry_json = {
                "resolveInfo": entry.resolve_info,
                "reference": entry.reference,
            }
            json_array.append(entry_json)
        return json_array
