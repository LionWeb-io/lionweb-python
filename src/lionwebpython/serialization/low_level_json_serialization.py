import json

from lionwebpython.serialization.data.serialized_chunk import SerializedChunk


class LowLevelJsonSerialization:
    @staticmethod
    def deserialize_serialization_block(json_element: dict) -> SerializedChunk:
        # if not isinstance(json_element, dict):
        #     raise ValueError("Expected a dictionary, got: " + str(json_element))
        #
        # required_keys = {"nodes", "serializationFormatVersion", "languages"}
        # if not required_keys.issubset(json_element.keys()):
        #     raise ValueError("Missing required keys: " + str(required_keys - json_element.keys()))
        #
        # serialized_chunk = SerializedChunk()
        # serialized_chunk.set_serialization_format_version(json_element.get("serializationFormatVersion"))
        #
        # for language in json_element.get("languages", []):
        #     serialized_chunk.add_language(language)
        #
        # for node in json_element.get("nodes", []):
        #     serialized_chunk.add_classifier_instance(node)
        #
        # return serialized_chunk
        raise ValueError("NOT YET TRANSLATED")

    @staticmethod
    def serialize_to_json_element(serialized_chunk: SerializedChunk) -> dict:
        return {
            "serializationFormatVersion": serialized_chunk.serialization_format_version,
            "languages": serialized_chunk.languages,
            "nodes": serialized_chunk.classifier_instances,
        }

    @staticmethod
    def serialize_to_json_string(serialized_chunk: SerializedChunk) -> str:
        return json.dumps(
            LowLevelJsonSerialization.serialize_to_json_element(serialized_chunk),
            indent=2,
        )

    @staticmethod
    def deserialize_serialization_block_from_string(
        json_string: str,
    ) -> SerializedChunk:
        try:
            json_element = json.loads(json_string)
            return LowLevelJsonSerialization.deserialize_serialization_block(
                json_element
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")

    @staticmethod
    def deserialize_serialization_block_from_file(file_path: str) -> SerializedChunk:
        try:
            with open(file_path, "r") as file:
                json_element = json.load(file)
                return LowLevelJsonSerialization.deserialize_serialization_block(
                    json_element
                )
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in file: {e}")

    @staticmethod
    def check_no_extra_keys(json_object: dict, expected_keys: set):
        extra_keys = set(json_object.keys()) - expected_keys
        if extra_keys:
            raise ValueError(
                f"Extra keys found: {extra_keys}. Expected keys: {expected_keys}"
            )

    @staticmethod
    def require_is_string(value, desc: str):
        if not isinstance(value, str):
            raise ValueError(f"{desc} should be a string value")
