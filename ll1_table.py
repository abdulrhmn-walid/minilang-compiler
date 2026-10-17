"""LL(1) parsing table.

For a production  A -> alpha  put it in cell M[A, a]
  * for every terminal a in FIRST(alpha), and
  * if eps is in FIRST(alpha): for every terminal b in FOLLOW(A)  (including "$").

That set of terminals is called the production's "select set".
If two different productions land in the same cell, the grammar is NOT LL(1).
"""
from functools import lru_cache

from grammar import GRAMMAR, EPS
from first_follow import compute_first, compute_follow, first_of_sequence


def select_set(nt, rhs, first, follow, grammar=GRAMMAR):
    f = first_of_sequence(rhs, first, grammar)
    return (f - {EPS}) | (follow[nt] if EPS in f else set())


def build_table(first, follow, grammar=GRAMMAR):
    """Return (table, conflicts). table[(non_terminal, terminal)] = right-hand side tuple."""
    table = {}
    conflicts = []
    for nt, rules in grammar.items():
        for rhs in rules:
            for terminal in select_set(nt, rhs, first, follow, grammar):
                key = (nt, terminal)
                if key in table and table[key] != tuple(rhs):
                    conflicts.append(key)
                table[key] = tuple(rhs)
    return table, conflicts


def numbered_productions(first, follow, grammar=GRAMMAR):
    """[(number, non_terminal, rhs, select_set), ...] in grammar order."""
    rows = []
    number = 0
    for nt, rules in grammar.items():
        for rhs in rules:
            number += 1
            rows.append((number, nt, rhs, select_set(nt, rhs, first, follow, grammar)))
    return rows


@lru_cache(maxsize=None)
def analysis():
    """FIRST, FOLLOW, table and conflicts of the MiniLang grammar (computed once)."""
    first = compute_first()
    follow = compute_follow(first)
    table, conflicts = build_table(first, follow)
    return first, follow, table, conflicts
