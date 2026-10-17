import unittest

import tests  # noqa: F401  (sets up the import path)
from symbol_table import SymbolTable, DuplicateDeclaration


class SymbolTableTests(unittest.TestCase):
    def test_addresses_grow_by_type_size(self):
        t = SymbolTable()
        symbols = [t.declare("x", "int", 1), t.declare("y", "float", 2),
                   t.declare("c", "char", 3), t.declare("i", "int", 4)]
        self.assertEqual([s.address for s in symbols], [0, 2, 6, 7])

    def test_duplicate_in_same_scope_is_rejected(self):
        t = SymbolTable()
        first = t.declare("a", "int", 1)
        with self.assertRaises(DuplicateDeclaration) as ctx:
            t.declare("a", "float", 5)
        self.assertIs(ctx.exception.existing, first)

    def test_inner_scope_may_hide_an_outer_name(self):
        t = SymbolTable()
        outer = t.declare("x", "int", 1)
        t.new_scope()
        inner = t.declare("x", "float", 3)
        self.assertIs(t.lookup("x"), inner)
        t.exit_scope()
        self.assertIs(t.lookup("x"), outer)

    def test_inner_names_disappear_after_exit(self):
        t = SymbolTable()
        t.new_scope()
        t.declare("tmp", "int", 2)
        t.exit_scope()
        self.assertIsNone(t.lookup("tmp"))

    def test_lookup_of_unknown_name(self):
        self.assertIsNone(SymbolTable().lookup("nope"))

    def test_scope_numbers(self):
        t = SymbolTable()
        a = t.declare("a", "int", 1)
        t.new_scope()
        b = t.declare("b", "int", 2)
        self.assertEqual((a.scope, b.scope), (0, 1))

    def test_references_exclude_the_declaration_line(self):
        t = SymbolTable()
        s = t.declare("x", "int", 3)
        t.add_reference(s, 3)          # same line as the declaration
        t.add_reference(s, 5)
        t.add_reference(s, 5)
        self.assertEqual(s.references, {5})
        self.assertTrue(s.used)

    def test_cannot_exit_the_global_scope(self):
        with self.assertRaises(RuntimeError):
            SymbolTable().exit_scope()

    def test_all_symbols_keep_declaration_order_even_after_scope_exit(self):
        t = SymbolTable()
        t.declare("a", "int", 1)
        t.new_scope()
        t.declare("b", "int", 2)
        t.exit_scope()
        t.declare("c", "int", 3)
        self.assertEqual([s.name for s in t.all_symbols()], ["a", "b", "c"])


if __name__ == "__main__":
    unittest.main()
