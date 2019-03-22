import unittest
from tree_sitter import Parser, Language


LIB_PATH = "build/languages.so"
Language.build_library(LIB_PATH, [
    "tests/fixtures/tree-sitter-python",
    "tests/fixtures/tree-sitter-javascript",
])
PYTHON = Language(LIB_PATH, "python")
JAVASCRIPT = Language(LIB_PATH, "javascript")


class TestTreeSitter(unittest.TestCase):
    def test_set_language(self):
        parser = Parser()
        parser.set_language(PYTHON)
        tree = parser.parse("def foo():\n  bar()")
        self.assertEqual(
            tree.root_node.sexp(),
            "(module (function_definition (identifier) (parameters) (expression_statement (call (identifier) (argument_list)))))"
        )
        parser.set_language(JAVASCRIPT)
        tree = parser.parse("function foo() {\n  bar();\n}")
        self.assertEqual(
            tree.root_node.sexp(),
            "(program (function (identifier) (formal_parameters) (statement_block (expression_statement (call_expression (identifier) (arguments))))))"
        )

    def test_node_children(self):
        parser = Parser()
        parser.set_language(PYTHON)
        tree = parser.parse("def foo():\n  bar()")

        root_node = tree.root_node
        self.assertEqual(root_node.type, "module")
        self.assertEqual(root_node.start_byte, 0)
        self.assertEqual(root_node.end_byte, 18)
        self.assertEqual(root_node.start_point, (0, 0))
        self.assertEqual(root_node.end_point, (1, 7))

        # List object is reused
        self.assertIs(root_node.children, root_node.children)

        fn_node = root_node.children[0]
        self.assertEqual(fn_node.type, "function_definition")
        self.assertEqual(fn_node.start_byte, 0)
        self.assertEqual(fn_node.end_byte, 18)
        self.assertEqual(fn_node.start_point, (0, 0))
        self.assertEqual(fn_node.end_point, (1, 7))

        def_node = fn_node.children[0]
        self.assertEqual(def_node.type, "def")
        self.assertEqual(def_node.is_named, False)

        id_node = fn_node.children[1]
        self.assertEqual(id_node.type, "identifier")
        self.assertEqual(id_node.is_named, True)
        self.assertEqual(len(id_node.children), 0)

        params_node = fn_node.children[2]
        self.assertEqual(params_node.type, "parameters")
        self.assertEqual(params_node.is_named, True)

        colon_node = fn_node.children[3]
        self.assertEqual(colon_node.type, ":")
        self.assertEqual(colon_node.is_named, False)

        statement_node = fn_node.children[4]
        self.assertEqual(statement_node.type, "expression_statement")
        self.assertEqual(statement_node.is_named, True)
