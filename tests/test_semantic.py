import unittest

import tests  # noqa: F401
from pipeline import compile_source


def analyze(source):
    """(kind, line, message) for every diagnostic of a program that passes lexing and parsing."""
    result = compile_source(source)
    assert result.stage == "semantic", f"program did not reach the semantic phase: {result.diagnostics.items}"
    return [(d.kind, d.line, d.message) for d in result.diagnostics.sorted()], result


class SemanticChecksTests(unittest.TestCase):
    def messages(self, source):
        return analyze(source)[0]

    # ---- errors -------------------------------------------------------------------------
    def test_1_undeclared_variable_on_the_right(self):
        self.assertIn(("semantic", 2, "variable 'k' is not declared"),
                      self.messages("int i = 0;\ni = i + k;"))

    def test_1_undeclared_variable_on_the_left(self):
        self.assertIn(("semantic", 1, "variable 'z' is not declared"), self.messages("z = 3;"))

    def test_2_duplicate_declaration_in_one_scope(self):
        self.assertIn(("semantic", 2, "variable 'a' is already declared in this scope (line 1)"),
                      self.messages("int a;\nint a;"))

    def test_2_same_declaration_in_an_inner_scope_is_fine(self):
        msgs = self.messages("int a = 1;\nif (a > 0) {\n int a = 2;\n a = a + 1;\n}")
        self.assertEqual([m for m in msgs if m[0] == "semantic"], [])

    def test_3_assign_float_to_int(self):
        self.assertIn(("semantic", 2, "cannot assign float to int variable 'a'"),
                      self.messages("int a = 1;\na = 2.5;"))

    def test_3_assign_int_to_char_and_char_to_int(self):
        msgs = self.messages("int a = 1;\nchar c = 'x';\nc = a;\na = c;")
        self.assertIn(("semantic", 3, "cannot assign int to char variable 'c'"), msgs)
        self.assertIn(("semantic", 4, "cannot assign char to int variable 'a'"), msgs)

    def test_3_int_to_float_is_allowed(self):
        msgs = self.messages("float f = 1;\nf = 2;\nf = f + 1;")
        self.assertEqual([m for m in msgs if m[0] == "semantic"], [])

    def test_3_wrong_type_in_declaration_initializer(self):
        self.assertIn(("semantic", 1, "cannot assign float to int variable 'a'"),
                      self.messages("int a = 1.5;"))

    def test_4_arithmetic_on_char(self):
        msgs = self.messages("char c = 'a';\nfloat f = 1.0;\nf = c + f;")
        self.assertIn(("semantic", 3, "operator '+' cannot be applied to char and float"), msgs)

    def test_4_result_type_of_mixed_arithmetic_is_float(self):
        msgs = self.messages("int a = 1;\nfloat f = 2.5;\nint r = a + f;")
        self.assertIn(("semantic", 3, "cannot assign float to int variable 'r'"), msgs)

    def test_5_comparing_char_with_int(self):
        msgs = self.messages("char c = 'a';\nint a = 1;\nif (c > a) { a = 2; }")
        self.assertIn(("semantic", 3, "cannot compare char with int"), msgs)

    def test_5_comparing_int_with_float_and_char_with_char_is_allowed(self):
        msgs = self.messages("int a = 1;\nfloat f = 1.5;\nchar c = 'a';\nwhile (a < f) { a = a + 1; }\nif (c == 'b') { c = 'c'; }")
        self.assertEqual([m for m in msgs if m[0] == "semantic"], [])

    def test_6_division_by_literal_zero(self):
        self.assertIn(("semantic", 2, "division by zero"), self.messages("int a = 1;\na = 10 / 0;"))
        self.assertIn(("semantic", 2, "division by zero"), self.messages("float a = 1.0;\na = a / 0.0;"))

    def test_6_division_by_a_variable_is_not_checked(self):
        msgs = self.messages("int a = 1;\nint z = 0;\na = a / z;")
        self.assertNotIn("division by zero", [m[2] for m in msgs])

    def test_one_mistake_does_not_cascade(self):
        msgs = self.messages("int a = 1;\na = a + nothing + 2;")
        self.assertEqual(len([m for m in msgs if m[0] == "semantic"]), 1)

    def test_variable_is_not_visible_outside_its_block(self):
        msgs = self.messages("int a = 1;\nif (a > 0) {\n int inner = 1;\n a = inner;\n}\na = inner;")
        self.assertIn(("semantic", 6, "variable 'inner' is not declared"), msgs)

    # ---- warnings -----------------------------------------------------------------------
    def test_7_declared_but_never_used(self):
        self.assertIn(("warning", 1, "variable 'a' is declared but never used"), self.messages("int a = 1;"))

    def test_7_assignment_counts_as_use(self):
        msgs = self.messages("int a;\na = 1;")
        self.assertNotIn("variable 'a' is declared but never used", [m[2] for m in msgs])

    def test_8_used_before_initialization_warns_once(self):
        msgs = self.messages("int a;\nint b = a;\nb = a + 1;")
        self.assertEqual([m for m in msgs if "before being initialized" in m[2]],
                         [("warning", 2, "variable 'a' is used before being initialized")])


class BookExampleTests(unittest.TestCase):
    """The cross-reference example of the course book (chapter 4), without arrays."""

    def test_book_example(self):
        from tests import read_sample
        msgs, result = analyze(read_sample("book_example.txt"))
        self.assertEqual(msgs, [
            ("warning", 1, "variable 'j' is declared but never used"),
            ("warning", 2, "variable 'index' is declared but never used"),
            ("semantic", 5, "variable 'k' is not declared"),
            ("warning", 6, "variable 'f' is used before being initialized"),
        ])
        table = {s.name: s for s in result.symbols.all_symbols()}
        self.assertEqual([table[n].address for n in ("i", "j", "c", "index", "block", "f")],
                         [0, 2, 4, 5, 6, 7])
        self.assertEqual(sorted(table["i"].references), [4, 5, 6])


if __name__ == "__main__":
    unittest.main()
