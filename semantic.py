"""Phase 3: semantic analyzer.

Walks the parse tree top-down, keeps a symbol table with scopes, and works out
the type of every expression bottom-up. Checks:

  errors    1 undeclared variable          5 comparing incompatible types
            2 declared twice in one scope  6 division by a literal zero
            3 assigning an incompatible type
            4 arithmetic on invalid types (char operands)
  warnings  7 declared but never used      8 used before being initialized

Type rules (our decision, the book only says "mismatched types are semantic errors"):
  assignment  int <- int | float <- int, float | char <- char     (int <- float is an error)
  arithmetic  only int and float; any float operand makes the result float
  comparison  numeric with numeric, or char with char
When an expression already has an error its type becomes "unknown" (None) so that
one mistake does not produce a chain of follow-up errors.
"""
from diagnostics import Diagnostics
from symbol_table import SymbolTable, DuplicateDeclaration

NUMERIC = ("int", "float")


def analyze(tree):
    """Return (symbol_table, diagnostics) for a parse tree built by parser.parse()."""
    return _Analyzer().run(tree)


class _Analyzer:
    def __init__(self):
        self.table = SymbolTable()
        self.diags = Diagnostics()

    # ------------------------------------------------------------------ helpers
    def _error(self, line, message):
        self.diags.add("semantic", line, message)

    def _warn(self, line, message):
        self.diags.add("warning", line, message)

    @staticmethod
    def _assignable(target, source):
        return target == source or (target == "float" and source == "int")

    # ------------------------------------------------------------------ driver
    def run(self, tree):
        self._stmt_list(tree.children[0])
        for symbol in self.table.all_symbols():
            if not symbol.used:
                self._warn(symbol.line_declared,
                           f"variable '{symbol.name}' is declared but never used")
        return self.table, self.diags

    # ------------------------------------------------------------------ statements
    def _stmt_list(self, node):
        while node.children[0].label != "ε":            # StmtList -> Stmt StmtList | ε
            self._stmt(node.children[0].children[0])
            node = node.children[1]

    def _block(self, node):                             # Block -> { StmtList }
        self.table.new_scope()
        self._stmt_list(node.children[1])
        self.table.exit_scope()

    def _stmt(self, node):
        if node.label == "Decl":
            self._decl(node)
        elif node.label == "Assign":
            self._assign(node)
        elif node.label == "IfStmt":                    # if ( Cond ) Block ElsePart
            self._cond(node.children[2])
            self._block(node.children[4])
            else_part = node.children[5]
            if else_part.children[0].label == "else":
                self._block(else_part.children[1])
        elif node.label == "WhileStmt":                 # while ( Cond ) Block
            self._cond(node.children[2])
            self._block(node.children[4])

    def _decl(self, node):                              # Type id InitOpt MoreDecl ;
        type_ = node.children[0].children[0].token.lexeme
        id_node, init_opt, more = node.children[1], node.children[2], node.children[3]
        self._declare_one(type_, id_node, init_opt)
        while more.children[0].label != "ε":            # MoreDecl -> , id InitOpt MoreDecl
            self._declare_one(type_, more.children[1], more.children[2])
            more = more.children[3]

    def _declare_one(self, type_, id_node, init_opt):
        name, line = id_node.token.lexeme, id_node.token.line
        try:
            symbol = self.table.declare(name, type_, line)
        except DuplicateDeclaration as dup:
            self._error(line, f"variable '{name}' is already declared in this scope "
                              f"(line {dup.existing.line_declared})")
            return
        if init_opt.children[0].label == "=":           # InitOpt -> = Expr
            value_type = self._expr_type(init_opt.children[1])
            if value_type and not self._assignable(type_, value_type):
                self._error(line, f"cannot assign {value_type} to {type_} variable '{name}'")
            symbol.initialized = True

    def _assign(self, node):                            # id = Expr ;
        id_token = node.children[0].token
        value_type = self._expr_type(node.children[2])
        symbol = self.table.lookup(id_token.lexeme)
        if symbol is None:
            self._error(id_token.line, f"variable '{id_token.lexeme}' is not declared")
            return
        self.table.add_reference(symbol, id_token.line)
        symbol.initialized = True
        if value_type and not self._assignable(symbol.type, value_type):
            self._error(id_token.line,
                        f"cannot assign {value_type} to {symbol.type} variable '{symbol.name}'")

    def _cond(self, node):                              # Cond -> Expr RelOp Expr
        left = self._expr_type(node.children[0])
        right = self._expr_type(node.children[2])
        op_token = node.children[1].children[0].token
        if left and right and not ((left in NUMERIC and right in NUMERIC) or left == right):
            self._error(op_token.line, f"cannot compare {left} with {right}")

    # ------------------------------------------------------------------ expressions
    def _expr_type(self, node):
        """Type of an Expr / Term / Factor node, or None if unknown (error already reported)."""
        if node.label in ("Expr", "Term"):              # Expr -> Term ExprP,  Term -> Factor TermP
            left = self._expr_type(node.children[0])
            return self._fold(left, node.children[1])

        first = node.children[0]                        # Factor
        if first.label == "(":
            return self._expr_type(node.children[1])
        if first.label == "intnum":
            return "int"
        if first.label == "floatnum":
            return "float"
        if first.label == "charlit":
            return "char"
        return self._variable_type(first)               # id

    def _fold(self, left, tail):
        """Combine `left` with the rest of the chain: ExprP -> + Term ExprP | ... | ε."""
        while tail.children[0].label != "ε":
            op_node, operand, next_tail = tail.children
            op, line = op_node.token.lexeme, op_node.token.line
            right = self._expr_type(operand)

            if op == "/" and self._is_zero_literal(operand):
                self._error(line, "division by zero")

            if left is None or right is None:
                left = None
            elif left not in NUMERIC or right not in NUMERIC:
                self._error(line, f"operator '{op}' cannot be applied to {left} and {right}")
                left = None
            else:
                left = "float" if "float" in (left, right) else "int"
            tail = next_tail
        return left

    @staticmethod
    def _is_zero_literal(factor):
        first = factor.children[0]
        return first.label in ("intnum", "floatnum") and float(first.token.lexeme) == 0

    def _variable_type(self, id_node):
        token = id_node.token
        symbol = self.table.lookup(token.lexeme)
        if symbol is None:
            self._error(token.line, f"variable '{token.lexeme}' is not declared")
            return None
        self.table.add_reference(symbol, token.line)
        if not symbol.initialized:
            self._warn(token.line, f"variable '{symbol.name}' is used before being initialized")
            symbol.initialized = True                   # warn once per variable
        return symbol.type
