import os
import subprocess
import sys
import unittest

SRC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")

MODULES = [
    "lionweb",
    "lionweb.api",
    "lionweb.autoresolve",
    "lionweb.generation",
    "lionweb.language",
    "lionweb.lionweb_version",
    "lionweb.model",
    "lionweb.self.lioncore",
    "lionweb.serialization",
    "lionweb.utils",
]


class ImportsTest(unittest.TestCase):
    """Verifies there are no circular imports between the lionweb packages.

    Each package is imported first, in a fresh interpreter: an import cycle can
    go unnoticed in the rest of the suite, where modules are already loaded in
    an order that happens to work.
    """

    def test_each_package_can_be_imported_first(self):
        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join(filter(None, [SRC_DIR, env.get("PYTHONPATH")]))
        for module in MODULES:
            with self.subTest(module=module):
                result = subprocess.run(
                    [sys.executable, "-c", f"import {module}"],
                    env=env,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
