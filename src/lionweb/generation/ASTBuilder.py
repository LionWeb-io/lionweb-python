import ast


class ASTBuilder:
    """Helper mixin to reduce ast verbosity."""

    def name(self, id: str | None, ctx=None) -> ast.Name:
        """Build an `ast.Name` node.

        Args:
            id: The identifier name (must not be None).
            ctx: The expression context to use; defaults to `ast.Load()`.

        Returns:
            ast.Name: The constructed name node.

        Raises:
            ValueError: If `id` is None.
        """
        if id is None:
            raise ValueError("id must not be None")
        return ast.Name(id=id, ctx=ctx or ast.Load())

    def const(self, value) -> ast.Constant:
        """Build an `ast.Constant` node wrapping the given value."""
        return ast.Constant(value=value)

    def attr(self, value, attr: str | None, ctx=None) -> ast.Attribute:
        """Build an `ast.Attribute` access node (e.g. `value.attr`).

        Args:
            value: Either a string (interpreted as a name) or an existing AST node.
            attr: The attribute name to access (must not be None).
            ctx: The expression context to use; defaults to `ast.Load()`.

        Returns:
            ast.Attribute: The constructed attribute-access node.

        Raises:
            ValueError: If `attr` is None.
        """
        if attr is None:
            raise ValueError("attr must not be None")
        # value can be a string (implies a Name node) or an AST node
        if isinstance(value, str):
            value = self.name(value)
        return ast.Attribute(value=value, attr=attr, ctx=ctx or ast.Load())

    def call(self, func, args=None, keywords=None) -> ast.Call:
        """Build an `ast.Call` node representing a function call.

        Args:
            func: Either a string (function name) or an existing AST node
                representing the callee.
            args: Positional argument AST nodes.
            keywords: A dict of `{arg_name: ast_node}` mapping keyword argument
                names to their value expressions; entries with a None value are
                skipped.

        Returns:
            ast.Call: The constructed call node.
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
        """Build an `ast.Assign` node assigning `value` to a single named target."""
        return ast.Assign(targets=[self.name(target_id, ctx=ast.Store())], value=value)
