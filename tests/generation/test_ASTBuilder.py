import ast
import unittest

from lionweb.generation.ASTBuilder import ASTBuilder


class ASTBuilderTest(unittest.TestCase):

    def setUp(self):
        self.builder = ASTBuilder()

    def test_name_creates_name_node(self):
        result = self.builder.name("my_var")
        self.assertIsInstance(result, ast.Name)
        self.assertEqual(result.id, "my_var")
        self.assertIsInstance(result.ctx, ast.Load)

    def test_name_with_custom_context(self):
        result = self.builder.name("my_var", ctx=ast.Store())
        self.assertIsInstance(result, ast.Name)
        self.assertEqual(result.id, "my_var")
        self.assertIsInstance(result.ctx, ast.Store)

    def test_name_raises_on_none_id(self):
        with self.assertRaises(ValueError) as cm:
            self.builder.name(None)
        self.assertEqual(str(cm.exception), "id must not be None")

    def test_const_creates_constant_node(self):
        result = self.builder.const(42)
        self.assertIsInstance(result, ast.Constant)
        self.assertEqual(result.value, 42)

    def test_const_with_string(self):
        result = self.builder.const("hello")
        self.assertIsInstance(result, ast.Constant)
        self.assertEqual(result.value, "hello")

    def test_const_with_none(self):
        result = self.builder.const(None)
        self.assertIsInstance(result, ast.Constant)
        self.assertIsNone(result.value)

    def test_attr_with_string_value(self):
        result = self.builder.attr("obj", "method")
        self.assertIsInstance(result, ast.Attribute)
        self.assertEqual(result.attr, "method")
        self.assertIsInstance(result.value, ast.Name)
        self.assertEqual(result.value.id, "obj")
        self.assertIsInstance(result.ctx, ast.Load)

    def test_attr_with_ast_node_value(self):
        name_node = self.builder.name("obj")
        result = self.builder.attr(name_node, "method")
        self.assertIsInstance(result, ast.Attribute)
        self.assertEqual(result.attr, "method")
        self.assertIs(result.value, name_node)

    def test_attr_with_custom_context(self):
        result = self.builder.attr("obj", "attr", ctx=ast.Store())
        self.assertIsInstance(result, ast.Attribute)
        self.assertIsInstance(result.ctx, ast.Store)

    def test_attr_raises_on_none_attr(self):
        with self.assertRaises(ValueError) as cm:
            self.builder.attr("obj", None)
        self.assertEqual(str(cm.exception), "attr must not be None")

    def test_call_with_string_func(self):
        result = self.builder.call("my_func")
        self.assertIsInstance(result, ast.Call)
        self.assertIsInstance(result.func, ast.Name)
        self.assertEqual(result.func.id, "my_func")
        self.assertEqual(result.args, [])
        self.assertEqual(result.keywords, [])

    def test_call_with_ast_node_func(self):
        func_node = self.builder.attr("obj", "method")
        result = self.builder.call(func_node)
        self.assertIsInstance(result, ast.Call)
        self.assertIs(result.func, func_node)

    def test_call_with_args(self):
        arg1 = self.builder.const(42)
        arg2 = self.builder.const("hello")
        result = self.builder.call("my_func", args=[arg1, arg2])
        self.assertIsInstance(result, ast.Call)
        self.assertEqual(len(result.args), 2)
        self.assertIs(result.args[0], arg1)
        self.assertIs(result.args[1], arg2)

    def test_call_with_keywords(self):
        result = self.builder.call(
            "my_func",
            keywords={
                "param1": self.builder.const(42),
                "param2": self.builder.const("hello"),
            },
        )
        self.assertIsInstance(result, ast.Call)
        self.assertEqual(len(result.keywords), 2)
        self.assertEqual(result.keywords[0].arg, "param1")
        self.assertEqual(result.keywords[0].value.value, 42)
        self.assertEqual(result.keywords[1].arg, "param2")
        self.assertEqual(result.keywords[1].value.value, "hello")

    def test_call_filters_none_keywords(self):
        result = self.builder.call(
            "my_func",
            keywords={
                "param1": self.builder.const(42),
                "param2": None,
                "param3": self.builder.const("hello"),
            },
        )
        self.assertIsInstance(result, ast.Call)
        self.assertEqual(len(result.keywords), 2)
        self.assertEqual(result.keywords[0].arg, "param1")
        self.assertEqual(result.keywords[1].arg, "param3")

    def test_call_with_args_and_keywords(self):
        arg = self.builder.const(1)
        result = self.builder.call(
            "my_func", args=[arg], keywords={"key": self.builder.const(2)}
        )
        self.assertIsInstance(result, ast.Call)
        self.assertEqual(len(result.args), 1)
        self.assertEqual(len(result.keywords), 1)

    def test_assign_creates_assignment(self):
        value = self.builder.const(42)
        result = self.builder.assign("x", value)
        self.assertIsInstance(result, ast.Assign)
        self.assertEqual(len(result.targets), 1)
        self.assertIsInstance(result.targets[0], ast.Name)
        self.assertEqual(result.targets[0].id, "x")
        self.assertIsInstance(result.targets[0].ctx, ast.Store)
        self.assertIs(result.value, value)

    def test_complex_nested_expression(self):
        # Build: obj.method(arg1, arg2, key=value)
        result = self.builder.call(
            self.builder.attr("obj", "method"),
            args=[self.builder.const(1), self.builder.const(2)],
            keywords={"key": self.builder.const("value")},
        )
        self.assertIsInstance(result, ast.Call)
        self.assertIsInstance(result.func, ast.Attribute)
        self.assertEqual(result.func.attr, "method")


if __name__ == "__main__":
    unittest.main()
