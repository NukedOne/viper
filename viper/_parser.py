import enum
from dataclasses import dataclass
import typing as t
from viper.tokenizer import Token, TokenKind
from abc import ABC, abstractmethod


class StatementKind(enum.Enum):
    LET = enum.auto()
    PRINT = enum.auto()
    IF = enum.auto()
    FN = enum.auto()
    WHILE = enum.auto()
    FOR = enum.auto()
    BLOCK = enum.auto()
    RETURN = enum.auto()
    EXPRESSION = enum.auto()


class ExpressionKind(enum.Enum):
    ASSIGN = enum.auto()
    BINARY = enum.auto()
    LITERAL = enum.auto()
    VARIABLE = enum.auto()
    CALL = enum.auto()


class BinaryExpressionKind(enum.Enum):
    ADD = enum.auto()
    SUB = enum.auto()
    MUL = enum.auto()
    DIV = enum.auto()
    LT = enum.auto()
    ASSIGN = enum.auto()


@dataclass
class CallExpression:
    callee: "Expression"
    args: list["Expression"]

    def __repr__(self) -> str:
        return f"{self.callee}({self.args})"


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
            case v if v == BinaryExpressionKind.LT:
                return f"({self.lhs} < {self.rhs})"
            case _:
                raise Exception("Unknown expression kind.")


@dataclass
class AssignExpression:
    lhs: "Expression"
    rhs: "Expression"

    def __repr__(self) -> str:
        return f"({self.lhs} = {self.rhs})"


@dataclass
class Expression:
    kind: ExpressionKind
    value: LiteralExpression | BinaryExpression | VariableExpression | CallExpression | AssignExpression

    def __repr__(self) -> str:
        return f"{self.value}"


@dataclass
class LetStatement:
    expr: Expression


@dataclass
class PrintStatement:
    expr: Expression


@dataclass
class IfStatement:
    condition: Expression
    then_branch: "Statement"
    else_branch: t.Optional["Statement"]


@dataclass
class FnStatement:
    name: str
    arguments: list[Expression]
    body: "Statement"


@dataclass
class BlockStatement:
    body: list["Statement"]


@dataclass
class ReturnStatement:
    expr: Expression


@dataclass
class WhileStatement:
    condition: Expression
    body: "Statement"


@dataclass
class ForStatement:
    initializer: Expression
    condition: Expression
    advancement: Expression
    body: "Statement"


@dataclass
class ExpressionStatement:
    expr: Expression


@dataclass
class Statement:
    kind: StatementKind
    stmt: LetStatement | PrintStatement | FnStatement | IfStatement | BlockStatement | ExpressionStatement | ReturnStatement | WhileStatement


@dataclass
class PrefixExpression:
    token: Token
    operand: Expression


class PrefixParselet(ABC):
    @abstractmethod
    def parse(self, parser: "Parser", token: Token) -> Expression:
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


class CallParselet(InfixParselet):
    def parse(self, parser: "Parser", left: Expression, token: Token) -> Expression:
        args = []
        if not parser.match([TokenKind.RPAREN]):
            while True:
                args.append(parser.parse_expression(0))
                if not parser.match([TokenKind.COMMA]):
                    break
            parser.consume(TokenKind.RPAREN)
        return Expression(ExpressionKind.CALL, CallExpression(left, args))


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
            case "<":
                return Expression(
                    ExpressionKind.BINARY,
                    BinaryExpression(BinaryExpressionKind.LT, left, right),
                )
            case "=":
                return Expression(
                    ExpressionKind.ASSIGN,
                    AssignExpression(left, right),
                )
            case _:
                raise Exception("Unknown operator.")


class Parser:
    prefix_parselets: dict[TokenKind, PrefixParselet] = {}
    infix_parselets: dict[TokenKind, InfixParselet] = {}
    tokens: list[Token]
    precedence: dict[TokenKind, int] = {
        TokenKind.EQUAL: 1,
        TokenKind.LT: 2,
        TokenKind.PLUS: 3,
        TokenKind.MINUS: 3,
        TokenKind.STAR: 4,
        TokenKind.SLASH: 4,
        TokenKind.LPAREN: 8,
        TokenKind.NUMBER: 10,
    }

    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.register(TokenKind.PLUS, BinaryOperatorParselet())
        self.register(TokenKind.MINUS, BinaryOperatorParselet())
        self.register(TokenKind.STAR, BinaryOperatorParselet())
        self.register(TokenKind.SLASH, BinaryOperatorParselet())
        self.register(TokenKind.EQUAL, BinaryOperatorParselet())
        self.register(TokenKind.LT, BinaryOperatorParselet())
        self.register(TokenKind.LPAREN, CallParselet())
        self.register(TokenKind.NUMBER, NumberParselet())
        self.register(TokenKind.IDENTIFIER, NameParselet())

    def register(
        self, kind: TokenKind, parselet: PrefixParselet | InfixParselet
    ) -> None:
        if isinstance(parselet, PrefixParselet):
            self.prefix_parselets[kind] = parselet
        elif isinstance(parselet, InfixParselet):
            self.infix_parselets[kind] = parselet

    def consume(self, kind: TokenKind | None) -> Token:
        assert len(self.tokens) > 0
        if kind is not None:
            assert (
                self.tokens[0].kind == kind
            ), f"found {self.tokens[0].kind}: {self.tokens[0]}, expected {kind}"
            return self.tokens.pop(0)
        return self.tokens.pop(0)

    def next_token_precedence(self) -> int:
        if self.tokens:
            return self.precedence.get(self.tokens[0].kind, 0)
        return 0

    def parse_expression(self, desired_precedence: int) -> Expression:
        token = self.consume(None)
        prefix_parselet = self.prefix_parselets.get(token.kind, None)
        assert prefix_parselet is not None, f"unable to parse token: {token}"
        left = prefix_parselet.parse(self, token)
        while desired_precedence < self.next_token_precedence():
            token = self.consume(None)
            infix_parselet = self.infix_parselets.get(token.kind, None)
            assert infix_parselet is not None, f"unable to parse token: {token}"
            left = infix_parselet.parse(self, left, token)
        return left

    def parse_print_statement(self) -> Statement:
        expr = self.parse_expression(0)
        self.consume(TokenKind.SEMICOLON)
        return Statement(StatementKind.PRINT, PrintStatement(expr))

    def parse_let_statement(self) -> Statement:
        expr = self.parse_expression(0)
        self.consume(TokenKind.SEMICOLON)
        return Statement(StatementKind.LET, LetStatement(expr))

    def check(self, kind: TokenKind) -> bool:
        return self.tokens[0].kind == kind

    def match(self, kinds: list[TokenKind]) -> bool:
        for kind in kinds:
            if self.check(kind):
                self.consume(kind)
                return True
        return False

    def parse_while_statement(self) -> Statement:
        self.consume(TokenKind.LPAREN)
        condition = self.parse_expression(0)
        self.consume(TokenKind.RPAREN)
        body = self.parse_statement()
        return Statement(StatementKind.WHILE, WhileStatement(condition, body))

    def parse_for_statement(self) -> Statement:
        self.consume(TokenKind.LPAREN)
        self.consume(TokenKind.LET)
        initializer = self.parse_expression(0)
        self.consume(TokenKind.SEMICOLON)
        condition = self.parse_expression(0)
        self.consume(TokenKind.SEMICOLON)
        advancement = self.parse_expression(0)
        self.consume(TokenKind.RPAREN)
        body = self.parse_statement()
        return Statement(
            StatementKind.FOR, ForStatement(initializer, condition, advancement, body)
        )

    def parse_fn_statement(self) -> Statement:
        name = self.consume(TokenKind.IDENTIFIER)
        self.consume(TokenKind.LPAREN)
        arguments = []
        if not self.match([TokenKind.RPAREN]):
            while True:
                arguments.append(self.parse_expression(0))
                if not self.match([TokenKind.COMMA]):
                    break
            self.consume(TokenKind.RPAREN)
        body = self.parse_statement()
        return Statement(StatementKind.FN, FnStatement(name.value, arguments, body))

    def parse_return_statement(self) -> Statement:
        expr = self.parse_expression(0)
        self.consume(TokenKind.SEMICOLON)
        return Statement(StatementKind.RETURN, ReturnStatement(expr))

    def parse_if_statement(self) -> Statement:
        self.consume(TokenKind.LPAREN)
        condition = self.parse_expression(0)
        self.consume(TokenKind.RPAREN)
        then_branch = self.parse_statement()
        else_branch = None
        if self.match([TokenKind.ELSE]):
            else_branch = self.parse_statement()
        return Statement(
            StatementKind.IF, IfStatement(condition, then_branch, else_branch)
        )

    def parse_block_statement(self) -> Statement:
        body = []
        while not self.match([TokenKind.RBRACE]):
            body.append(self.parse_statement())
        return Statement(StatementKind.BLOCK, BlockStatement(body))

    def parse_expression_statement(self) -> Statement:
        expr = self.parse_expression(0)
        self.consume(TokenKind.SEMICOLON)
        return Statement(StatementKind.EXPRESSION, ExpressionStatement(expr))

    def parse_statement(self) -> Statement:
        if self.match([TokenKind.LET]):
            return self.parse_let_statement()
        elif self.match([TokenKind.PRINT]):
            return self.parse_print_statement()
        elif self.match([TokenKind.FN]):
            return self.parse_fn_statement()
        elif self.match([TokenKind.WHILE]):
            return self.parse_while_statement()
        elif self.match([TokenKind.FOR]):
            return self.parse_for_statement()
        elif self.match([TokenKind.IF]):
            return self.parse_if_statement()
        elif self.match([TokenKind.RETURN]):
            return self.parse_return_statement()
        elif self.match([TokenKind.LBRACE]):
            return self.parse_block_statement()
        else:
            return self.parse_expression_statement()

    def parse(self) -> list[Statement]:
        ast = []
        while not self.tokens[0].kind == TokenKind.EOF:
            ast.append(self.parse_statement())
        return ast
