import ast
import sys
from typing import Any, cast


def make_class_def(name: str, bases: list[ast.expr], body: list[ast.stmt]) -> ast.ClassDef:
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
        return ast.ClassDef(name=name, bases=bases, keywords=[], body=body, decorator_list=[])


def make_function_def(
    name: str | None,
    args: ast.arguments,
    body: list[ast.stmt],
    decorator_list: list[ast.expr] | None = None,
    returns: ast.expr | None = None,
) -> ast.FunctionDef:
    if name is None:
        raise ValueError("Name should not be None")

    decorator_list = decorator_list or []

    if sys.version_info >= (3, 12):
        return ast.FunctionDef(
            name=name,
            args=args,
            body=body,
            decorator_list=decorator_list,
            returns=returns,
            type_comment=None,
            type_params=cast(list[Any], []),
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
