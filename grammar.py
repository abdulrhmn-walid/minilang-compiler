"""The grammar of MiniLang, written as plain data.

Each key is a non-terminal. Each value is the list of its productions, and each
production is a list of symbols. "eps" means the empty string (epsilon).

Terminals are the names in `tokens.grammar_symbol`: id, intnum, floatnum, charlit,
plus keywords and punctuation written literally.

The grammar was shaped to be LL(1):
  * no left recursion   -> Expr / ExprP, Term / TermP instead of Expr -> Expr + Term
  * no ambiguity        -> three layers Expr / Term / Factor give * and / priority over + and -
  * left factoring      -> InitOpt holds the optional "= Expr" part of a declaration
  * no dangling else    -> blocks always use { }
"""

EPS = "eps"
START = "Program"

GRAMMAR = {
    "Program":   [["StmtList"]],
    "StmtList":  [["Stmt", "StmtList"], [EPS]],
    "Stmt":      [["Decl"], ["Assign"], ["IfStmt"], ["WhileStmt"]],
    "Decl":      [["Type", "id", "InitOpt", "MoreDecl", ";"]],
    "InitOpt":   [["=", "Expr"], [EPS]],
    "MoreDecl":  [[",", "id", "InitOpt", "MoreDecl"], [EPS]],
    "Type":      [["int"], ["float"], ["char"]],
    "Assign":    [["id", "=", "Expr", ";"]],
    "IfStmt":    [["if", "(", "Cond", ")", "Block", "ElsePart"]],
    "ElsePart":  [["else", "Block"], [EPS]],
    "WhileStmt": [["while", "(", "Cond", ")", "Block"]],
    "Block":     [["{", "StmtList", "}"]],
    "Cond":      [["Expr", "RelOp", "Expr"]],
    "RelOp":     [["=="], ["!="], ["<"], [">"], ["<="], [">="]],
    "Expr":      [["Term", "ExprP"]],
    "ExprP":     [["+", "Term", "ExprP"], ["-", "Term", "ExprP"], [EPS]],
    "Term":      [["Factor", "TermP"]],
    "TermP":     [["*", "Factor", "TermP"], ["/", "Factor", "TermP"], [EPS]],
    "Factor":    [["(", "Expr", ")"], ["id"], ["intnum"], ["floatnum"], ["charlit"]],
}

NONTERMINALS = list(GRAMMAR)
TERMINALS = sorted({s for rules in GRAMMAR.values() for rhs in rules for s in rhs
                    if s not in GRAMMAR and s != EPS})


def rhs_text(rhs):
    """Production right-hand side for printing."""
    return " ".join("ε" if s == EPS else s for s in rhs)
