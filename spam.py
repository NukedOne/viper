from dataclasses import dataclass
import enum

source = "print 1 + 2*3 - 4/5;"


class TokenKind(enum.Enum):
    PRINT = enum.auto()
    NUMBER = enum.auto()
    PLUS = enum.auto()
    MINUS = enum.auto()
    STAR = enum.auto()
    SLASH = enum.auto()
    IDENTIFIER = enum.auto()


@dataclass
class Token:
    kind: TokenKind
    value: str

    def __repr__(self) -> str:
        return self.value


def lookahead(source: str, current: int, thing: str) -> bool:
    return source[current : current + len(thing)] == thing


def identifier(source: str, current: int) -> Token:
    c = current
    while source[c].isalpha() or source[c].isdigit() or source[c] == "_":
        c += 1
    return Token(TokenKind.IDENTIFIER, source[current:c])


def tokenize(source: str) -> list[Token]:
    current = 0
    tokens = []
    while current < len(source):
        match source[current]:
            case v if v == "p":
                if lookahead(source, current, "rint"):
                    tokens.append(Token(TokenKind.PRINT, "print"))
                    continue
                tokens.append(identifier(source, current))
            case v if v == "+":
                tokens.append(Token(TokenKind.PLUS, "+"))
            case v if v == "-":
                tokens.append(Token(TokenKind.MINUS, "-"))
            case v if v == "*":
                tokens.append(Token(TokenKind.STAR, "*"))
            case v if v == "/":
                tokens.append(Token(TokenKind.SLASH, "/"))
        current += 1
    return tokens


def main() -> None:
    tokens = tokenize(source)
    print(tokens)


if __name__ == "__main__":
    main()
