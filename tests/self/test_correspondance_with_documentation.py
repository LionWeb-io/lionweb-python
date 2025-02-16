import unittest

import requests

from lionwebpython.language.lioncore_builtins import LionCoreBuiltins
from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.self.lioncore import LionCore
from lionwebpython.serialization.serialization_provider import \
    SerializationProvider
from lionwebpython.utils.model_comparator import ModelComparator


class CorrespondenceWithDocumentationTest(unittest.TestCase):

    SPECIFICATION_2023_1_COMMIT_CONSIDERED = "73b1c88e8e8f365c76bcf13340da310ed74d5f8e"
    SPECIFICATION_2024_1_COMMIT_CONSIDERED = "73b1c88e8e8f365c76bcf13340da310ed74d5f8e"

    SPECIFICATION_LIONCORE_2023_1_PATH = "/2023.1/metametamodel/lioncore.json"
    SPECIFICATION_LIONCORE_2024_1_PATH = "/2024.1/metametamodel/lioncore.json"
    SPECIFICATION_LIONCOREBUILTINS_2023_1_PATH = "/2023.1/metametamodel/builtins.json"
    SPECIFICATION_LIONCOREBUILTINS_2024_1_PATH = "/2024.1/metametamodel/builtins.json"

    def test_lioncore_same_as_repo_2023_1(self):
        json_ser = SerializationProvider.get_standard_json_serialization(
            LionWebVersion.V2023_1
        )

        url = (
            f"https://raw.githubusercontent.com/LionWeb-io/specification/"
            f"{self.SPECIFICATION_2023_1_COMMIT_CONSIDERED}"
            f"{self.SPECIFICATION_LIONCORE_2023_1_PATH}"
        )
        response = requests.get(url)
        response.raise_for_status()
        nodes = json_ser.deserialize_string_to_nodes(response.text)

        deserialized_lioncore = nodes[0]
        comparison = ModelComparator().compare(
            deserialized_lioncore, LionCore.get_instance(LionWebVersion.V2023_1)
        )
        print(f"Differences: {len(comparison.differences)}")
        for diff in comparison.differences:
            print(f" - {diff}")
        self.assertTrue(comparison.are_equivalent, comparison)

    def test_lioncore_same_as_repo_2024_1(self):
        json_ser = SerializationProvider.get_standard_json_serialization(
            LionWebVersion.V2024_1
        )

        url = (
            f"https://raw.githubusercontent.com/LionWeb-io/specification/"
            f"{self.SPECIFICATION_2024_1_COMMIT_CONSIDERED}"
            f"{self.SPECIFICATION_LIONCORE_2024_1_PATH}"
        )
        response = requests.get(url)
        response.raise_for_status()
        nodes = json_ser.deserialize_string_to_nodes(response.text)

        deserialized_lioncore = nodes[0]
        comparison = ModelComparator().compare(
            deserialized_lioncore, LionCore.get_instance(LionWebVersion.V2024_1)
        )
        print(f"Differences: {len(comparison.differences)}")
        for diff in comparison.differences:
            print(f" - {diff}")
        self.assertTrue(comparison.are_equivalent, comparison)

    def test_builtins_same_as_repo_2023_1(self):
        json_ser = SerializationProvider.get_standard_json_serialization(
            LionWebVersion.V2023_1
        )

        url = (
            f"https://raw.githubusercontent.com/LionWeb-io/specification/"
            f"{self.SPECIFICATION_2023_1_COMMIT_CONSIDERED}"
            f"{self.SPECIFICATION_LIONCOREBUILTINS_2023_1_PATH}"
        )
        response = requests.get(url)
        response.raise_for_status()
        nodes = json_ser.deserialize_string_to_nodes(response.text)

        deserialized_builtins = nodes[0]
        comparison = ModelComparator().compare(
            deserialized_builtins, LionCoreBuiltins.get_instance(LionWebVersion.V2023_1)
        )
        print(f"Differences: {len(comparison.differences)}")
        for diff in comparison.differences:
            print(f" - {diff}")
        self.assertTrue(comparison.are_equivalent, comparison)

    def test_builtins_same_as_repo_2024_1(self):
        json_ser = SerializationProvider.get_standard_json_serialization(
            LionWebVersion.V2024_1
        )

        url = (
            f"https://raw.githubusercontent.com/LionWeb-io/specification/"
            f"{self.SPECIFICATION_2024_1_COMMIT_CONSIDERED}"
            f"{self.SPECIFICATION_LIONCOREBUILTINS_2024_1_PATH}"
        )
        response = requests.get(url)
        response.raise_for_status()
        nodes = json_ser.deserialize_string_to_nodes(response.text)

        deserialized_builtins = nodes[0]
        comparison = ModelComparator().compare(
            deserialized_builtins, LionCoreBuiltins.get_instance(LionWebVersion.V2024_1)
        )
        print(f"Differences: {len(comparison.differences)}")
        for diff in comparison.differences:
            print(f" - {diff}")
        self.assertTrue(comparison.are_equivalent, comparison)


if __name__ == "__main__":
    unittest.main()
