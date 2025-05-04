import keyword
import re
from typing import Optional, cast

from lionweb.language import Feature


def calculate_field_name(feature: Feature) -> str:
    field_name = cast(str, feature.get_name())
    if field_name in keyword.kwlist:
        field_name = f"{field_name}_"
    return field_name


def to_snake_case(name: Optional[str]) -> str:
    if not name:
        raise ValueError("Name should not be None")
    # Replace capital letters with _lowercase, except at the beginning
    name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return name.lower()
