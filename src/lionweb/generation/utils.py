import ast
import keyword
import re
import sys
from typing import Any, List, Optional, cast

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


def make_class_def(
    name: str, bases: List[ast.expr], body: List[ast.stmt]
) -> ast.ClassDef:
    if sys.version_info >= (3, 12):
        return ast.ClassDef(
            name=name,
            bases=bases,
            keywords=[],
            body=body,
            decorator_list=[],
            type_params=[],  # Only valid from Python 3.12+
        )
    else:
        return ast.ClassDef(
            name=name, bases=bases, keywords=[], body=body, decorator_list=[]
        )


def make_function_def(
    name: str,
    args: ast.arguments,
    body: List[ast.stmt],
    decorator_list: Optional[List[ast.expr]] = None,
    returns: Optional[ast.expr] = None,
) -> ast.FunctionDef:
    decorator_list = decorator_list or []

    if sys.version_info >= (3, 12):
        return ast.FunctionDef(
            name=name,
            args=args,
            body=body,
            decorator_list=decorator_list,
            returns=returns,
            type_comment=None,
            type_params=cast(List[Any], []),
        )
    else:
        return ast.FunctionDef(
            name=name,
            args=args,
            body=body,
            decorator_list=decorator_list,
            returns=returns,
            type_comment=None,
        )
