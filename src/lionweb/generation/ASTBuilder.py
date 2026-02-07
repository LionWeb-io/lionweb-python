import ast
from typing import Optional


class ASTBuilder:
    """Helper mixin to reduce ast verbosity."""

    def name(self, id: Optional[str], ctx=None) -> ast.Name:
        if id is None:
            raise ValueError("id must not be None")
        return ast.Name(id=id, ctx=ctx or ast.Load())

    def const(self, value) -> ast.Constant:
        return ast.Constant(value=value)

    def attr(self, value, attr: Optional[str], ctx=None) -> ast.Attribute:
        if attr is None:
            raise ValueError("attr must not be None")
        # value can be a string (implies a Name node) or an AST node
        if isinstance(value, str):
            value = self.name(value)
        return ast.Attribute(value=value, attr=attr, ctx=ctx or ast.Load())

    def call(self, func, args=None, keywords=None) -> ast.Call:
        """Creates a function call.
        'func' can be a string (function name) or an AST node.
        'keywords' is a dict of {arg_name: ast_node}.
        """
        if isinstance(func, str):
            func = self.name(func)

        ast_keywords = []
        if keywords:
            for k, v in keywords.items():
                if v is None:
                    continue
                ast_keywords.append(ast.keyword(arg=k, value=v))

        return ast.Call(func=func, args=args or [], keywords=ast_keywords)

    def assign(self, target_id: str, value) -> ast.Assign:
        return ast.Assign(targets=[self.name(target_id, ctx=ast.Store())], value=value)
