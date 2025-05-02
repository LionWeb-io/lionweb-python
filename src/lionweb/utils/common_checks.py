import re

from typing_extensions import Optional


class CommonChecks:
    _ID_PATTERN = re.compile("^[a-zA-Z0-9_-]+$")

    @staticmethod
    def is_valid_id(id: Optional[str]) -> bool:
        if id is None:
            return False
        m = CommonChecks._ID_PATTERN.fullmatch(id)
        return m is not None
