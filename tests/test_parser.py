import unittest

import tests  # noqa: F401
from grammar import GRAMMAR
from lexer import tokenize
from parser import parse


def run(source):
    tokens, _ = tokenize(source)
    tree, diags = parse(tokens)
    return tree, [(d.line, d.message) for d in diags], tokens


def leaves(node):
    if not node.children:
        return [node.token] if node.token is not None else []
    return [t for child in node.children for t in leaves(child)]


def depth_of_token(node, lexeme, depth=0):
    """How many levels below the root the leaf holding `lexeme` is (None if absent)."""
    if node.token is not None and node.token.lexeme == lexeme:
        return depth
    for child in node.children:
        found = depth_of_token(child, lexeme, depth + 1)
        if found is not None:
            return found
    return None


def count_nonterminals(node):
    own = 1 if node.label in GRAMMAR else 0
    return own + sum(count_nonterminals(c) for c in node.children)


class ParserAcceptsTests(unittest.TestCase):
    def test_valid_program_is_accepted(self):
        from tests import read_sample
        tree, errors, _ = run(read_sample("valid.txt"))
        self.assertIsNotNone(tree)
        self.assertEqual(errors, [])

    def test_empty_program_is_accepted(self):
        tree, errors, _ = run("# nothing\n")
        self.assertIsNotNone(tree)
        self.assertEqual(errors, [])

    def test_tree_leaves_are_exactly_the_tokens_in_order(self):
        from tests import read_sample
        tree, _, tokens = run(read_sample("valid.txt"))
        self.assertEqual(leaves(tree), tokens)

    def test_derivation_of_a_declaration_has_13_steps(self):
        tree, _, _ = run("int x = 10;")
        self.assertEqual(count_nonterminals(tree), 13)

    def test_tree_drawing_of_a_declaration_has_22_lines(self):
        tree, _, _ = run("int x = 10;")
        lines = tree.draw()
        self.assertEqual(len(lines), 22)
        self.assertEqual(lines[0], "Program")
        self.assertIn("intnum  '10'", "".join(lines))

    def test_char_literal_is_drawn_with_single_quotes_only(self):
        tree, _, _ = run("char c = 'a';")
        text = "\n".join(tree.draw())
        self.assertIn("charlit  'a'", text)
        self.assertNotIn("''a''", text)

    def test_operator_priority_is_in_the_tree(self):
        # in  1 + 2 * 3  the multiplication must sit deeper in the tree than the addition,
        # because it is evaluated first. (Checks the tree structure, not how it is printed.)
        tree, _, _ = run("int a = 1 + 2 * 3;")
        self.assertGreater(depth_of_token(tree, "*"), depth_of_token(tree, "+"))

    def test_parentheses_and_nested_blocks(self):
        src = "int a = (1 + 2) * 3;\nwhile (a > 0) {\n if (a == 1) { a = a - 1; }\n}"
        tree, errors, _ = run(src)
        self.assertIsNotNone(tree)
        self.assertEqual(errors, [])

    def test_multiple_declarators(self):
        tree, errors, _ = run("int i, j = 2, k;")
        self.assertIsNotNone(tree)
        self.assertEqual(errors, [])


class ParserRejectsTests(unittest.TestCase):
    def check(self, source, line, text):
        tree, errors, _ = run(source)
        self.assertIsNone(tree)
        self.assertEqual(len(errors), 1, errors)       # the parser stops at the first error
        self.assertEqual(errors[0][0], line)
        self.assertIn(text, errors[0][1])

    def test_missing_semicolon_is_reported_on_its_own_line(self):
        self.check("int num1 = 10\nfloat num2 = 3.5;", 1, "missing ';'")

    def test_missing_semicolon_at_end_of_file(self):
        self.check("int a = 1", 1, "missing ';'")

    def test_missing_closing_parenthesis(self):
        self.check("int n = 1;\nwhile (n < 3 { n = n + 1; }", 2, "unexpected '{'")

    def test_extra_closing_brace(self):
        self.check("int n = 1;\n}", 2, "unexpected '}' after end of program")

    def test_missing_closing_brace_at_end_of_file(self):
        self.check("int n = 1;\nwhile (n < 3) {\n n = n + 1;\n", 3, "expected '}'")

    def test_else_without_if(self):
        self.check("int n = 1;\nelse { n = 2; }", 2, "unexpected 'else'")

    def test_if_without_braces(self):
        self.check("int n = 1;\nif (n > 1)\n    n = 2;\n", 3, "unexpected 'n'")

    def test_condition_needs_a_comparison(self):
        self.check("int n = 1;\nif (n) { n = 2; }", 2, "unexpected ')'")

    def test_statement_cannot_start_with_a_number(self):
        self.check("5 = x;", 1, "unexpected '5'")


if __name__ == "__main__":
    unittest.main()
