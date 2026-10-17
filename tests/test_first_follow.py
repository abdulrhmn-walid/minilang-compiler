import unittest

import tests  # noqa: F401
from first_follow import compute_first, compute_follow
from grammar import GRAMMAR, NONTERMINALS
from ll1_table import analysis, build_table, numbered_productions


class MiniLangGrammarTests(unittest.TestCase):
    def setUp(self):
        self.first, self.follow, self.table, self.conflicts = analysis()

    def test_size_of_the_grammar(self):
        self.assertEqual(len(NONTERMINALS), 19)
        self.assertEqual(sum(len(r) for r in GRAMMAR.values()), 41)

    def test_no_direct_left_recursion(self):
        for nt, rules in GRAMMAR.items():
            for rhs in rules:
                self.assertNotEqual(rhs[0], nt, f"{nt} is left-recursive")

    def test_first_of_expr(self):
        self.assertEqual(self.first["Expr"], {"(", "id", "intnum", "floatnum", "charlit"})

    def test_first_of_stmt_list_contains_epsilon(self):
        self.assertIn("eps", self.first["StmtList"])
        self.assertEqual(self.first["Decl"], {"int", "float", "char"})

    def test_follow_of_expr(self):
        self.assertEqual(self.follow["Expr"],
                         {"==", "!=", "<", ">", "<=", ">=", ")", ",", ";"})

    def test_follow_of_start_symbol_has_end_marker(self):
        self.assertEqual(self.follow["Program"], {"$"})

    def test_epsilon_is_never_in_a_follow_set(self):
        for nt, s in self.follow.items():
            self.assertNotIn("eps", s, nt)

    def test_else_is_not_in_follow_of_else_part(self):
        # that is why the empty production of ElsePart never clashes with 'else'
        self.assertNotIn("else", self.follow["ElsePart"])

    def test_table_is_ll1_with_95_cells(self):
        self.assertEqual(self.conflicts, [])
        self.assertEqual(len(self.table), 95)

    def test_select_sets_of_one_non_terminal_are_disjoint(self):
        by_nt = {}
        for _n, nt, _rhs, select in numbered_productions(self.first, self.follow):
            by_nt.setdefault(nt, []).append(select)
        for nt, sets in by_nt.items():
            union = set().union(*sets)
            self.assertEqual(sum(len(s) for s in sets), len(union), f"overlap in {nt}")


class ConflictDetectionTests(unittest.TestCase):
    def test_book_example_is_not_ll1(self):
        # Course book, chapter 6:  S -> iEtSS1 | a ;  S1 -> eS1 | eps ;  E -> b
        g = {
            "S": [["i", "E", "t", "S", "S1"], ["a"]],
            "S1": [["e", "S1"], ["eps"]],
            "E": [["b"]],
        }
        first = compute_first(g)
        follow = compute_follow(first, g, "S")
        _table, conflicts = build_table(first, follow, g)
        self.assertIn(("S1", "e"), conflicts)

    def test_left_recursive_expression_grammar_is_rejected_by_the_check(self):
        # E -> E + T | T  has two productions starting with the same terminals
        g = {"E": [["E", "+", "T"], ["T"]], "T": [["id"]]}
        first = compute_first(g)
        follow = compute_follow(first, g, "E")
        _table, conflicts = build_table(first, follow, g)
        self.assertTrue(conflicts)


if __name__ == "__main__":
    unittest.main()
