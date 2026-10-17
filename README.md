# MiniLang Compiler (front-end)

A compiler front-end for a small C-like language, **MiniLang**, written in pure Python (standard library only, no `pip install`). Built for a Compiler Design course at Damietta University.

It takes a source file and runs three phases, reporting every problem with its line number:

```
source ──► Lexer ──► tokens ──► LL(1) Parser ──► parse tree ──► Semantic analyzer ──► report
              │                      │                               │
        lexical errors         syntax error                 semantic errors + warnings
```

[Arabic setup guide / دليل التشغيل بالعربي](README.ar.md)

## Features

- **Lexer**: hand-written DFA-style scanner, longest-match, panic-mode recovery (reports *all* lexical errors in one run).
- **Grammar analysis**: FIRST and FOLLOW sets computed by fixed-point iteration, then the LL(1) table is built from them. 19 non-terminals, 41 productions, 95 table cells, **0 conflicts** (checked at start-up).
- **Parser**: table-driven, non-recursive predictive parser (explicit stack) that builds the parse tree while parsing. A forgotten `;` is reported on the line where it belongs.
- **Semantic analysis** with a scoped symbol table: 6 errors (undeclared variable, duplicate declaration, incompatible assignment, arithmetic on `char`, incompatible comparison, division by literal zero) and 2 warnings (declared but never used, used before initialization).
- **Tkinter GUI** with tabs: Messages, Tokens, Symbol Table, FIRST, FOLLOW, LL(1) Table, Parse Tree.
- **85 unit tests** (`unittest`).

## The language

```
int x = 10;
float y = 2.5;
char c = 'a';

while (x > 0) {
    if (x == 5) { y = y * 2; } else { y = y + 1; }
    x = x - 1;
}
```

| | |
|---|---|
| Types | `int` (2 bytes), `float` (4), `char` (1) |
| Keywords | `int float char if else while` |
| Operators | `+ - * /`, and `== != < > <= >=` inside conditions |
| Other | `#` comments, mandatory `{ }` blocks, no unary minus |
| Assignment rules | `float ← int` is allowed, `int ← float` is an error, `char` only accepts `char` |

## Run it

Requires Python 3.10+ (tkinter is only needed for the GUI; on Linux: `sudo apt install python3-tk`).

```bash
python gui.py                                     # graphical interface
python main.py tests/valid.txt                    # full report in the terminal
python main.py tests/semantic_error.txt --show errors
python main.py tests/valid.txt --show tokens symbols tree
python main.py --grammar                          # FIRST / FOLLOW / LL(1) table
python -m unittest -v                             # run the tests
```

`--show` accepts: `tokens`, `symbols`, `first-follow`, `table`, `tree`, `errors`. Exit code: 0 success, 1 errors found, 2 usage error.

## Project layout

| File | Role |
|---|---|
| `tokens.py`, `lexer.py` | Phase 1: tokens and scanner |
| `grammar.py` | The grammar as data |
| `first_follow.py`, `ll1_table.py` | FIRST/FOLLOW and the LL(1) table |
| `parser.py` | Phase 2: predictive parser + parse tree |
| `symbol_table.py`, `semantic.py` | Phase 3: scoped symbol table and type/scope checks |
| `diagnostics.py` | Shared collector for errors and warnings |
| `pipeline.py` | Chains the phases; stops at the first failing one |
| `report.py`, `main.py`, `gui.py` | Output: text reports, CLI, GUI |
| `tests/` | Unit tests and sample programs |

## Example output

```
[Semantic Error] line 5: cannot assign float to int variable 'a'
[Semantic Error] line 6: variable 'b' is not declared
[Warning]        line 8: variable 'u' is declared but never used
```

## Scope

This is the **front-end** only (analysis). There is no code generation or optimization stage.

## License

MIT, see [LICENSE](LICENSE).
