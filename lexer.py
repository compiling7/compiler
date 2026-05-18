"""Rust-like language lexer"""

import re
from token_types import Token, KEYWORDS, SINGLE_CHAR_TOKENS, TWO_CHAR_TOKENS, TT_ERROR, TT_EOF, TT_DOT, TT_DOTDOT, TT_DOTDOT_EQ


class Lexer:
    """Lexical analyzer for Rust-like language"""

    def __init__(self, source_code):
        self.source = source_code
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []

    def tokenize(self):
        """Tokenize the entire source code"""
        while self.pos < len(self.source):
            self.skip_whitespace_and_comments()
            if self.pos >= len(self.source):
                break

            token = self.next_token()
            if token:
                self.tokens.append(token)
                if token.type == TT_ERROR:
                    break

        # Add end-of-file token
        self.tokens.append(Token(TT_EOF, "", self.line, self.column))
        return self.tokens

    def skip_whitespace_and_comments(self):
        """Skip whitespace and comments"""
        while self.pos < len(self.source):
            ch = self.source[self.pos]

            # Skip whitespace (including newlines)
            if ch in ' \t\r\n':
                self.advance()
            # Skip single-line comments
            elif self.pos + 1 < len(self.source) and self.source[self.pos:self.pos + 2] == "//":
                while self.pos < len(self.source) and self.source[self.pos] != '\n':
                    self.advance()
            # Skip multi-line comments
            elif self.pos + 1 < len(self.source) and self.source[self.pos:self.pos + 2] == "/*":
                start_line = self.line
                start_col = self.column
                self.advance()  # skip /
                self.advance()  # skip *
                while self.pos + 1 < len(self.source):
                    if self.source[self.pos:self.pos + 2] == "*/":
                        self.advance()  # skip *
                        self.advance()  # skip /
                        break
                    if self.source[self.pos] == '\n':
                        self.line += 1
                        self.column = 1
                    else:
                        self.column += 1
                    self.pos += 1
                if self.pos + 1 >= len(self.source):
                    # Unterminated multi-line comment
                    self.column = start_col
                    self.line = start_line
            else:
                break

    def advance(self):
        """Move to the next character"""
        if self.pos < len(self.source):
            if self.source[self.pos] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.pos += 1

    def peek(self, offset=1):
        """Look at the next character without consuming it"""
        if self.pos + offset <= len(self.source):
            return self.source[self.pos + offset - 1]
        return None

    def next_token(self):
        """Get the next token"""
        if self.pos >= len(self.source):
            return Token(TT_EOF, "", self.line, self.column)

        start_line = self.line
        start_col = self.column
        ch = self.source[self.pos]

        # Letter or underscore - identifier or keyword
        if ch.isalpha() or ch == '_':
            return self.read_identifier()
        # Digit - number
        elif ch.isdigit():
            return self.read_number()
        # Dot operators (., .., ..=)
        elif ch == '.':
            return self.read_dot_ops()
        # Two-character operators
        elif self.pos + 1 < len(self.source):
            two_char = self.source[self.pos:self.pos + 2]
            if two_char in TWO_CHAR_TOKENS:
                self.advance()
                self.advance()
                return Token(TWO_CHAR_TOKENS[two_char], two_char, start_line, start_col)
        # Single character operators/delimiters
        if ch in SINGLE_CHAR_TOKENS:
            self.advance()
            return Token(SINGLE_CHAR_TOKENS[ch], ch, start_line, start_col)

        # Unknown character
        self.advance()
        return Token(TT_ERROR, f"未知字符 '{ch}'", start_line, start_col)

    def read_identifier(self):
        """Read an identifier or keyword"""
        start_line = self.line
        start_col = self.column
        result = ""

        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
            result += self.source[self.pos]
            self.advance()

        # Check if it's a keyword
        if result in KEYWORDS:
            return Token(KEYWORDS[result], result, start_line, start_col)
        else:
            return Token("ID", result, start_line, start_col)

    def read_number(self):
        """Read a number literal"""
        start_line = self.line
        start_col = self.column
        result = ""

        while self.pos < len(self.source) and self.source[self.pos].isdigit():
            result += self.source[self.pos]
            self.advance()

        return Token("NUM", result, start_line, start_col)

    def read_dot_ops(self):
        """Handle ., .., ..= operators"""
        start_line = self.line
        start_col = self.column
        self.advance()  # consume first .

        if self.pos < len(self.source) and self.source[self.pos] == '.':
            self.advance()  # consume second .
            if self.pos < len(self.source) and self.source[self.pos] == '=':
                self.advance()  # consume =
                return Token(TT_DOTDOT_EQ, "..=", start_line, start_col)
            return Token(TT_DOTDOT, "..", start_line, start_col)

        return Token(TT_DOT, ".", start_line, start_col)

    def format_tokens(self):
        """Format tokens for display"""
        if not self.tokens:
            self.tokenize()
        return "\n".join([str(t) for t in self.tokens if t.type != TT_EOF])