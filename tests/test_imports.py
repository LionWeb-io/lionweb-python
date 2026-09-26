import os
import subprocess
import sys
import unittest

SRC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")

MODULES = [
    "lionweb",
    "lionweb.api",
    "lionweb.generation",
    "lionweb.language",
    "lionweb.lionweb_version",
    "lionweb.model",
    "lionweb.self.lioncore",
    "lionweb.serialization",
    "lionweb.utils",
]


class ImportsTest(unittest.TestCase):
    """Each package must be importable first, in a fresh interpreter."""

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

    def test_lazy_utils_exports(self):
        from lionweb.utils import InvalidLanguageError, LanguageValidator
        from lionweb.utils.language_validator import (
            InvalidLanguageError as DirectInvalidLanguageError,
        )
        from lionweb.utils.language_validator import LanguageValidator as DirectLanguageValidator

        self.assertIs(LanguageValidator, DirectLanguageValidator)
        self.assertIs(InvalidLanguageError, DirectInvalidLanguageError)


if __name__ == "__main__":
    unittest.main()
