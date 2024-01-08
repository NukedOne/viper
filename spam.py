from abc import ABC, abstractmethod
from dataclasses import dataclass
import enum

source = "let x = 1 + 2*3 - 4/5; print x;"


class TokenKind(enum.Enum):
    PRINT = enum.auto()
    LET = enum.auto()
    NUMBER = enum.auto()
    PLUS = enum.auto()
    MINUS = enum.auto()
    STAR = enum.auto()
    SLASH = enum.auto()
    EQUAL = enum.auto()
    SEMICOLON = enum.auto()
    IDENTIFIER = enum.auto()
    EOF = enum.auto()


@dataclass
class Token:
    kind: TokenKind
    value: str

    def __repr__(self) -> str:
        return self.value


def lookahead(source: str, current: int, thing: str) -> bool:
    return source[current + 1 : current + len(thing) + 1] == thing


def identifier(source: str, current: int) -> Token:
    c = current
    while source[c].isalpha() or source[c].isdigit() or source[c] == "_":
        c += 1
    return Token(TokenKind.IDENTIFIER, source[current:c])


def number(source: str, current: int) -> Token:
    c = current
    while source[c].isdigit():
        c += 1
    return Token(TokenKind.NUMBER, source[current:c])


def tokenize(source: str) -> list[Token]:
    current = 0
    tokens = []
    while current < len(source):
        while source[current].isspace():
            current += 1
        match source[current]:
            case v if v == "l":
                if lookahead(source, current, "et"):
                    tokens.append(Token(TokenKind.LET, "let"))
                    current += 3
                else:
                    tokens.append(identifier(source, current))
            case v if v == "p":
                if lookahead(source, current, "rint"):
                    tokens.append(Token(TokenKind.PRINT, "print"))
                    current += 5
                else:
                    tokens.append(identifier(source, current))
            case v if v.isalpha():
                tokens.append(identifier(source, current))
            case v if v.isdigit():
                tokens.append(number(source, current))
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
            case _:
                raise Exception("Unknown token.")
        current += 1
    tokens.append(Token(TokenKind.EOF, ""))
    return tokens


class StatementKind(enum.Enum):
    LET = enum.auto()
    PRINT = enum.auto()


class ExpressionKind(enum.Enum):
    ASSIGN = enum.auto()
    BINARY = enum.auto()
    LITERAL = enum.auto()
    VARIABLE = enum.auto()


class BinaryExpressionKind(enum.Enum):
    ADD = enum.auto()
    SUB = enum.auto()
    MUL = enum.auto()
    DIV = enum.auto()
    ASSIGN = enum.auto()


@dataclass
class LiteralExpression:
    expr: float

    def __repr__(self) -> str:
        return str(self.expr)


@dataclass
class VariableExpression:
    name: str

    def __repr__(self) -> str:
        return self.name


@dataclass
class BinaryExpression:
    kind: "BinaryExpressionKind"
    lhs: "Expression"
    rhs: "Expression"

    def __repr__(self) -> str:
        match self.kind:
            case v if v == BinaryExpressionKind.ADD:
                return f"({self.lhs} + {self.rhs})"
            case v if v == BinaryExpressionKind.SUB:
                return f"({self.lhs} - {self.rhs})"
            case v if v == BinaryExpressionKind.MUL:
                return f"({self.lhs} * {self.rhs})"
            case v if v == BinaryExpressionKind.DIV:
                return f"({self.lhs} / {self.rhs})"
            case v if v == BinaryExpressionKind.ASSIGN:
                return f"({self.lhs} = {self.rhs})"
            case _:
                raise Exception("Unknown expression kind.")


@dataclass
class Expression:
    kind: ExpressionKind
    value: LiteralExpression | BinaryExpression | VariableExpression

    def __repr__(self) -> str:
        return f"{self.value}"


@dataclass
class LetStatement:
    expr: Expression


@dataclass
class PrintStatement:
    expr: Expression


@dataclass
class Statement:
    kind: StatementKind
    stmt: LetStatement | PrintStatement


@dataclass
class PrefixExpression:
    token: Token
    operand: Expression


class PrefixParselet(ABC):
    @abstractmethod
    def parse(self) -> Expression:
        pass


class NumberParselet(PrefixParselet):
    def parse(self, parser: "Parser", token: Token):
        return Expression(ExpressionKind.LITERAL, LiteralExpression(float(token.value)))


class NameParselet(PrefixParselet):
    def parse(self, parser: "Parser", token: Token):
        return Expression(ExpressionKind.VARIABLE, VariableExpression(token.value))


class InfixParselet(ABC):
    @abstractmethod
    def parse(self, parser: "Parser", left: Expression, token: Token) -> Expression:
        pass


class BinaryOperatorParselet(InfixParselet):
    def parse(self, parser: "Parser", left: Expression, token: Token) -> Expression:
        right = parser.parse_expression(parser.precedence[token.kind])
        match token.value:
            case "+":
                return Expression(
                    ExpressionKind.BINARY,
                    BinaryExpression(BinaryExpressionKind.ADD, left, right),
                )
            case "-":
                return Expression(
                    ExpressionKind.BINARY,
                    BinaryExpression(BinaryExpressionKind.SUB, left, right),
                )
            case "*":
                return Expression(
                    ExpressionKind.BINARY,
                    BinaryExpression(BinaryExpressionKind.MUL, left, right),
                )
            case "/":
                return Expression(
                    ExpressionKind.BINARY,
                    BinaryExpression(BinaryExpressionKind.DIV, left, right),
                )
            case "=":
                return Expression(
                    ExpressionKind.ASSIGN,
                    BinaryExpression(BinaryExpressionKind.ASSIGN, left, right),
                )
            case _:
                raise Exception("Unknown operator.")


class Parser:
    prefix_parselets: dict[TokenKind, PrefixParselet] = {}
    infix_parselets: dict[TokenKind, InfixParselet] = {}
    tokens: list[Token]
    precedence: dict[TokenKind, int] = {
        TokenKind.EQUAL: 1,
        TokenKind.PLUS: 3,
        TokenKind.MINUS: 3,
        TokenKind.STAR: 4,
        TokenKind.SLASH: 4,
        TokenKind.NUMBER: 10,
    }

    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.register(TokenKind.PLUS, BinaryOperatorParselet())
        self.register(TokenKind.MINUS, BinaryOperatorParselet())
        self.register(TokenKind.STAR, BinaryOperatorParselet())
        self.register(TokenKind.SLASH, BinaryOperatorParselet())
        self.register(TokenKind.EQUAL, BinaryOperatorParselet())
        self.register(TokenKind.NUMBER, NumberParselet())
        self.register(TokenKind.IDENTIFIER, NameParselet())

    def register(
        self, kind: TokenKind, parselet: PrefixParselet | InfixParselet
    ) -> None:
        if isinstance(parselet, PrefixParselet):
            self.prefix_parselets[kind] = parselet
        elif isinstance(parselet, InfixParselet):
            self.infix_parselets[kind] = parselet

    def consume(self) -> Token:
        assert len(self.tokens) > 0
        return self.tokens.pop(0)

    def next_token_precedence(self) -> int:
        if self.tokens:
            return self.precedence.get(self.tokens[0].kind, 0)
        return 0

    def parse_expression(self, desired_precedence: int) -> Expression:
        token = self.consume()
        prefix_parselet = self.prefix_parselets.get(token.kind, None)
        left = prefix_parselet.parse(self, token)
        while desired_precedence < self.next_token_precedence():
            token = self.consume()
            infix_parselet = self.infix_parselets.get(token.kind, None)
            left = infix_parselet.parse(self, left, token)
        return left

    def parse_print_statement(self) -> Statement:
        self.consume()  # consume 'print'
        expr = self.parse_expression(0)
        self.consume()  # consume ';'
        return Statement(StatementKind.PRINT, PrintStatement(expr))

    def parse_let_statement(self) -> Statement:
        self.consume()  # consume 'let'
        expr = self.parse_expression(0)
        self.consume()  # consume ';'
        return Statement(StatementKind.LET, LetStatement(expr))

    def parse_statement(self) -> Statement:
        match self.tokens[0].value:
            case v if v == "let":
                return self.parse_let_statement()
            case v if v == "print":
                return self.parse_print_statement()
            case _:
                pass

    def parse(self) -> list[Statement]:
        ast = []
        while not self.tokens[0].kind == TokenKind.EOF:
            ast.append(self.parse_statement())
        return ast


@dataclass
class Interpreter:
    ast: Statement
    globals: dict[str, float]

    def exec(self) -> None:
        while self.ast:
            stmt = self.ast.pop(0)
            match stmt:
                case v if v.kind == StatementKind.PRINT:
                    expr = self._eval(v.stmt.expr)
                    print(expr)
                case v if v.kind == StatementKind.LET:
                    expr = self._eval(v.stmt.expr)

    def _eval(self, expr: Expression):
        match expr.kind:
            case ExpressionKind.LITERAL:
                return expr.value.expr
            case ExpressionKind.VARIABLE:
                return self.globals[expr.value.name]
            case ExpressionKind.ASSIGN:
                self.globals[expr.value.lhs.value.name] = self._eval(expr.value.rhs)
            case ExpressionKind.BINARY:
                match expr.value.kind:
                    case BinaryExpressionKind.ADD:
                        return self._eval(expr.value.lhs) + self._eval(expr.value.rhs)
                    case BinaryExpressionKind.SUB:
                        return self._eval(expr.value.lhs) - self._eval(expr.value.rhs)
                    case BinaryExpressionKind.MUL:
                        return self._eval(expr.value.lhs) * self._eval(expr.value.rhs)
                    case BinaryExpressionKind.DIV:
                        return self._eval(expr.value.lhs) / self._eval(expr.value.rhs)


def main() -> None:
    tokens = tokenize(source)
    print(tokens)
    parser = Parser(tokens)
    ast = parser.parse()
    print(ast)
    interpreter = Interpreter(ast, {})
    interpreter.exec()


if __name__ == "__main__":
    main()
