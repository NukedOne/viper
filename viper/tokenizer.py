from dataclasses import dataclass
import enum


class Tokenizer:
    def __init__(self, source: str) -> None:
        self.source = source
        self.current: int = 0

    def identifier(self) -> "Token":
        c = self.current
        while (
            self.source[c].isalpha()
            or self.source[c].isdigit()
            or self.source[c] == "_"
        ):
            c += 1
        token = Token(TokenKind.IDENTIFIER, self.source[self.current : c])
        self.current = c - 1
        return token

    def number(self) -> "Token":
        c = self.current
        while self.source[c].isdigit():
            c += 1
        token = Token(TokenKind.NUMBER, self.source[self.current : c])
        self.current = c - 1
        return token

    def lookahead(self, thing: str) -> bool:
        if self.source[self.current + 1 : self.current + len(thing) + 1] == thing:
            self.current += len(thing)
            return True
        return False

    def tokenize(self) -> list["Token"]:
        tokens = []
        while self.current < len(self.source):
            if self.source[self.current].isspace():
                self.current += 1
                continue
            match self.source[self.current]:
                case v if v == "i":
                    if self.lookahead("f"):
                        tokens.append(Token(TokenKind.IF, "if"))
                    else:
                        tokens.append(self.identifier())
                case v if v == "f":
                    if self.lookahead("n"):
                        tokens.append(Token(TokenKind.FN, "fn"))
                    elif self.lookahead("or"):
                        tokens.append(Token(TokenKind.FOR, "for"))
                    else:
                        tokens.append(self.identifier())
                case v if v == "e":
                    if self.lookahead("lse"):
                        tokens.append(Token(TokenKind.ELSE, "else"))
                    else:
                        tokens.append(self.identifier())
                case v if v == "l":
                    if self.lookahead("et"):
                        tokens.append(Token(TokenKind.LET, "let"))
                    else:
                        tokens.append(self.identifier())
                case v if v == "p":
                    if self.lookahead("rint"):
                        tokens.append(Token(TokenKind.PRINT, "print"))
                    else:
                        tokens.append(self.identifier())
                case v if v == "r":
                    if self.lookahead("eturn"):
                        tokens.append(Token(TokenKind.RETURN, "return"))
                    else:
                        tokens.append(self.identifier())
                case v if v == "w":
                    if self.lookahead("hile"):
                        tokens.append(Token(TokenKind.WHILE, "while"))
                    else:
                        tokens.append(self.identifier())
                case v if v.isalpha():
                    tokens.append(self.identifier())
                case v if v.isdigit():
                    tokens.append(self.number())
                case v if v == "+":
                    tokens.append(Token(TokenKind.PLUS, "+"))
                case v if v == "-":
                    tokens.append(Token(TokenKind.MINUS, "-"))
                case v if v == "*":
                    tokens.append(Token(TokenKind.STAR, "*"))
                case v if v == "/":
                    tokens.append(Token(TokenKind.SLASH, "/"))
                case v if v == "=":
                    tokens.append(Token(TokenKind.EQUAL, "="))
                case v if v == ";":
                    tokens.append(Token(TokenKind.SEMICOLON, ";"))
                case v if v == ",":
                    tokens.append(Token(TokenKind.COMMA, ","))
                case v if v == "(":
                    tokens.append(Token(TokenKind.LPAREN, "("))
                case v if v == ")":
                    tokens.append(Token(TokenKind.RPAREN, ")"))
                case v if v == "{":
                    tokens.append(Token(TokenKind.LBRACE, "{"))
                case v if v == "}":
                    tokens.append(Token(TokenKind.RBRACE, "}"))
                case v if v == ",":
                    tokens.append(Token(TokenKind.COMMA, ","))
                case v if v == "<":
                    tokens.append(Token(TokenKind.LT, "<"))
                case _:
                    raise Exception("Unknown token.")
            self.current += 1
        tokens.append(Token(TokenKind.EOF, ""))
        return tokens


@dataclass
class Token:
    kind: "TokenKind"
    value: str

    def __repr__(self) -> str:
        return f"Token(kind={self.kind}, value={self.value})"


class TokenKind(enum.Enum):
    PRINT = enum.auto()
    LET = enum.auto()
    NUMBER = enum.auto()
    PLUS = enum.auto()
    MINUS = enum.auto()
    STAR = enum.auto()
    SLASH = enum.auto()
    EQUAL = enum.auto()
    LPAREN = enum.auto()
    RPAREN = enum.auto()
    LBRACE = enum.auto()
    RBRACE = enum.auto()
    IF = enum.auto()
    ELSE = enum.auto()
    FN = enum.auto()
    WHILE = enum.auto()
    FOR = enum.auto()
    RETURN = enum.auto()
    LT = enum.auto()
    COMMA = enum.auto()
    SEMICOLON = enum.auto()
    IDENTIFIER = enum.auto()
    EOF = enum.auto()
