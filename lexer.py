"""Phase 1: lexical analyzer (scanner).

Reads the source text character by character and groups the characters into
tokens. It is a hand-written DFA: the first character decides which kind of
token we are reading, and we always take the longest possible match.

It also (1) skips whitespace and comments, (2) counts lines so every message can
carry a line number, and (3) recovers from errors in "panic mode": skip the bad
character/word and keep going, so ALL lexical errors are reported in one run.
"""
from diagnostics import Diagnostics
from tokens import Token, KEYWORDS

TWO_CHAR_RELOPS = ("==", "!=", "<=", ">=")


# Plain ASCII checks on purpose: str.isalpha()/isdigit() also accept Arabic letters
# and Arabic-Indic digits, which are NOT part of MiniLang.
def _is_letter(c):
    return c.isascii() and c.isalpha()


def _is_digit(c):
    return c.isascii() and c.isdigit()


def _is_word_char(c):
    return _is_letter(c) or _is_digit(c) or c == "_"


def tokenize(source):
    """Return (tokens, diagnostics). Never raises on bad input."""
    tokens = []
    diags = Diagnostics()
    n = len(source)
    i = 0
    line = 1

    while i < n:
        c = source[i]

        if c == "\n":
            line += 1
            i += 1
        elif c in " \t\r":
            i += 1
        elif c == "#":                                  # comment: skip to end of line
            while i < n and source[i] != "\n":
                i += 1
        elif _is_letter(c) or c == "_":                 # identifier or keyword
            j = i
            while j < n and _is_word_char(source[j]):
                j += 1
            word = source[i:j]
            tokens.append(Token("KEYWORD" if word in KEYWORDS else "ID", word, line))
            i = j
        elif _is_digit(c):                              # integer or float
            i = _scan_number(source, i, line, tokens, diags)
        elif c == "'":                                  # character literal
            i = _scan_char(source, i, line, tokens, diags)
        else:
            two = source[i:i + 2]
            if two in TWO_CHAR_RELOPS:
                tokens.append(Token("REL_OP", two, line))
                i += 2
            elif c in "<>":
                tokens.append(Token("REL_OP", c, line))
                i += 1
            elif c == "=":
                tokens.append(Token("ASSIGN_OP", c, line))
                i += 1
            elif c in "+-*/":
                tokens.append(Token("ARITH_OP", c, line))
                i += 1
            elif c in "(){};,":
                tokens.append(Token("PUNCT", c, line))
                i += 1
            else:
                diags.add("lexical", line, f"illegal character '{c}'")
                i += 1                                  # panic mode: skip it

    return tokens, diags


def _scan_number(source, i, line, tokens, diags):
    """digits [ '.' digits ]  -- returns the index after the number."""
    n = len(source)
    j = i
    while j < n and _is_digit(source[j]):
        j += 1
    kind = "INT_NUM"
    if j + 1 < n and source[j] == "." and _is_digit(source[j + 1]):
        j += 1
        while j < n and _is_digit(source[j]):
            j += 1
        kind = "FLOAT_NUM"

    # A number must not be glued to letters or extra dots: 2x, 1s, 0..5, 3.
    if j < n and (_is_letter(source[j]) or source[j] in "_."):
        k = j
        while k < n and (_is_word_char(source[k]) or source[k] == "."):
            k += 1
        diags.add("lexical", line, f"malformed number '{source[i:k]}'")
        return k                                        # panic mode: skip the whole bad word

    tokens.append(Token(kind, source[i:j], line))
    return j


def _scan_char(source, i, line, tokens, diags):
    """'x'  -- exactly one character between single quotes."""
    n = len(source)
    if i + 2 < n and source[i + 2] == "'" and source[i + 1] not in "'\n":
        tokens.append(Token("CHAR_LIT", source[i:i + 3], line))
        return i + 3

    j = i + 1
    while j < n and source[j] not in "'\n":
        j += 1
    if j < n and source[j] == "'":
        j += 1
    diags.add("lexical", line,
              f"invalid character literal {source[i:j]} (must be exactly one character)")
    return j
