from typing import Dict, List, Optional, Union

from lionwebpython.serialization.data.metapointer import MetaPointer
from lionwebpython.serialization.data.serialized_reference_value import \
    SerializedReferenceValueEntry
from lionwebpython.serialization.deserialization_exception import \
    DeserializationException
from lionwebpython.serialization.low_level_json_serialization import JsonObject


class SerializationUtils:
    @staticmethod
    def get_as_string_or_none(element) -> Optional[str]:
        if element is None or element == "null":
            return None
        return str(element)

    @staticmethod
    def try_to_get_string_property(
        json_object: Dict, property_name: str
    ) -> Optional[str]:
        if property_name not in json_object:
            return None
        value = json_object.get(property_name)
        if isinstance(value, str):
            return value
        return None

    @staticmethod
    def try_to_get_meta_pointer_property(
        json_object: Dict, property_name: str
    ) -> Optional[MetaPointer]:
        if property_name not in json_object:
            return None
        value = json_object.get(property_name)
        if isinstance(value, dict):
            return MetaPointer(
                language=SerializationUtils.try_to_get_string_property(
                    value, "language"
                ),
                version=SerializationUtils.try_to_get_string_property(value, "version"),
                key=SerializationUtils.try_to_get_string_property(value, "key"),
            )
        return None

    @staticmethod
    def try_to_get_array_of_ids(
        json_object: JsonObject, property_name: str
    ) -> Optional[List[str]]:
        if property_name not in json_object:
            return None
        value = json_object.get(property_name)
        if isinstance(value, list):
            result = []
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
    ) -> List[SerializedReferenceValueEntry]:
        if property_name not in json_object:
            return []
        value = json_object.get(property_name)
        if isinstance(value, list):
            entries: List[SerializedReferenceValueEntry] = []
            for e in value:
                if isinstance(e, dict):
                    entries.append(
                        SerializedReferenceValueEntry(
                            reference=SerializationUtils.try_to_get_string_property(
                                e, "reference"
                            ),
                            resolve_info=SerializationUtils.try_to_get_string_property(
                                e, "resolveInfo"
                            ),
                        )
                    )
            return entries
        return []

    @staticmethod
    def to_json_array(string_list: List[str]) -> List[str]:
        return string_list

    @staticmethod
    def to_json_array_of_reference_values(
        entries: List[SerializedReferenceValueEntry],
    ) -> List[Dict[str, Union[str, None]]]:
        json_array = []
        for entry in entries:
            entry_json = {
                "resolveInfo": entry.resolve_info,
                "reference": entry.reference,
            }
            json_array.append(entry_json)
        return json_array
