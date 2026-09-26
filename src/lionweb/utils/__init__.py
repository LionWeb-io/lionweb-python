from typing import TYPE_CHECKING, Any

from .id_utils import clean_string_as_id, is_valid_id
from .issue import Issue
from .issue_severity import IssueSeverity
from .node_navigation import root

if TYPE_CHECKING:
    from .language_validator import InvalidLanguageError, LanguageValidator

__all__ = [
    "is_valid_id",
    "clean_string_as_id",
    "Issue",
    "IssueSeverity",
    "InvalidLanguageError",
    "LanguageValidator",
    "root",
]


def __getattr__(name: str) -> Any:
    # language_validator depends on lionweb.language, which in turn (through
    # lionweb.model) imports this package: loading it eagerly makes
    # `import lionweb.language` fail with a circular import.
    if name in ("InvalidLanguageError", "LanguageValidator"):
        from . import language_validator

        return getattr(language_validator, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
