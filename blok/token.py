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
    BREAK               = 104
    CONTINUE            = 105
    # Operators
    PLUS                = 201
    PLUS_EQUAL          = 202
    MINUS               = 203
    MINUS_EQUAL         = 204
    STAR                = 205
    STAR_EQUAL          = 206
    SLASH               = 207
    SLASH_EQUAL         = 208
    EQUAL               = 209
    TWO_EQUAL           = 210
    EXMARK_EQUAL        = 211
    LESS_THAN           = 212
    LESS_THAN_EQUAL     = 213
    GREATER_THAN        = 214
    GREATER_THAN_EQUAL  = 215
    AMPERSAND           = 216
    TWO_AMPERSAND       = 217
    VERT_LINE           = 218
    TWO_VERT_LINE       = 219
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
    VOID                = 309
    STRUCT              = 310
    # Separators
    SEMICOLON           = 400
    COMMA               = 401
    CURLY_BRAC_LEFT     = 402
    CURLY_BRAC_RIGHT    = 403
    ROUND_BRAC_LEFT     = 404
    ROUND_BRAC_RIGHT    = 405
    SQUARE_BRAC_LEFT    = 406
    SQUARE_BRAC_RIGHT   = 407