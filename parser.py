"""Phase 2: table-driven LL(1) parser (non-recursive predictive parser).

Three data structures, as in the course book: the input (the tokens), a stack,
and the parsing table. The stack holds (symbol, tree node) pairs so the parse
tree is built while parsing:

    pop X
    X is a terminal      -> it must equal the current token, then consume the token
    X is a non-terminal  -> look up M[X, current token], push the production's right side
                            (reversed, so its first symbol ends up on top)
    no table entry       -> syntax error
"""
from diagnostics import Diagnostics
from grammar import GRAMMAR, START, EPS
from ll1_table import analysis
from tokens import grammar_symbol

_FIRST, _FOLLOW, TABLE, _CONFLICTS = analysis()
if _CONFLICTS:      # would mean someone broke the grammar; fail loudly, not silently
    raise RuntimeError(f"the grammar is not LL(1): conflicts at {_CONFLICTS}")

_VALUE_TERMINALS = ("id", "intnum", "floatnum", "charlit")


class ParseNode:
    def __init__(self, label, token=None):
        self.label = label          # non-terminal name, terminal name, or "ε"
        self.token = token          # the Token, for terminal leaves only
        self.children = []

    def draw(self, prefix="", is_last=True, is_root=True):
        """The tree as a list of text lines (box-drawing characters)."""
        if self.token is not None and self.label == "charlit":
            text = f"{self.label}  {self.token.lexeme}"          # the lexeme already has its own quotes: 'a'
        elif self.token is not None and self.label in _VALUE_TERMINALS:
            text = f"{self.label}  '{self.token.lexeme}'"
        elif self.token is not None:
            text = f"'{self.token.lexeme}'"
        else:
            text = self.label
        if is_root:
            lines, child_prefix = [text], ""
        else:
            lines = [prefix + ("└── " if is_last else "├── ") + text]
            child_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(self.children):
            lines += child.draw(child_prefix, i == len(self.children) - 1, False)
        return lines


def parse(tokens):
    """Return (tree, diagnostics). tree is None if there is a syntax error."""
    diags = Diagnostics()
    root = ParseNode(START)
    stack = [("$", None), (START, root)]
    lookahead = [grammar_symbol(t) for t in tokens] + ["$"]
    pos = 0

    def current_line():
        if pos < len(tokens):
            return tokens[pos].line
        return tokens[-1].line if tokens else 1

    while stack:
        symbol, node = stack.pop()
        a = lookahead[pos]

        if symbol == "$":
            if a == "$":
                return root, diags                              # ACCEPT
            diags.add("syntax", current_line(),
                      f"unexpected '{tokens[pos].lexeme}' after end of program")
            return None, diags

        if symbol not in GRAMMAR:                               # a terminal on the stack
            if symbol == a:
                node.token = tokens[pos]
                pos += 1
            else:
                diags.add("syntax", current_line(), f"expected '{symbol}'")
                return None, diags
            continue

        rhs = TABLE.get((symbol, a))                            # a non-terminal on the stack
        if rhs is None:
            expected = sorted(t for (nt, t) in TABLE if nt == symbol)
            # The classic case: a forgotten ';' is only noticed at the first token of the
            # NEXT line, so report it on the line where the ';' should have been.
            if ";" in expected and pos > 0 and (pos >= len(tokens)
                                                or tokens[pos].line > tokens[pos - 1].line):
                diags.add("syntax", tokens[pos - 1].line, "missing ';'")
            else:
                found = tokens[pos].lexeme if pos < len(tokens) else "end of file"
                diags.add("syntax", current_line(),
                          f"unexpected '{found}'; expected one of {expected}")
            return None, diags

        children = [ParseNode("ε" if s == EPS else s) for s in rhs]
        node.children = children
        for s, child in reversed(list(zip(rhs, children))):
            if s != EPS:
                stack.append((s, child))

    diags.add("syntax", current_line(), "parser stack became empty unexpectedly")
    return None, diags
