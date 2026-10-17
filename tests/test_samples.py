"""The sample programs in tests/*.txt and what the whole pipeline must say about each."""
import io
import os
import unittest
from contextlib import redirect_stdout

from tests import read_sample, HERE
from pipeline import compile_source
import main as cli


def run(name):
    return compile_source(read_sample(name))


def lines_of(result, kind=None):
    return [d.line for d in result.diagnostics.sorted() if kind is None or d.kind == kind]


class SampleProgramTests(unittest.TestCase):
    def test_valid_program(self):
        r = run("valid.txt")
        self.assertEqual(r.stage, "semantic")
        self.assertTrue(r.succeeded)
        self.assertEqual(len(r.diagnostics.errors()), 0)
        self.assertEqual(lines_of(r, "warning"), [3, 4, 4])       # c, i, j are never used
        table = {s.name: s for s in r.symbols.all_symbols()}
        self.assertEqual([(s.name, s.address) for s in r.symbols.all_symbols()],
                         [("x", 0), ("y", 2), ("c", 6), ("i", 7), ("j", 9)])
        self.assertEqual(sorted(table["x"].references), [5, 8])
        self.assertEqual(sorted(table["y"].references), [6, 10, 11])

    def test_lexical_errors_stop_the_pipeline(self):
        r = run("lexical_error.txt")
        self.assertEqual(r.stage, "lexical")
        self.assertEqual(lines_of(r), [1, 2, 3, 4])
        self.assertIsNone(r.tree)
        self.assertIsNone(r.symbols)

    def test_syntax_errors_stop_before_semantic(self):
        for name, line, text in [("syntax_error_1.txt", 1, "missing ';'"),
                                 ("syntax_error_2.txt", 2, "unexpected '{'"),
                                 ("syntax_error_3.txt", 2, "unexpected '}' after end of program"),
                                 ("syntax_error_4.txt", 2, "unexpected 'else'")]:
            with self.subTest(name):
                r = run(name)
                self.assertEqual(r.stage, "syntax")
                self.assertEqual(lines_of(r), [line])
                self.assertIn(text, r.diagnostics.items[0].message)
                self.assertIsNone(r.symbols)

    def test_semantic_errors(self):
        r = run("semantic_error.txt")
        self.assertEqual(r.stage, "semantic")
        self.assertFalse(r.succeeded)
        self.assertEqual(lines_of(r, "semantic"), [4, 5, 6, 7, 8, 9, 10])
        self.assertEqual(len(r.diagnostics.errors()), 7)
        self.assertEqual([d.message for d in r.diagnostics.warnings()],
                         ["variable 'inner' is declared but never used"])

    def test_comment_only_program(self):
        r = run("empty.txt")
        self.assertEqual(r.tokens, [])
        self.assertTrue(r.succeeded)
        self.assertEqual(len(r.diagnostics), 0)


class CommandLineTests(unittest.TestCase):
    def call(self, *args):
        out = io.StringIO()
        with redirect_stdout(out):
            code = cli.main(list(args))
        return code, out.getvalue()

    def test_exit_codes(self):
        self.assertEqual(self.call(os.path.join(HERE, "valid.txt"))[0], 0)
        self.assertEqual(self.call(os.path.join(HERE, "semantic_error.txt"))[0], 1)
        self.assertEqual(self.call(os.path.join(HERE, "no_such_file.txt"))[0], 2)

    def test_show_only_messages(self):
        code, text = self.call(os.path.join(HERE, "syntax_error_1.txt"), "--show", "errors")
        self.assertEqual(code, 1)
        self.assertIn("[Syntax Error]", text)
        self.assertNotIn("Tokens", text)

    def test_grammar_mode_needs_no_file(self):
        code, text = self.call("--grammar")
        self.assertEqual(code, 0)
        self.assertIn("no conflicts: the grammar is LL(1)", text)
        self.assertIn("FOLLOW sets", text)


if __name__ == "__main__":
    unittest.main()
