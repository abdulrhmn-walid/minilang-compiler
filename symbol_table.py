"""Symbol table with nested scopes.

Operations (the ones the course book asks for):
    new_scope()       enter a block        ( '{' )
    exit_scope()      leave a block        ( '}' )  -- inner names disappear
    declare()         bind a name in the CURRENT scope
    lookup()          find a name, innermost scope first
    add_reference()   remember a line where the name is used

Memory addresses start at 0 and grow by the size of each declared type
(int = 2, float = 4, char = 1 bytes, as in the book). They are never reused.
"""
from dataclasses import dataclass, field

SIZES = {"int": 2, "float": 4, "char": 1}


class DuplicateDeclaration(Exception):
    """The name is already declared in the current scope."""

    def __init__(self, existing):
        super().__init__(existing.name)
        self.existing = existing


@dataclass
class Symbol:
    name: str
    type: str
    address: int
    line_declared: int
    scope: int                      # 0 = global, 1 = inside the first { }, ...
    dim: int = 0                    # array dimensions (always 0 in the basic language)
    references: set = field(default_factory=set)   # lines where it is used (not the declaration line)
    initialized: bool = False       # has it been given a value yet?
    used: bool = False              # has it been read/assigned after its declaration?


class SymbolTable:
    def __init__(self):
        self._scopes = [{}]         # stack of dicts: name -> Symbol
        self._symbols = []          # every symbol ever declared, in order (for printing)
        self._next_address = 0

    @property
    def depth(self):
        return len(self._scopes) - 1

    def new_scope(self):
        self._scopes.append({})

    def exit_scope(self):
        if len(self._scopes) == 1:
            raise RuntimeError("cannot exit the global scope")
        self._scopes.pop()

    def declare(self, name, type_, line):
        current = self._scopes[-1]
        if name in current:
            raise DuplicateDeclaration(current[name])
        symbol = Symbol(name, type_, self._next_address, line, self.depth)
        self._next_address += SIZES[type_]
        current[name] = symbol
        self._symbols.append(symbol)
        return symbol

    def lookup(self, name):
        for scope in reversed(self._scopes):
            if name in scope:
                return scope[name]
        return None

    def add_reference(self, symbol, line):
        symbol.used = True
        if line != symbol.line_declared:
            symbol.references.add(line)

    def all_symbols(self):
        return list(self._symbols)
