"""Token definition and the fixed vocabulary of MiniLang."""
from dataclasses import dataclass

KEYWORDS = {"int", "float", "char", "if", "else", "while"}


@dataclass(frozen=True)
class Token:
    type: str      # KEYWORD, ID, INT_NUM, FLOAT_NUM, CHAR_LIT, ARITH_OP, REL_OP, ASSIGN_OP, PUNCT
    lexeme: str    # the exact text in the source, e.g. "x" or "10"
    line: int      # 1-based line number, used for error messages


# Many different lexemes share one grammar terminal (every identifier is "id", ...).
# Keywords, operators and punctuation are their own terminal: the lexeme itself.
_TERMINAL_OF_TYPE = {
    "ID": "id",
    "INT_NUM": "intnum",
    "FLOAT_NUM": "floatnum",
    "CHAR_LIT": "charlit",
}


def grammar_symbol(token):
    """The terminal symbol of the grammar that this token stands for."""
    return _TERMINAL_OF_TYPE.get(token.type, token.lexeme)
