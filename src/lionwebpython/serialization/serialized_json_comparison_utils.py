from typing import Dict, List, cast

from lionwebpython.serialization.json_utils import JsonArray, JsonObject


class SerializedJsonComparisonUtils:

    @staticmethod
    def assert_equivalent_lionweb_json(expected: JsonObject, actual: JsonObject):
        keys = {"serializationFormatVersion", "nodes", "languages"}
        if set(expected.keys()) != keys:
            raise RuntimeError(
                f"The expected object has irregular keys: {expected.keys()}"
            )
        if set(actual.keys()) != keys:
            raise RuntimeError(f"The actual object has irregular keys: {actual.keys()}")

        SerializedJsonComparisonUtils.assert_equals(
            "serializationFormatVersion",
            expected.get("serializationFormatVersion"),
            actual.get("serializationFormatVersion"),
        )
        SerializedJsonComparisonUtils.assert_equivalent_lionweb_json_nodes(
            cast(JsonArray, expected.get("nodes")), cast(JsonArray, actual.get("nodes"))
        )
        SerializedJsonComparisonUtils.assert_equivalent_lionweb_json_languages(
            cast(JsonArray, expected.get("languages")),
            cast(JsonArray, actual.get("languages")),
        )

    @staticmethod
    def assert_equivalent_lionweb_json_languages(
        expected_languages: JsonArray, actual_languages: JsonArray
    ) -> None:
        if len(expected_languages) != len(actual_languages):
            raise AssertionError(
                f"Expected {len(expected_languages)} languages, but found {len(actual_languages)}. Actual languages: {actual_languages}"
            )

        expected_versions = {
            cast(Dict, lang)["key"]: cast(Dict, lang)["version"]
            for lang in expected_languages
        }
        actual_versions = {
            cast(Dict, lang)["key"]: cast(Dict, lang)["version"]
            for lang in actual_languages
        }

        if expected_versions != actual_versions:
            raise AssertionError(
                f"Used languages do not match: expected {expected_versions}, got {actual_versions}"
            )

    @staticmethod
    def assert_equivalent_lionweb_json_nodes(expected: JsonArray, actual: JsonArray):
        expected_elements = {(cast(JsonObject, e))["id"]: e for e in expected}
        actual_elements = {(cast(JsonObject, e))["id"]: e for e in actual}

        unexpected_ids = set(actual_elements.keys()) - set(expected_elements.keys())
        missing_ids = set(expected_elements.keys()) - set(actual_elements.keys())

        if unexpected_ids:
            raise AssertionError(f"Unexpected IDs found: {unexpected_ids}")
        if missing_ids:
            raise AssertionError(f"Missing IDs found: {missing_ids}")

        SerializedJsonComparisonUtils.assert_equals(
            "The number of nodes is different", len(expected), len(actual)
        )

        for node_id in expected_elements:
            expected_node = cast(JsonObject, expected_elements[node_id])
            actual_node = cast(JsonObject, actual_elements[node_id])
            SerializedJsonComparisonUtils.assert_equivalent_nodes(
                expected_node, actual_node, f"Node {node_id}"
            )

    @staticmethod
    def assert_equivalent_nodes(expected: dict, actual: dict, context: str):
        actual_keys = set(actual.keys())
        expected_keys = set(expected.keys())

        # Remove null 'parent' keys
        if "parent" in actual and actual["parent"] is None:
            actual_keys.remove("parent")
        if "parent" in expected and expected["parent"] is None:
            expected_keys.remove("parent")

        unexpected_keys = actual_keys - expected_keys
        missing_keys = expected_keys - actual_keys

        if unexpected_keys:
            raise AssertionError(
                f"({context}) Unexpected keys found: {unexpected_keys}"
            )
        if missing_keys:
            raise AssertionError(f"({context}) Missing keys found: {missing_keys}")

        for key in actual_keys:
            if key in {"parent", "classifier", "id"}:
                SerializedJsonComparisonUtils.assert_equals(
                    f"({context}) different {key}", expected.get(key), actual.get(key)
                )
            elif key in {"references", "containments", "properties", "annotations"}:
                SerializedJsonComparisonUtils.assert_equivalent_unordered_arrays(
                    expected.get(key, []),
                    actual.get(key, []),
                    f"{key.capitalize()} of {context}",
                )
            else:
                raise AssertionError(
                    f"({context}) unexpected top-level key found: {key}"
                )

    @staticmethod
    def assert_equivalent_unordered_arrays(
        expected: List[dict], actual: List[dict], context: str
    ):
        if len(expected) != len(actual):
            raise AssertionError(
                f"({context}) Arrays with different sizes: expected={len(expected)} and actual={len(actual)}"
            )

        consumed_actual = set()
        for expected_element in expected:
            match_found = False
            for i, actual_element in enumerate(actual):
                if (
                    i not in consumed_actual
                    and SerializedJsonComparisonUtils.are_equivalent_objects(
                        expected_element, actual_element
                    )
                ):
                    consumed_actual.add(i)
                    match_found = True
                    break
            if not match_found:
                SerializedJsonComparisonUtils.fail(
                    f"{context} element {expected_element} not found"
                )

    @staticmethod
    def are_equivalent_objects(expected: dict, actual: dict) -> bool:
        try:
            SerializedJsonComparisonUtils.assert_equivalent_objects(
                expected, actual, "<IRRELEVANT>"
            )
            return True
        except AssertionError:
            return False

    @staticmethod
    def assert_equivalent_objects(expected: dict, actual: dict, context: str):
        actual_meaningful_keys = {
            k for k, v in actual.items() if v not in ({}, [], None)
        }
        expected_meaningful_keys = {
            k for k, v in expected.items() if v not in ({}, [], None)
        }

        unexpected_keys = actual_meaningful_keys - expected_meaningful_keys
        missing_keys = expected_meaningful_keys - actual_meaningful_keys

        if unexpected_keys:
            raise AssertionError(
                f"({context}) Unexpected keys found: {unexpected_keys}"
            )
        if missing_keys:
            raise AssertionError(f"({context}) Missing keys found: {missing_keys}")

        for key in actual_meaningful_keys:
            SerializedJsonComparisonUtils.assert_equals(
                f"({context}) Different values for key {key}",
                expected.get(key),
                actual.get(key),
            )

    @staticmethod
    def assert_equals(message: str, expected, actual):
        if expected != actual:
            raise AssertionError(f"{message}: expected {expected} but found {actual}")

    @staticmethod
    def fail(message: str):
        raise AssertionError(f"Comparison failed. {message}")
