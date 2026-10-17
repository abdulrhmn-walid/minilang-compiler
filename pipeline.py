"""Connects the phases:  lexer -> parser -> semantic analyzer.

Each phase assumes the one before it succeeded, so we stop at the first phase
that reports errors (lexical errors: all of them; syntax: the first one;
semantic: all of them).
"""
from dataclasses import dataclass, field

from diagnostics import Diagnostics
from lexer import tokenize
from parser import parse
from semantic import analyze


@dataclass
class Result:
    stage: str                      # last phase that ran: "lexical" | "syntax" | "semantic"
    diagnostics: Diagnostics
    tokens: list = field(default_factory=list)
    tree: object = None             # ParseNode, available from the syntax phase on
    symbols: object = None          # SymbolTable, available after the semantic phase

    @property
    def succeeded(self):
        return self.stage == "semantic" and not self.diagnostics.has_errors()


def compile_source(source):
    tokens, diags = tokenize(source)
    if diags.has_errors():
        return Result("lexical", diags, tokens)

    tree, diags = parse(tokens)
    if diags.has_errors():
        return Result("syntax", diags, tokens)

    symbols, diags = analyze(tree)
    return Result("semantic", diags, tokens, tree, symbols)
