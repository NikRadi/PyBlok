from blok.error import errors, CompileError
from blok.token import Token, TokenKind


class Lexer:
    def __init__(self, text):
        self.text = text
        self.char_idx = 0
        self.token_idx = 0
        self.line = 1
        self.tokens = []

    def peek_token(self, forward_amount=0):
        num_tokens_to_read = (self.token_idx + 1 + forward_amount) - len(self.tokens)
        for _ in range(num_tokens_to_read):
            self.read_token()

        return self.tokens[self.token_idx + forward_amount]

    def eat_next_token(self):
        self.token_idx += 1

    def add_err(self, msg):
        errors.append(CompileError(None, self.line, msg))

    def add_token(self, kind, value=""):
        self.tokens.append(Token(kind, value, self.line))

    def read_token(self):
        while True:
            if self.char_idx == len(self.text):
                self.add_token(TokenKind.EOF)
                return

            c = self.text[self.char_idx]
            if c == "\n":
                self.char_idx += 1
                self.line += 1
            elif c == " ":
                self.char_idx += 1
            else:
                break

        c = self.text[self.char_idx]
        if   c == "+":      self.try_read_pair(TokenKind.PLUS, "=", TokenKind.PLUS_EQUAL)
        elif c == "-":      self.try_read_pair(TokenKind.MINUS, "=", TokenKind.MINUS_EQUAL)
        elif c == "*":      self.try_read_pair(TokenKind.STAR, "=", TokenKind.STAR_EQUAL)
        elif c == "/":      self.try_read_pair(TokenKind.SLASH, "=", TokenKind.SLASH_EQUAL)
        elif c == "{":      self.add_token(TokenKind.CURLY_BRAC_LEFT)
        elif c == "}":      self.add_token(TokenKind.CURLY_BRAC_RIGHT)
        elif c == "(":      self.add_token(TokenKind.ROUND_BRAC_LEFT)
        elif c == ")":      self.add_token(TokenKind.ROUND_BRAC_RIGHT)
        elif c == "[":      self.add_token(TokenKind.SQUARE_BRAC_LEFT)
        elif c == "]":      self.add_token(TokenKind.SQUARE_BRAC_RIGHT)
        elif c == ";":      self.add_token(TokenKind.SEMICOLON)
        elif c == ",":      self.add_token(TokenKind.COMMA)
        elif c == ".":      self.try_read_pair(TokenKind.DOT, ".", TokenKind.TWO_DOT)
        elif c == "=":      self.try_read_pair(TokenKind.EQUAL, "=", TokenKind.TWO_EQUAL)
        elif c == "!":      self.try_read_pair(TokenKind.INVALID, "=", TokenKind.EXMARK_EQUAL)
        elif c == "<":      self.try_read_pair(TokenKind.LESS_THAN, "=", TokenKind.LESS_THAN_EQUAL)
        elif c == ">":      self.try_read_pair(TokenKind.GREATER_THAN, "=", TokenKind.GREATER_THAN_EQUAL)
        elif c == "&":      self.try_read_pair(TokenKind.AMPERSAND, "&", TokenKind.TWO_AMPERSAND)
        elif c == "|":      self.try_read_pair(TokenKind.VERT_LINE, "|", TokenKind.TWO_VERT_LINE)
        elif c.isdecimal(): self.read_number()
        elif c.isalpha():   self.read_ident()
        else:
            self.add_err(f"invalid character '{c}'")
            self.add_token(TokenKind.INVALID)

        self.char_idx += 1

    def try_read_pair(self, kind1, char2, kind2):
        peek_idx = self.char_idx + 1
        if peek_idx < len(self.text) and self.text[peek_idx] == char2:
            self.char_idx += 1
            self.add_token(kind2)
        else:
            self.add_token(kind1)

    def read_number(self):
        peek = self.text[self.char_idx]
        if peek == "0" and self.char_idx + 1 != len(self.text) and \
           self.text[self.char_idx + 1] == "x" or \
           self.text[self.char_idx + 1] == "b":
            self.char_idx += 1
            inttype_char = self.text[self.char_idx].lower()
            if self.char_idx + 1 == len(self.text):
                self.add_err(f"invalid integer '0{inttype_char}'")
            else:
                self.char_idx += 1
                if inttype_char == "x":
                    self.read_hex_number()
                elif inttype_char == "b":
                    self.read_bin_number()
        else:
            number = self.read_number_stream(lambda x: x.isdecimal())
            self.add_token(TokenKind.INT_LITERAL, int(number))

    def read_hex_number(self):
        is_valid_char = lambda x: x.isdecimal() or x.lower() in "abcdec"
        if not is_valid_char(self.text[self.char_idx]):
            self.add_err(f"invalid hexidecimal integer '0x'")
            number = "0"
        else:
            number = self.read_number_stream(is_valid_char)

        self.add_token(TokenKind.INT_LITERAL, int(number, base=16))

    def read_bin_number(self):
        is_valid_char = lambda x: x == "0" or x == "1"
        if not is_valid_char(self.text[self.char_idx]):
            self.add_err(f"invalid binary integer '0b'")
            number = "0"
        else:
            number = self.read_number_stream(is_valid_char)

        self.add_token(TokenKind.INT_LITERAL, int(number, base=2))

    def read_number_stream(self, is_valid_char_func):
        peek = self.text[self.char_idx]
        number = ""
        was_last_char_underscore = False
        while True:
            if not was_last_char_underscore:
                number += peek

            if self.char_idx + 1 == len(self.text):
                break

            peek = self.text[self.char_idx + 1]
            if peek == "_":
                if was_last_char_underscore:
                    self.add_err("invalid integer containing two '_' in a row")
                else:
                    was_last_char_underscore = True
                    self.char_idx += 1
                    continue
            elif is_valid_char_func(peek):
                was_last_char_underscore = False
            else:
                break

            self.char_idx += 1

        if was_last_char_underscore:
            self.add_err(f"invalid integer ending with '_'")

        return number

    def read_ident(self):
        ident = ""
        peek = self.text[self.char_idx]
        while True:
            ident += peek
            if self.char_idx + 1 == len(self.text):
                break

            peek = self.text[self.char_idx + 1]
            if not peek.isalpha() and not peek.isdecimal() and peek != "_":
                break

            self.char_idx += 1

        if   ident == "if":       self.add_token(TokenKind.IF)
        elif ident == "else":     self.add_token(TokenKind.ELSE)
        elif ident == "while":    self.add_token(TokenKind.WHILE)
        elif ident == "for":      self.add_token(TokenKind.FOR)
        elif ident == "step":     self.add_token(TokenKind.STEP)
        elif ident == "void":     self.add_token(TokenKind.VOID)
        elif ident == "return":   self.add_token(TokenKind.RETURN)
        elif ident == "break":    self.add_token(TokenKind.BREAK)
        elif ident == "continue": self.add_token(TokenKind.CONTINUE)
        elif ident == "int":      self.add_token(TokenKind.INT)
        else:                     self.add_token(TokenKind.IDENT, ident)