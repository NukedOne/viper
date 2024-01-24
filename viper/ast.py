import enum
import typing as t
from viper.tokenizer import Token
from abc import ABC, abstractmethod


if t.TYPE_CHECKING:
    from viper.interpreter import Interpreter


class Expression(ABC):
    @abstractmethod
    def eval(self, interpreter: "Interpreter") -> t.Any:
        pass


class Statement(ABC):
    @abstractmethod
    def exec(self, interpreter: "Interpreter") -> t.Any:
        pass


class LiteralExpression(Expression):
    def __init__(self, expr: int | float | str) -> None:
        self.expr = expr

    def __repr__(self) -> str:
        if isinstance(self.expr, float):
            return "%.16g" % self.expr
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
            case v if v in "+":
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
            case v if v in "++":
                return str(self.lhs.eval(interpreter)) + str(self.rhs.eval(interpreter))


class AssignExpression(Expression):
    def __init__(self, lhs: Expression, rhs: Expression, operator: str) -> None:
        self.lhs = lhs
        self.rhs = rhs
        self.operator = operator

    def __repr__(self) -> str:
        return f"({self.lhs} {self.operator} {self.rhs})"

    def eval(self, interpreter: "Interpreter") -> t.Any:
        if isinstance(self.lhs, VariableExpression):
            storage = (
                interpreter.locals if interpreter.depth > 0 else interpreter.globals
            )

            match self.operator:
                case o if o == "=":
                    storage[self.lhs.name] = self.rhs.eval(interpreter)
                case o if o == "+=":
                    storage[self.lhs.name] += self.rhs.eval(interpreter)
                case o if o == "-=":
                    storage[self.lhs.name] -= self.rhs.eval(interpreter)
                case o if o == "*=":
                    storage[self.lhs.name] *= self.rhs.eval(interpreter)
                case o if o == "/=":
                    storage[self.lhs.name] /= self.rhs.eval(interpreter)
                case o if o == "%=":
                    storage[self.lhs.name] %= self.rhs.eval(interpreter)
                case o if o == ">>=":
                    storage[self.lhs.name] >>= self.rhs.eval(interpreter)
                case o if o == "<<=":
                    storage[self.lhs.name] <<= self.rhs.eval(interpreter)
                case o if o == "|=":
                    storage[self.lhs.name] |= self.rhs.eval(interpreter)
                case o if o == "&=":
                    storage[self.lhs.name] &= self.rhs.eval(interpreter)
                case o if o == "^=":
                    storage[self.lhs.name] ^= self.rhs.eval(interpreter)

        elif isinstance(self.lhs, IndexExpression):
            array = self.lhs.indexee.eval(interpreter)
            index = self.lhs.index.eval(interpreter)

            match self.operator:
                case o if o == "=":
                    array[index] = self.rhs.eval(interpreter)
                case o if o == "+=":
                    array[index] += self.rhs.eval(interpreter)
                case o if o == "-=":
                    array[index] -= self.rhs.eval(interpreter)
                case o if o == "*=":
                    array[index] *= self.rhs.eval(interpreter)
                case o if o == "/=":
                    array[index] /= self.rhs.eval(interpreter)
                case o if o == "%=":
                    array[index] %= self.rhs.eval(interpreter)
                case o if o == ">>=":
                    array[index] >>= self.rhs.eval(interpreter)
                case o if o == "<<=":
                    array[index] <<= self.rhs.eval(interpreter)
                case o if o == "|=":
                    array[index] |= self.rhs.eval(interpreter)
                case o if o == "&=":
                    array[index] &= self.rhs.eval(interpreter)
                case o if o == "^=":
                    array[index] ^= self.rhs.eval(interpreter)

        elif isinstance(self.lhs, GetExpression):
            target = self.lhs.gotten.eval(interpreter)
            member = self.lhs.member

            match self.operator:
                case o if o == "=":
                    target.fields[member] = self.rhs.eval(interpreter)
                case o if o == "+=":
                    target.fields[member] += self.rhs.eval(interpreter)
                case o if o == "-=":
                    target.fields[member] -= self.rhs.eval(interpreter)
                case o if o == "*=":
                    target.fields[member] *= self.rhs.eval(interpreter)
                case o if o == "/=":
                    target.fields[member] /= self.rhs.eval(interpreter)
                case o if o == "%=":
                    target.fields[member] %= self.rhs.eval(interpreter)
                case o if o == ">>=":
                    target.fields[member] >>= self.rhs.eval(interpreter)
                case o if o == "<<=":
                    target.fields[member] <<= self.rhs.eval(interpreter)
                case o if o == "|=":
                    target.fields[member] |= self.rhs.eval(interpreter)
                case o if o == "&=":
                    target.fields[member] &= self.rhs.eval(interpreter)
                case o if o == "^=":
                    target.fields[member] ^= self.rhs.eval(interpreter)


class GetExpression(Expression):
    def __init__(self, gotten: Expression, member: str) -> None:
        self.gotten = gotten
        self.member = member

    def __repr__(self) -> str:
        return f"({self.gotten}.{self.member})"

    def eval(self, interpreter: "Interpreter") -> t.Any:
        return self.gotten.eval(interpreter).fields[self.member]


class IndexExpression(Expression):
    def __init__(self, indexee: Expression, index: Expression) -> None:
        self.indexee = indexee
        self.index = index

    def __repr__(self) -> str:
        return f"({self.indexee}[{self.index}])"

    def eval(self, interpreter: "Interpreter") -> t.Any:
        return self.indexee.eval(interpreter)[self.index.eval(interpreter)]


class CallExpression(Expression):
    def __init__(self, callee: Expression, args: list[Expression]) -> None:
        self.callee = callee
        self.args = args

    def __repr__(self) -> str:
        return f"{self.callee}({self.args})"

    def eval(self, interpreter: "Interpreter") -> t.Any:
        if isinstance(self.callee, VariableExpression):
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
        elif isinstance(self.callee, GetExpression):
            assert isinstance(self.callee, GetExpression)
            method = self.callee.eval(interpreter)
            old_locals = interpreter.locals
            new_locals = {"self": self.callee.gotten.eval(interpreter)}
            new_locals.update(
                {
                    k: v.eval(interpreter)
                    for k, v in zip(
                        [arg.name for arg in method.arguments if arg.name != "self"],  # type: ignore
                        self.args,
                    )
                }
            )
            interpreter.locals = new_locals
            retval = method.body.exec(interpreter)
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


class StructLiteralExpression(Expression):
    def __init__(
        self, name: Token, fields: dict[str, Expression | Statement | None]
    ) -> None:
        self.name = name.value
        self.fields = fields

    def __repr__(self) -> str:
        return f"{self.name} {{ {self.fields} }}"

    def eval(self, interpreter: "Interpreter") -> t.Any:
        methods = {
            k: v
            for k, v in interpreter.structs[self.name].fields.items()
            if isinstance(v, FnStatement)
        }
        for method_name, method in methods.items():
            assert isinstance(method, FnStatement)
            self.fields[method_name] = method
        return self


class ArrayLiteralExpression(Expression):
    def __init__(self, initializers: list["Expression"]) -> None:
        self.initializers = initializers

    def __repr__(self) -> str:
        return f"[{self.initializers}]"

    def eval(self, interpreter: "Interpreter") -> t.Any:
        return self.initializers


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
        if isinstance(expr, float):
            print("%.16g" % expr)
        else:
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
            retval = self.body.exec(interpreter)
            match retval:
                case ControlFlow.CONTINUE:
                    continue
                case ControlFlow.BREAK:
                    break


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
            retval = self.body.exec(interpreter)
            match retval:
                case ControlFlow.CONTINUE:
                    continue
                case ControlFlow.BREAK:
                    break

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


class StructStatement(Statement):
    def __init__(
        self, name: Token, fields: dict[str, Expression | Statement | None]
    ) -> None:
        self.name = name
        self.fields = fields

    def __repr__(self) -> str:
        return f"Struct(name={self.name.value}, fields={self.fields})"

    def exec(self, interpreter: "Interpreter") -> t.Any:
        interpreter.structs[self.name.value] = self


class ImplStatement(Statement):
    def __init__(self, name: Token, methods: list[Statement]) -> None:
        self.name = name
        self.methods = methods

    def __repr__(self) -> str:
        return f"Impl(name={self.name.value}, methods={self.methods})"

    def exec(self, interpreter: "Interpreter") -> t.Any:
        for method in self.methods:
            assert isinstance(method, FnStatement)
            interpreter.structs[self.name.value].fields[method.name] = method


class ControlFlow(enum.Enum):
    BREAK = 0
    CONTINUE = 1


class BreakStatement(Statement):
    def __init__(self):
        pass

    def __repr__(self) -> str:
        return "Break"

    def exec(self, interpreter: "Interpreter") -> t.Any:
        return ControlFlow.BREAK


class ContinueStatement(Statement):
    def __init__(self):
        pass

    def __repr__(self) -> str:
        return "Continue"

    def exec(self, interpreter: "Interpreter") -> t.Any:
        return ControlFlow.CONTINUE
