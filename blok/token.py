from enum import Enum


class Token:
    def __init__(self, kind, value, line):
        self.kind = kind
        self.value = value
        self.line = line

    def __str__(self):
        return f"<Token kind=\"{self.kind}\" value=\"{self.value}\" line=\"{self.line}\"/>"


class TokenKind(Enum):
    EOF                 = 100
    INVALID             = 101
    IDENT               = 102
    INT_LITERAL         = 103
    # Operators
    PLUS                = 201
    MINUS               = 202
    STAR                = 203
    SLASH               = 204
    EQUAL               = 205
    TWO_EQUAL           = 206
    EXMARK_EQUAL        = 207
    LESS_THAN           = 208
    LESS_THAN_EQUAL     = 209
    GREATER_THAN        = 210
    GREATER_THAN_EQUAL  = 211
    # Keywords
    IF                  = 300
    ELSE                = 301
    WHILE               = 302
    FOR                 = 303
    STEP                = 304
    DOT                 = 305
    TWO_DOT             = 306
    RETURN              = 307
    INT                 = 308
    INT_PTR             = 309
    VOID                = 310
    # Separators
    SEMICOLON           = 400
    COMMA               = 401
    CURLY_BRAC_LEFT     = 402
    CURLY_BRAC_RIGHT    = 403
    ROUND_BRAC_LEFT     = 404
    ROUND_BRAC_RIGHT    = 405