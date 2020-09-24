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
        elif c == ";":      self.add_token(TokenKind.SEMICOLON)
        elif c == ",":      self.add_token(TokenKind.COMMA)
        elif c == ".":      self.try_read_pair(TokenKind.DOT, ".", TokenKind.TWO_DOT)
        elif c == "=":      self.try_read_pair(TokenKind.EQUAL, "=", TokenKind.TWO_EQUAL)
        elif c == "!":      self.try_read_pair(TokenKind.INVALID, "=", TokenKind.EXMARK_EQUAL)
        elif c == "<":      self.try_read_pair(TokenKind.LESS_THAN, "=", TokenKind.LESS_THAN_EQUAL)
        elif c == ">":      self.try_read_pair(TokenKind.GREATER_THAN, "=", TokenKind.GREATER_THAN_EQUAL)
        elif c.isdecimal(): self.read_number()
        elif c.isalpha():   self.read_ident()
        else:
            print(f"invalid character '{c}'")
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
        number = ""
        peek = self.text[self.char_idx]
        while True:
            number += peek
            if self.char_idx + 1 == len(self.text):
                break

            peek = self.text[self.char_idx + 1]
            if not peek.isdecimal():
                break

            self.char_idx += 1

        self.add_token(TokenKind.INT_LITERAL, int(number))

    def read_ident(self):
        ident = ""
        peek = self.text[self.char_idx]
        while True:
            ident += peek
            if self.char_idx + 1 == len(self.text):
                break

            peek = self.text[self.char_idx + 1]
            if not peek.isalpha():
                break

            self.char_idx += 1

        if   ident == "if":     self.add_token(TokenKind.IF)
        elif ident == "else":   self.add_token(TokenKind.ELSE)
        elif ident == "while":  self.add_token(TokenKind.WHILE)
        elif ident == "for":    self.add_token(TokenKind.FOR)
        elif ident == "step":   self.add_token(TokenKind.STEP)
        elif ident == "void":   self.add_token(TokenKind.VOID)
        elif ident == "return": self.add_token(TokenKind.RETURN)
        elif ident == "int":    self.try_read_pair(TokenKind.INT, ">", TokenKind.INT_PTR)
        else:                   self.add_token(TokenKind.IDENT, ident)