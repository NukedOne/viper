from dataclasses import dataclass
import typing as t
from viper.tokenizer import Token, TokenKind
from abc import ABC, abstractmethod


if t.TYPE_CHECKING:
    from viper.interpreter import Interpreter


class Expression(ABC):
    def eval(self, interpreter: "Interpreter") -> t.Any:
        pass


class LiteralExpression(Expression):
    def __init__(self, expr: float) -> None:
        self.expr = expr

    def __repr__(self) -> str:
        return str(self.expr)

    def eval(self, interpreter: "Interpreter") -> t.Any:
        return self.expr


class VariableExpression(Expression):
    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return self.name

    def eval(self, interpreter: "Interpreter") -> t.Any:
        return interpreter.resolve(self.name)


class BinaryExpression(Expression):
    def __init__(self, lhs: Expression, rhs: Expression, operator: str) -> None:
        self.lhs = lhs
        self.rhs = rhs
        self.operator = operator

    def __repr__(self) -> str:
        return f"({self.lhs} {self.operator} {self.rhs})"

    def eval(self, interpreter: "Interpreter") -> t.Any:
        match self.operator:
            case v if v == "+":
                return self.lhs.eval(interpreter) + self.rhs.eval(interpreter)
            case v if v == "-":
                return self.lhs.eval(interpreter) - self.rhs.eval(interpreter)
            case v if v == "*":
                return self.lhs.eval(interpreter) * self.rhs.eval(interpreter)
            case v if v == "/":
                return self.lhs.eval(interpreter) / self.rhs.eval(interpreter)
            case v if v == "%":
                return self.lhs.eval(interpreter) % self.rhs.eval(interpreter)
            case v if v == "&":
                return self.lhs.eval(interpreter) & self.rhs.eval(interpreter)
            case v if v == "|":
                return self.lhs.eval(interpreter) | self.rhs.eval(interpreter)
            case v if v == "^":
                return self.lhs.eval(interpreter) ^ self.rhs.eval(interpreter)
            case v if v == "<":
                return self.lhs.eval(interpreter) < self.rhs.eval(interpreter)
            case v if v == ">":
                return self.lhs.eval(interpreter) > self.rhs.eval(interpreter)
            case v if v == "<=":
                return self.lhs.eval(interpreter) <= self.rhs.eval(interpreter)
            case v if v == ">=":
                return self.lhs.eval(interpreter) >= self.rhs.eval(interpreter)
            case v if v == "&&":
                return self.lhs.eval(interpreter) and self.rhs.eval(interpreter)
            case v if v == "||":
                return self.lhs.eval(interpreter) or self.rhs.eval(interpreter)
            case v if v == "==":
                return self.lhs.eval(interpreter) == self.rhs.eval(interpreter)
            case v if v == "!=":
                return self.lhs.eval(interpreter) != self.rhs.eval(interpreter)


class AssignExpression(Expression):
    def __init__(self, lhs: Expression, rhs: Expression, operator: str) -> None:
        self.lhs = lhs
        self.rhs = rhs
        self.operator = operator

    def __repr__(self) -> str:
        return f"({self.lhs} {self.operator} {self.rhs})"

    def eval(self, interpreter: "Interpreter") -> t.Any:
        assert isinstance(self.lhs, VariableExpression)
        match self.operator:
            case o if o == "=":
                if interpreter.depth > 0:
                    interpreter.locals[self.lhs.name] = self.rhs.eval(interpreter)
                else:
                    interpreter.globals[self.lhs.name] = self.rhs.eval(interpreter)
            case o if o == "+=":
                if interpreter.depth > 0:
                    interpreter.locals[self.lhs.name] += self.rhs.eval(interpreter)
                else:
                    interpreter.globals[self.lhs.name] += self.rhs.eval(interpreter)
            case o if o == "-=":
                if interpreter.depth > 0:
                    interpreter.locals[self.lhs.name] -= self.rhs.eval(interpreter)
                else:
                    interpreter.globals[self.lhs.name] -= self.rhs.eval(interpreter)
            case o if o == "*=":
                if interpreter.depth > 0:
                    interpreter.locals[self.lhs.name] *= self.rhs.eval(interpreter)
                else:
                    interpreter.globals[self.lhs.name] *= self.rhs.eval(interpreter)
            case o if o == "/=":
                if interpreter.depth > 0:
                    interpreter.locals[self.lhs.name] /= self.rhs.eval(interpreter)
                else:
                    interpreter.globals[self.lhs.name] /= self.rhs.eval(interpreter)
            case o if o == "%=":
                if interpreter.depth > 0:
                    interpreter.locals[self.lhs.name] %= self.rhs.eval(interpreter)
                else:
                    interpreter.globals[self.lhs.name] %= self.rhs.eval(interpreter)
            case o if o == ">>=":
                if interpreter.depth > 0:
                    interpreter.locals[self.lhs.name] >>= self.rhs.eval(interpreter)
                else:
                    interpreter.globals[self.lhs.name] >>= self.rhs.eval(interpreter)
            case o if o == "<<=":
                if interpreter.depth > 0:
                    interpreter.locals[self.lhs.name] <<= self.rhs.eval(interpreter)
                else:
                    interpreter.globals[self.lhs.name] <<= self.rhs.eval(interpreter)
            case o if o == "|=":
                if interpreter.depth > 0:
                    interpreter.locals[self.lhs.name] |= self.rhs.eval(interpreter)
                else:
                    interpreter.globals[self.lhs.name] |= self.rhs.eval(interpreter)
            case o if o == "&=":
                if interpreter.depth > 0:
                    interpreter.locals[self.lhs.name] &= self.rhs.eval(interpreter)
                else:
                    interpreter.globals[self.lhs.name] &= self.rhs.eval(interpreter)
            case o if o == "^=":
                if interpreter.depth > 0:
                    interpreter.locals[self.lhs.name] ^= self.rhs.eval(interpreter)
                else:
                    interpreter.globals[self.lhs.name] ^= self.rhs.eval(interpreter)


class CallExpression(Expression):
    def __init__(self, callee: Expression, args: list[Expression]) -> None:
        self.callee = callee
        self.args = args

    def __repr__(self) -> str:
        return f"{self.callee}({self.args})"

    def eval(self, interpreter: "Interpreter") -> t.Any:
        assert isinstance(self.callee, VariableExpression)
        f = interpreter.functions[self.callee.name]
        old_locals = interpreter.locals
        interpreter.locals = {
            k: v.eval(interpreter)
            for k, v in zip(
                [arg.name for arg in f.arguments],  # type: ignore
                self.args,
            )
        }
        retval = f.body.exec(interpreter)
        interpreter.locals = old_locals
        return retval


class UnaryExpression(Expression):
    def __init__(self, expr: Expression, operator: str) -> None:
        self.expr = expr
        self.operator = operator

    def __repr__(self) -> str:
        return f"({self.operator}({self.expr}))"

    def eval(self, interpreter: "Interpreter") -> t.Any:
        match self.operator:
            case "!":
                return not self.expr.eval(interpreter)
            case "-":
                return -self.expr.eval(interpreter)
            case _:
                raise NotImplementedError()


@dataclass
class PrefixExpression:
    token: Token
    operand: Expression


class PrefixParselet(ABC):
    @abstractmethod
    def parse(self, parser: "Parser", token: Token) -> Expression:
        pass


class LiteralParselet(PrefixParselet):
    def parse(self, parser: "Parser", token: Token) -> Expression:
        match token:
            case t if t.value in {"true", "false"}:
                return LiteralExpression(True if v == "true" else False)
            case t if t.kind == TokenKind.NUMBER:
                return LiteralExpression(float(token.value))
            case _:
                raise NotImplementedError(f"Couldn't parse: {token.value}")


class NameParselet(PrefixParselet):
    def parse(self, parser: "Parser", token: Token) -> Expression:
        return VariableExpression(token.value)


class UnaryParselet(PrefixParselet):
    def parse(self, parser: "Parser", token: Token) -> Expression:
        expr = parser.parse_expression(0)
        return UnaryExpression(expr, token.value)


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
        return CallExpression(left, args)


class BinaryOperatorParselet(InfixParselet):
    def parse(self, parser: "Parser", left: Expression, token: Token) -> Expression:
        right = parser.parse_expression(parser.precedence[token.kind])
        match token.value:
            case (
                "+"
                | "-"
                | "*"
                | "/"
                | "%"
                | "&"
                | "|"
                | "^"
                | "<"
                | ">"
                | ">="
                | "<="
                | "=="
                | "!="
                | "||"
                | "&&"
            ):
                return BinaryExpression(left, right, token.value)
            case (
                "="
                | "+="
                | "-="
                | "*="
                | "/="
                | "%="
                | "&="
                | "|="
                | "^="
                | ">>="
                | "<<="
            ):
                return AssignExpression(left, right, token.value)
            case _:
                raise Exception("Unknown operator.")


class Statement(ABC):
    @abstractmethod
    def exec(self, interpreter: "Interpreter") -> t.Any:
        pass


class LetStatement(Statement):
    def __init__(self, expr: Expression) -> None:
        self.initializer = expr

    def exec(self, interpreter: "Interpreter") -> t.Any:
        self.initializer.eval(interpreter)


class PrintStatement(Statement):
    def __init__(self, expr: Expression) -> None:
        self.expr = expr

    def exec(self, interpreter: "Interpreter") -> t.Any:
        expr = self.expr.eval(interpreter)
        print(expr)


class IfStatement(Statement):
    def __init__(
        self,
        condition: Expression,
        then_branch: Statement,
        else_branch: t.Optional[Statement],
    ) -> None:
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def exec(self, interpreter: "Interpreter") -> t.Any:
        if self.condition.eval(interpreter):
            return self.then_branch.exec(interpreter)
        else:
            if self.else_branch is not None:
                return self.else_branch.exec(interpreter)


class FnStatement(Statement):
    def __init__(self, name: str, arguments: list[Expression], body: Statement) -> None:
        self.name = name
        self.arguments = arguments
        self.body = body

    def exec(self, interpreter: "Interpreter") -> t.Any:
        interpreter.functions[self.name] = self


class BlockStatement(Statement):
    def __init__(self, body: list[Statement]) -> None:
        self.body = body

    def exec(self, interpreter: "Interpreter") -> t.Any:
        interpreter.depth += 1
        retval = interpreter._exec(self.body)
        interpreter.depth -= 1
        if retval is not None:
            return retval


class ReturnStatement(Statement):
    def __init__(self, expr: Expression) -> None:
        self.expr = expr

    def exec(self, interpreter: "Interpreter") -> t.Any:
        return self.expr.eval(interpreter)


class WhileStatement(Statement):
    def __init__(self, condition: Expression, body: Statement) -> None:
        self.condition = condition
        self.body = body

    def exec(self, interpreter: "Interpreter") -> t.Any:
        while self.condition.eval(interpreter):
            self.body.exec(interpreter)


class ForStatement(Statement):
    def __init__(
        self,
        initializer: Expression,
        condition: Expression,
        advancement: Expression,
        body: Statement,
    ) -> None:
        self.initializer = initializer
        self.condition = condition
        self.advancement = advancement
        self.body = body

    def exec(self, interpreter: "Interpreter") -> t.Any:
        assert isinstance(self.initializer, AssignExpression)
        assert isinstance(self.initializer.lhs, VariableExpression)
        self.initializer.eval(interpreter)
        while self.condition.eval(interpreter):
            self.body.exec(interpreter)
            self.advancement.eval(interpreter)
        if interpreter.depth > 0:
            del interpreter.locals[self.initializer.lhs.name]
        else:
            del interpreter.globals[self.initializer.lhs.name]


class ExpressionStatement(Statement):
    def __init__(self, expr: Expression) -> None:
        self.expr = expr

    def exec(self, interpreter: "Interpreter") -> t.Any:
        self.expr.eval(interpreter)


class Parser:
    prefix_parselets: dict[TokenKind, PrefixParselet] = {}
    infix_parselets: dict[TokenKind, InfixParselet] = {}
    tokens: list[Token]
    precedence: dict[TokenKind, int] = {
        TokenKind.EQUAL: 1,
        TokenKind.PLUSEQUAL: 1,
        TokenKind.MINUSEQUAL: 1,
        TokenKind.STAREQUAL: 1,
        TokenKind.SLASHEQUAL: 1,
        TokenKind.SHLEQUAL: 1,
        TokenKind.SHREQUAL: 1,
        TokenKind.BITANDEQUAL: 1,
        TokenKind.BITOREQUAL: 1,
        TokenKind.BITXOREQUAL: 1,
        TokenKind.MODEQUAL: 1,
        TokenKind.OR: 2,
        TokenKind.AND: 3,
        TokenKind.BITOR: 4,
        TokenKind.BITXOR: 5,
        TokenKind.BITAND: 6,
        TokenKind.DOUBLE_EQUAL: 7,
        TokenKind.BANGEQUAL: 7,
        TokenKind.LT: 8,
        TokenKind.LTE: 8,
        TokenKind.GT: 8,
        TokenKind.GTE: 8,
        TokenKind.SHL: 9,
        TokenKind.SHR: 9,
        TokenKind.PLUS: 10,
        TokenKind.MINUS: 10,
        TokenKind.STAR: 11,
        TokenKind.SLASH: 11,
        TokenKind.MOD: 11,
        TokenKind.BANG: 12,
        TokenKind.LPAREN: 13,
        TokenKind.NUMBER: 14,
    }

    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.register(TokenKind.PLUS, BinaryOperatorParselet())
        self.register(TokenKind.MINUS, BinaryOperatorParselet())
        self.register(TokenKind.STAR, BinaryOperatorParselet())
        self.register(TokenKind.SLASH, BinaryOperatorParselet())
        self.register(TokenKind.EQUAL, BinaryOperatorParselet())
        self.register(TokenKind.DOUBLE_EQUAL, BinaryOperatorParselet())
        self.register(TokenKind.BANGEQUAL, BinaryOperatorParselet())
        self.register(TokenKind.PLUSEQUAL, BinaryOperatorParselet())
        self.register(TokenKind.MINUSEQUAL, BinaryOperatorParselet())
        self.register(TokenKind.STAREQUAL, BinaryOperatorParselet())
        self.register(TokenKind.SLASHEQUAL, BinaryOperatorParselet())
        self.register(TokenKind.BITANDEQUAL, BinaryOperatorParselet())
        self.register(TokenKind.BITXOREQUAL, BinaryOperatorParselet())
        self.register(TokenKind.BITOREQUAL, BinaryOperatorParselet())
        self.register(TokenKind.BITOR, BinaryOperatorParselet())
        self.register(TokenKind.BITAND, BinaryOperatorParselet())
        self.register(TokenKind.BITXOR, BinaryOperatorParselet())
        self.register(TokenKind.SHL, BinaryOperatorParselet())
        self.register(TokenKind.SHR, BinaryOperatorParselet())
        self.register(TokenKind.SHLEQUAL, BinaryOperatorParselet())
        self.register(TokenKind.SHREQUAL, BinaryOperatorParselet())
        self.register(TokenKind.MODEQUAL, BinaryOperatorParselet())
        self.register(TokenKind.MOD, BinaryOperatorParselet())
        self.register(TokenKind.AND, BinaryOperatorParselet())
        self.register(TokenKind.OR, BinaryOperatorParselet())
        self.register(TokenKind.LT, BinaryOperatorParselet())
        self.register(TokenKind.LPAREN, CallParselet())
        self.register(TokenKind.NUMBER, LiteralParselet())
        self.register(TokenKind.TRUE, LiteralParselet())
        self.register(TokenKind.FALSE, LiteralParselet())
        self.register(TokenKind.IDENTIFIER, NameParselet())
        self.register(TokenKind.BANG, UnaryParselet())
        self.register(TokenKind.MINUS, UnaryParselet())

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
        return PrintStatement(expr)

    def parse_let_statement(self) -> Statement:
        expr = self.parse_expression(0)
        self.consume(TokenKind.SEMICOLON)
        return LetStatement(expr)

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
        return WhileStatement(condition, body)

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
        return ForStatement(initializer, condition, advancement, body)

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
        return FnStatement(name.value, arguments, body)

    def parse_return_statement(self) -> Statement:
        expr = self.parse_expression(0)
        self.consume(TokenKind.SEMICOLON)
        return ReturnStatement(expr)

    def parse_if_statement(self) -> Statement:
        self.consume(TokenKind.LPAREN)
        condition = self.parse_expression(0)
        self.consume(TokenKind.RPAREN)
        then_branch = self.parse_statement()
        else_branch = None
        if self.match([TokenKind.ELSE]):
            else_branch = self.parse_statement()
        return IfStatement(condition, then_branch, else_branch)

    def parse_block_statement(self) -> Statement:
        body = []
        while not self.match([TokenKind.RBRACE]):
            body.append(self.parse_statement())
        return BlockStatement(body)

    def parse_expression_statement(self) -> Statement:
        expr = self.parse_expression(0)
        self.consume(TokenKind.SEMICOLON)
        return ExpressionStatement(expr)

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
