"""Turns compiler results into plain text. Used by both main.py (console) and gui.py (window),
so the two always show exactly the same thing."""
from grammar import NONTERMINALS, rhs_text
from ll1_table import analysis, numbered_productions


def _set_text(symbols):
    return "{ " + "  ".join("ε" if s == "eps" else s for s in sorted(symbols)) + " }"


def tokens_text(tokens):
    lines = [f"{'#':>4}  {'Token Type':<11} {'Lexeme':<14} Line", "-" * 40]
    for number, t in enumerate(tokens, 1):
        lines.append(f"{number:>4}  {t.type:<11} {t.lexeme:<14} {t.line}")
    lines.append("")
    lines.append(f"Total: {len(tokens)} token(s)")
    return "\n".join(lines)


def symbols_text(table):
    header = (f"{'#':>3}  {'Name':<12}{'Address':>7}  {'Type':<6}{'Dim':>3}  "
              f"{'Declared':>8}  {'Scope':>5}  References")
    lines = [header, "-" * 66]
    for number, s in enumerate(table.all_symbols(), 1):
        refs = ", ".join(str(n) for n in sorted(s.references)) or "-"
        lines.append(f"{number:>3}  {s.name:<12}{s.address:>7}  {s.type:<6}{s.dim:>3}  "
                     f"{s.line_declared:>8}  {s.scope:>5}  {refs}")
    if not table.all_symbols():
        lines.append("(no variables declared)")
    return "\n".join(lines)


def first_follow_text():
    first, follow, _table, _conflicts = analysis()
    width = max(len(nt) for nt in NONTERMINALS)
    lines = ["FIRST sets", "-" * 10]
    lines += [f"  {nt:<{width}} = {_set_text(first[nt])}" for nt in NONTERMINALS]
    lines += ["", "FOLLOW sets", "-" * 11]
    lines += [f"  {nt:<{width}} = {_set_text(follow[nt])}" for nt in NONTERMINALS]
    return "\n".join(lines)


def ll1_text():
    first, follow, table, conflicts = analysis()
    productions = numbered_productions(first, follow)
    verdict = "no conflicts: the grammar is LL(1)" if not conflicts else f"CONFLICTS: {conflicts}"
    lines = [f"Productions: {len(productions)}   Table cells filled: {len(table)}   {verdict}",
             "",
             "Each production is chosen when the next token is in its select set:",
             ""]
    for number, nt, rhs, select in productions:
        lines.append(f"{number:>3}. {nt} -> {rhs_text(rhs)}")
        lines.append(f"       chosen on {_set_text(select)}")
    lines += ["", "", "Table cells  M[non-terminal, next token] = production", ""]
    for nt in NONTERMINALS:
        for terminal in sorted(t for (n, t) in table if n == nt):
            lines.append(f"  M[{nt}, {terminal}] = {nt} -> {rhs_text(table[(nt, terminal)])}")
    return "\n".join(lines)


def tree_text(tree):
    return "\n".join(tree.draw())


def diagnostics_text(diags):
    if not diags.items:
        return "No errors or warnings."
    return "\n".join(str(d) for d in diags.sorted())


def summary(result):
    errors = len(result.diagnostics.errors())
    warnings = len(result.diagnostics.warnings())
    line = f"{errors} error(s), {warnings} warning(s)."
    if result.stage != "semantic":
        line += f" Compilation stopped after the {result.stage} phase."
    elif errors == 0:
        line += " Compilation succeeded."
    return line


# The two sections below depend on how far the compilation got.
def symbols_section(result):
    if result.symbols is None:
        return f"(not available: compilation stopped after the {result.stage} phase)"
    return symbols_text(result.symbols)


def tree_section(result):
    if result.tree is None:
        return f"(not available: compilation stopped after the {result.stage} phase)"
    return tree_text(result.tree)
