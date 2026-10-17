"""Shared collector for errors and warnings.

Every phase (lexer, parser, semantic analyzer) adds its messages here instead of
printing them or raising exceptions, so that all messages can be shown together
(in the console or in the GUI) and sorted by line number.
"""
from dataclasses import dataclass

LABELS = {
    "lexical": "Lexical Error",
    "syntax": "Syntax Error",
    "semantic": "Semantic Error",
    "warning": "Warning",
}


@dataclass(frozen=True)
class Diagnostic:
    kind: str      # "lexical" | "syntax" | "semantic" | "warning"
    line: int
    message: str

    @property
    def is_error(self):
        return self.kind != "warning"

    def __str__(self):
        label = f"[{LABELS[self.kind]}]"
        return f"{label:<16} line {self.line}: {self.message}"


class Diagnostics:
    def __init__(self):
        self.items = []

    def add(self, kind, line, message):
        self.items.append(Diagnostic(kind, line, message))

    def extend(self, other):
        self.items.extend(other.items)

    def errors(self):
        return [d for d in self.items if d.is_error]

    def warnings(self):
        return [d for d in self.items if not d.is_error]

    def has_errors(self):
        return any(d.is_error for d in self.items)

    def sorted(self):
        """By line number; on the same line, errors come before warnings."""
        return sorted(self.items, key=lambda d: (d.line, not d.is_error))

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)
