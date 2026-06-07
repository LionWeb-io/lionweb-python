import ast
import keyword
import re
from typing import cast

from lionweb.language import Feature


def dotted_name_expr(dotted: str) -> ast.expr:
    """Turn 'my.package.name' into an AST expr representing that dotted access."""
    if len(dotted) == 0:
        raise ValueError(f"Invalid dotted name (empty): {dotted!r}")
    parts = dotted.split(".")
    if not parts or any(not p for p in parts):
        raise ValueError(f"Invalid dotted name: {dotted!r}")

    node: ast.expr = ast.Name(id=parts[0], ctx=ast.Load())
    for part in parts[1:]:
        node = ast.Attribute(value=node, attr=part, ctx=ast.Load())
    return node


def calculate_field_name(feature: Feature) -> str:
    """Compute the Python field name for a LionWeb feature.

    Appends a trailing underscore if the feature's name collides with a
    Python keyword.

    Args:
        feature: The feature whose field name should be computed.

    Returns:
        str: A Python-safe field name.
    """
    field_name = cast(str, feature.get_name())
    if field_name in keyword.kwlist:
        field_name = f"{field_name}_"
    return field_name


def to_snake_case(name: str | None) -> str:
    """Convert a CamelCase/PascalCase name to snake_case.

    Args:
        name: The name to convert (must not be None or empty).

    Returns:
        str: The snake_case version of the name.

    Raises:
        ValueError: If `name` is None or empty.
    """
    if not name:
        raise ValueError("Name should not be None")
    # Replace capital letters with _lowercase, except at the beginning
    name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return name.lower()


def to_var_name(name: str | None) -> str:
    """Convert a name to snake_case while avoiding Python keywords.

    Args:
        name: The name to convert (must not be None).

    Returns:
        str: A snake_case identifier safe to use as a Python variable name,
        with a trailing underscore appended if it would otherwise be a keyword.

    Raises:
        ValueError: If `name` is None.
    """
    import keyword
    import re

    if name is None:
        raise ValueError("Name should not be None")

    # Convert to snake_case
    # Insert underscore before uppercase letters
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    # Insert underscore before uppercase letters that follow lowercase letters or numbers
    snake_case = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    # If the result is a Python keyword, append an underscore
    if keyword.iskeyword(snake_case):
        snake_case += "_"

    return snake_case


def to_type_name(name: str | None) -> str:
    """Convert a name to a Python type/class name by capitalizing its first letter.

    Args:
        name: The name to convert (must not be None).

    Returns:
        str: The name with its first letter capitalized.

    Raises:
        ValueError: If `name` is None.
    """
    if name is None:
        raise ValueError("Name should not be None")
    return name[0].upper() + name[1:]


def getter_name(name: str | None) -> str:
    """Compute the conventional getter method name (`get_<snake_case_name>`) for a feature name.

    Args:
        name: The feature name (must not be None).

    Returns:
        str: The getter method name.

    Raises:
        ValueError: If `name` is None.
    """
    if name is None:
        raise ValueError("Name should not be None")
    return f"get_{to_snake_case(name)}"
