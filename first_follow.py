"""FIRST and FOLLOW sets.

FIRST(X)  : terminals that can start a string derived from X (plus "eps" if X can vanish).
FOLLOW(A) : terminals that can appear right after A in some derivation ("$" = end of input).

Both are computed by repeating the rules until nothing changes any more
(a "fixed point"). This avoids the infinite loops of a recursive solution.
"""
from grammar import GRAMMAR, EPS, START


def first_of_sequence(symbols, first, grammar=GRAMMAR):
    """FIRST of a sequence of symbols, e.g. the right-hand side of a production."""
    result = set()
    for s in symbols:
        if s == EPS:
            continue
        if s not in grammar:                 # a terminal starts the sequence
            result.add(s)
            return result
        result |= first[s] - {EPS}
        if EPS not in first[s]:              # s cannot vanish, so we stop here
            return result
    result.add(EPS)                          # every symbol can vanish (or the list is empty)
    return result


def compute_first(grammar=GRAMMAR):
    first = {nt: set() for nt in grammar}
    changed = True
    while changed:
        changed = False
        for nt, rules in grammar.items():
            for rhs in rules:
                new = first_of_sequence(rhs, first, grammar)
                if not new <= first[nt]:
                    first[nt] |= new
                    changed = True
    return first


def compute_follow(first, grammar=GRAMMAR, start=START):
    follow = {nt: set() for nt in grammar}
    follow[start].add("$")
    changed = True
    while changed:
        changed = False
        for nt, rules in grammar.items():
            for rhs in rules:
                for i, symbol in enumerate(rhs):
                    if symbol not in grammar:        # only non-terminals have a FOLLOW set
                        continue
                    rest = first_of_sequence(rhs[i + 1:], first, grammar)
                    new = rest - {EPS}               # rule: FIRST(what comes next)
                    if EPS in rest:                  # rule: nothing (or only vanishing symbols) follows
                        new |= follow[nt]
                    if not new <= follow[symbol]:
                        follow[symbol] |= new
                        changed = True
    return follow
