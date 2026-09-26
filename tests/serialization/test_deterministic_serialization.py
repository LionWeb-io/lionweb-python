import os
import subprocess
import sys
import unittest

SRC_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "src"
)

# Serializes the LionCore language (a tree with many nodes) in both formats
SERIALIZE_TREE = """
import sys
from lionweb.self.lioncore import LionCore
from lionweb.serialization import (
    create_standard_json_serialization,
    create_standard_protobuf_serialization,
)

language = LionCore.get_language()
sys.stdout.write(create_standard_json_serialization().serialize_tree_to_json_string(language))
sys.stdout.write("\\n")
chunk = create_standard_protobuf_serialization().serialize_tree(language)
sys.stdout.write(chunk.SerializeToString(deterministic=True).hex())
"""


class DeterministicSerializationTest(unittest.TestCase):
    """Serializing the same tree must give the same output in every process.

    The order of the nodes used to depend on Python's hash randomization, so it
    changed from run to run: each serialization runs in a fresh interpreter with a
    different PYTHONHASHSEED.
    """

    def _serialize_with_hash_seed(self, seed: str) -> str:
        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join(filter(None, [SRC_DIR, env.get("PYTHONPATH")]))
        env["PYTHONHASHSEED"] = seed
        result = subprocess.run(
            [sys.executable, "-c", SERIALIZE_TREE],
            env=env,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_serialize_tree_output_does_not_depend_on_hash_seed(self):
        outputs = {self._serialize_with_hash_seed(seed) for seed in ["1", "2", "3"]}
        self.assertEqual(len(outputs), 1)


if __name__ == "__main__":
    unittest.main()
