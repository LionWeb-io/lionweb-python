import re

_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")


def is_valid_id(id: str | None) -> bool:
    if id is None:
        return False
    return _ID_PATTERN.fullmatch(id) is not None


def clean_string_as_id(string: str) -> str:
    return string.replace(".", "-")
