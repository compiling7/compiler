"""Token types for Rust-like language lexer"""

# Token type constants
TT_EOF = "EOF"
TT_ERROR = "ERROR"

# Keywords
TT_KEYWORD_I32 = "I32"
TT_KEYWORD_LET = "LET"
TT_KEYWORD_IF = "IF"
TT_KEYWORD_ELSE = "ELSE"
TT_KEYWORD_WHILE = "WHILE"
TT_KEYWORD_RETURN = "RETURN"
TT_KEYWORD_MUT = "MUT"
TT_KEYWORD_FN = "FN"
TT_KEYWORD_FOR = "FOR"
TT_KEYWORD_IN = "IN"
TT_KEYWORD_LOOP = "LOOP"
TT_KEYWORD_BREAK = "BREAK"
TT_KEYWORD_CONTINUE = "CONTINUE"

# Identifiers and literals
TT_ID = "ID"
TT_NUM = "NUM"

# Operators
TT_ASSIGN = "="
TT_PLUS = "+"
TT_MINUS = "-"
TT_MUL = "*"
TT_DIV = "/"
TT_EQ = "=="
TT_GT = ">"
TT_GE = ">="
TT_LT = "<"
TT_LE = "<="
TT_NE = "!="
TT_AMP = "&"

# Delimiters
TT_LPAREN = "("
TT_RPAREN = ")"
TT_LBRACE = "{"
TT_RBRACE = "}"
TT_LBRACKET = "["
TT_RBRACKET = "]"
TT_SEMICOLON = ";"
TT_COLON = ":"
TT_COMMA = ","

# Special symbols
TT_ARROW = "->"
TT_DOT = "."
TT_DOTDOT = ".."

# Comment markers (internal use, not actual tokens)
# Comments are skipped during lexing

# End marker
TT_HASH = "#"

# Keywords map
KEYWORDS = {
    "i32": TT_KEYWORD_I32,
    "let": TT_KEYWORD_LET,
    "if": TT_KEYWORD_IF,
    "else": TT_KEYWORD_ELSE,
    "while": TT_KEYWORD_WHILE,
    "return": TT_KEYWORD_RETURN,
    "mut": TT_KEYWORD_MUT,
    "fn": TT_KEYWORD_FN,
    "for": TT_KEYWORD_FOR,
    "in": TT_KEYWORD_IN,
    "loop": TT_KEYWORD_LOOP,
    "break": TT_KEYWORD_BREAK,
    "continue": TT_KEYWORD_CONTINUE,
}

# Single-character operators and delimiters
SINGLE_CHAR_TOKENS = {
    "+": TT_PLUS,
    "-": TT_MINUS,
    "*": TT_MUL,
    "/": TT_DIV,
    "(": TT_LPAREN,
    ")": TT_RPAREN,
    "{": TT_LBRACE,
    "}": TT_RBRACE,
    "[": TT_LBRACKET,
    "]": TT_RBRACKET,
    ";": TT_SEMICOLON,
    ":": TT_COLON,
    ",": TT_COMMA,
    "=": TT_ASSIGN,
    ">": TT_GT,
    "<": TT_LT,
    "!": TT_NE,
    "#": TT_HASH,
    "&": TT_AMP,
    ".": TT_DOT,
}

# Two-character operators
TWO_CHAR_TOKENS = {
    "==": TT_EQ,
    ">=": TT_GE,
    "<=": TT_LE,
    "!=": TT_NE,
    "..": TT_DOTDOT,
    "->": TT_ARROW,
}


class Token:
    """Represents a token in the source code"""

    def __init__(self, token_type, value, line, column):
        self.type = token_type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, '{self.value}', line={self.line}, col={self.column})"