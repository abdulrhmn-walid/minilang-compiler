import unittest

from tests import read_sample
from lexer import tokenize


def pairs(source):
    tokens, _ = tokenize(source)
    return [(t.type, t.lexeme) for t in tokens]


def messages(source):
    _, diags = tokenize(source)
    return [(d.line, d.message) for d in diags]


class LexerTests(unittest.TestCase):
    def test_book_example_assignment(self):
        self.assertEqual(pairs("newval = oldval + 12;"), [
            ("ID", "newval"), ("ASSIGN_OP", "="), ("ID", "oldval"),
            ("ARITH_OP", "+"), ("INT_NUM", "12"), ("PUNCT", ";")])

    def test_minus_is_always_an_operator(self):
        self.assertEqual(pairs("y=y-1;"), [
            ("ID", "y"), ("ASSIGN_OP", "="), ("ID", "y"),
            ("ARITH_OP", "-"), ("INT_NUM", "1"), ("PUNCT", ";")])

    def test_float_is_one_token(self):
        self.assertEqual(pairs("x = 3.5;")[2], ("FLOAT_NUM", "3.5"))

    def test_float_followed_by_plus_without_spaces(self):
        self.assertEqual(pairs("3.5+1"), [("FLOAT_NUM", "3.5"), ("ARITH_OP", "+"), ("INT_NUM", "1")])

    def test_comment_only_gives_no_tokens(self):
        self.assertEqual(pairs("# just a comment\n"), [])

    def test_comment_after_code(self):
        self.assertEqual(pairs("x # not an operator + 1\n"), [("ID", "x")])

    def test_keywords_need_the_whole_word(self):
        self.assertEqual(pairs("integer ifx int"),
                         [("ID", "integer"), ("ID", "ifx"), ("KEYWORD", "int")])

    def test_keywords_are_case_sensitive(self):
        self.assertEqual(pairs("Int"), [("ID", "Int")])

    def test_relational_operators(self):
        ops = [t for t, _ in pairs("== != <= >= < >")]
        self.assertEqual(ops, ["REL_OP"] * 6)
        self.assertEqual([lx for _, lx in pairs("a<=b")], ["a", "<=", "b"])

    def test_char_literal(self):
        self.assertEqual(pairs("'a' '7' ' '"), [("CHAR_LIT", "'a'"), ("CHAR_LIT", "'7'"), ("CHAR_LIT", "' '")])

    def test_line_numbers(self):
        tokens, _ = tokenize("int a;\n\n# c\nfloat b;")
        self.assertEqual([t.line for t in tokens], [1, 1, 1, 4, 4, 4])

    # ---------------------------------------------------------------- errors
    def test_book_lexical_error_dollar_and_double_dot(self):
        self.assertEqual(messages("int $, b=0..5;"), [
            (1, "illegal character '$'"), (1, "malformed number '0..5'")])

    def test_book_lexical_error_number_glued_to_letter(self):
        self.assertEqual(messages("a=2x;"), [(1, "malformed number '2x'")])

    def test_trailing_dot_is_malformed(self):
        self.assertEqual(messages("x = 3.;"), [(1, "malformed number '3.'")])

    def test_all_errors_are_collected_not_just_the_first(self):
        self.assertEqual(len(messages(read_sample("lexical_error.txt"))), 4)

    def test_arabic_letters_and_digits_are_not_part_of_the_language(self):
        self.assertEqual(len(messages("ب")), 1)
        self.assertEqual(len(messages("x = ٣;")), 1)

    def test_bad_character_literals(self):
        self.assertEqual(len(messages("char c = 'ab';")), 1)
        self.assertEqual(len(messages("char c = '';")), 1)
        self.assertEqual(len(messages("char c = 'a;")), 1)

    def test_lone_bang_is_illegal(self):
        self.assertEqual(messages("a ! b"), [(1, "illegal character '!'")])


if __name__ == "__main__":
    unittest.main()
