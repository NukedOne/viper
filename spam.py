from abc import ABC, abstractmethod
from dataclasses import dataclass
import enum
import textwrap
import typing as t

source = textwrap.dedent(
    """
    fn fib(n) {
        if (n < 2) return n;
        return fib(n-1)+fib(n-2);
    }
    print fib(10);
    """
)


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
    RETURN = enum.auto()
    LT = enum.auto()
    COMMA = enum.auto()
    SEMICOLON = enum.auto()
    IDENTIFIER = enum.auto()
    EOF = enum.auto()


@dataclass
class Token:
    kind: TokenKind
    value: str

    def __repr__(self) -> str:
        return self.value


@dataclass
class Tokenizer:
    source: str
    current: int = 0

    def identifier(self) -> Token:
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

    def number(self) -> Token:
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

    def tokenize(self) -> list[Token]:
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
                case v if v == "<":
                    tokens.append(Token(TokenKind.LT, "<"))
                case _:
                    raise Exception("Unknown token.")
            self.current += 1
        tokens.append(Token(TokenKind.EOF, ""))
        return tokens


class StatementKind(enum.Enum):
    LET = enum.auto()
    PRINT = enum.auto()
    IF = enum.auto()
    FN = enum.auto()
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
class IfStatement:
    condition: Expression
    then_branch: "Statement"
    else_branch: t.Optional["Statement"]


@dataclass
class FnStatement:
    name: str
    arguments: list[Expression]
    body: list["Statement"]


@dataclass
class BlockStatement:
    body: list["Statement"]


@dataclass
class ReturnStatement:
    expr: Expression


@dataclass
class ExpressionStatement:
    expr: Expression


@dataclass
class Statement:
    kind: StatementKind
    stmt: LetStatement | PrintStatement | FnStatement | IfStatement | BlockStatement | ExpressionStatement | ReturnStatement


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

    def consume(self, kind: TokenKind = None) -> Token:
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
        token = self.consume()
        prefix_parselet = self.prefix_parselets.get(token.kind, None)
        assert prefix_parselet is not None, f"unable to parse token: {token}"
        left = prefix_parselet.parse(self, token)
        while desired_precedence < self.next_token_precedence():
            token = self.consume()
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

    def parse_fn_statement(self) -> Statement:
        name = self.consume(TokenKind.IDENTIFIER)
        self.consume(TokenKind.LPAREN)
        arguments = []
        while not self.match([TokenKind.RPAREN]):
            arguments.append(self.parse_expression(0))
        self.consume(TokenKind.LBRACE)
        body = []
        while not self.match([TokenKind.RBRACE]):
            body.append(self.parse_statement())
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


@dataclass
class Interpreter:
    locals: dict[str, t.Any]
    functions: dict[str, FnStatement]

    def exec_stmt(self, v: Statement) -> t.Any:
        if v.kind == StatementKind.PRINT:
            assert isinstance(v.stmt, PrintStatement)
            expr = self._eval(v.stmt.expr)
            print(expr)
            return None
        if v.kind == StatementKind.IF:
            assert isinstance(v.stmt, IfStatement)
            if self._eval(v.stmt.condition):
                return self.exec_stmt(v.stmt.then_branch)
            return None
        if v.kind == StatementKind.FN:
            assert isinstance(v.stmt, FnStatement)
            self.functions[v.stmt.name] = v.stmt
            return None
        if v.kind == StatementKind.RETURN:
            assert isinstance(v.stmt, ReturnStatement)
            return self._eval(v.stmt.expr)
        if v.kind == StatementKind.EXPRESSION:
            assert isinstance(v.stmt, ExpressionStatement)
            self._eval(v.stmt.expr)
            return None
        assert False, v

    def exec(self, ast) -> t.Any:
        assert isinstance(ast, list)
        for stmt in ast:
            retval = self.exec_stmt(stmt)
            if retval is not None:
                return retval
        return None

    def _eval(self, expr: Expression) -> t.Any:
        if expr.kind == ExpressionKind.LITERAL:
            assert isinstance(expr.value, LiteralExpression)
            return expr.value.expr
        if expr.kind == ExpressionKind.VARIABLE:
            assert isinstance(expr.value, VariableExpression)
            return self.locals[expr.value.name]
        if expr.kind == ExpressionKind.BINARY:
            assert isinstance(expr.value, BinaryExpression)
            if expr.value.kind == BinaryExpressionKind.ADD:
                return self._eval(expr.value.lhs) + self._eval(expr.value.rhs)
            if expr.value.kind == BinaryExpressionKind.SUB:
                return self._eval(expr.value.lhs) - self._eval(expr.value.rhs)
            if expr.value.kind == BinaryExpressionKind.MUL:
                return self._eval(expr.value.lhs) * self._eval(expr.value.rhs)
            if expr.value.kind == BinaryExpressionKind.DIV:
                return self._eval(expr.value.lhs) / self._eval(expr.value.rhs)
            if expr.value.kind == BinaryExpressionKind.LT:
                return self._eval(expr.value.lhs) < self._eval(expr.value.rhs)
        if expr.kind == ExpressionKind.CALL:
            assert isinstance(expr.value, CallExpression)
            f = self.functions[expr.value.callee.value.name]
            old_locals = self.locals
            self.locals = {
                k: self._eval(v)
                for k, v in zip([x.value.name for x in f.arguments], expr.value.args)
            }
            retval = self.exec(f.body)
            self.locals = old_locals
            return retval
        assert False, expr


def main() -> None:
    tokenizer = Tokenizer(source)
    tokens = tokenizer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter({}, {})
    interpreter.exec(ast)


if __name__ == "__main__":
    main()
