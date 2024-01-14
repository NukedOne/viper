import typing as t

from viper._parser import (
    FnStatement,
    LetStatement,
    IfStatement,
    WhileStatement,
    ForStatement,
    ReturnStatement,
    ExpressionStatement,
    BlockStatement,
    PrintStatement,
    StatementKind,
    Statement,
    Expression,
    LiteralExpression,
    AssignExpression,
    ExpressionKind,
    CallExpression,
    BinaryExpression,
    BinaryExpressionKind,
    VariableExpression,
)


class Interpreter:
    def __init__(
        self,
        _globals: dict[str, t.Any],
        _locals: dict[str, t.Any],
        functions: dict[str, FnStatement],
        depth: int = 0,
    ) -> None:
        self.globals = _globals
        self.locals = _locals
        self.functions = functions
        self.depth = depth

    def exec_stmt(self, stmt: Statement) -> t.Any:
        match stmt:
            case s if s.kind == StatementKind.LET:
                assert isinstance(s.stmt, LetStatement)
                self._eval(s.stmt.expr)
            case s if s.kind == StatementKind.PRINT:
                assert isinstance(s.stmt, PrintStatement)
                expr = self._eval(s.stmt.expr)
                print(expr)
            case s if s.kind == StatementKind.IF:
                assert isinstance(s.stmt, IfStatement)
                if self._eval(s.stmt.condition):
                    return self.exec_stmt(s.stmt.then_branch)
                else:
                    if s.stmt.else_branch is not None:
                        return self.exec_stmt(s.stmt.else_branch)
            case s if s.kind == StatementKind.FN:
                assert isinstance(s.stmt, FnStatement)
                self.functions[s.stmt.name] = s.stmt
            case s if s.kind == StatementKind.WHILE:
                assert isinstance(s.stmt, WhileStatement)
                while self._eval(s.stmt.condition):
                    self._exec(s.stmt.body.stmt.body)
            case s if s.kind == StatementKind.FOR:
                assert isinstance(s.stmt, ForStatement)
                self._eval(s.stmt.initializer)
                while self._eval(s.stmt.condition):
                    self._exec(s.stmt.body.stmt.body)
                    self._eval(s.stmt.advancement)
                if self.depth > 0:
                    del self.locals[s.stmt.initializer.value.lhs.value.name]
                else:
                    del self.globals[s.stmt.initializer.value.lhs.value.name]
            case s if s.kind == StatementKind.RETURN:
                assert isinstance(s.stmt, ReturnStatement)
                return self._eval(s.stmt.expr)
            case s if s.kind == StatementKind.EXPRESSION:
                assert isinstance(s.stmt, ExpressionStatement)
                self._eval(s.stmt.expr)
            case s if s.kind == StatementKind.BLOCK:
                assert isinstance(s.stmt, BlockStatement)
                self.depth += 1
                retval = self._exec(s.stmt.body)
                self.depth -= 1
                if retval is not None:
                    return retval
            case _:
                assert False, s

    def _exec(self, ast) -> t.Any:
        assert isinstance(ast, list)
        for stmt in ast:
            retval = self.exec_stmt(stmt)
            if retval is not None:
                return retval

    def is_local(self, name: str) -> bool:
        return name in self.locals

    def is_global(self, name: str) -> bool:
        return name in self.globals

    def resolve(self, name: str) -> t.Any:
        if self.is_local(name):
            return self.locals[name]
        elif self.is_global(name):
            return self.globals[name]
        raise Exception(f"{name} is not defined.")

    def _eval(self, expr: Expression) -> t.Any:
        match expr:
            case e if e.kind == ExpressionKind.LITERAL:
                assert isinstance(expr.value, LiteralExpression)
                return expr.value.expr
            case e if e.kind == ExpressionKind.VARIABLE:
                assert isinstance(expr.value, VariableExpression)
                return self.resolve(expr.value.name)
            case e if e.kind == ExpressionKind.ASSIGN:
                assert isinstance(expr.value, AssignExpression)
                if self.depth > 0:
                    self.locals[expr.value.lhs.value.name] = self._eval(expr.value.rhs)
                else:
                    self.globals[expr.value.lhs.value.name] = self._eval(expr.value.rhs)
            case e if e.kind == ExpressionKind.BINARY:
                assert isinstance(expr.value, BinaryExpression)
                match expr.value:
                    case binexp if binexp.kind == BinaryExpressionKind.ADD:
                        return self._eval(expr.value.lhs) + self._eval(expr.value.rhs)
                    case binexp if binexp.kind == BinaryExpressionKind.SUB:
                        return self._eval(expr.value.lhs) - self._eval(expr.value.rhs)
                    case binexp if binexp.kind == BinaryExpressionKind.MUL:
                        return self._eval(expr.value.lhs) * self._eval(expr.value.rhs)
                    case binexp if binexp.kind == BinaryExpressionKind.DIV:
                        return self._eval(expr.value.lhs) / self._eval(expr.value.rhs)
                    case binexp if binexp.kind == BinaryExpressionKind.LT:
                        return self._eval(expr.value.lhs) < self._eval(expr.value.rhs)
            case e if e.kind == ExpressionKind.CALL:
                assert isinstance(expr.value, CallExpression)
                assert isinstance(expr.value.callee.value, VariableExpression)
                f = self.functions[expr.value.callee.value.name]
                old_locals = self.locals
                self.locals = {
                    k: self._eval(v)
                    for k, v in zip(
                        [x.value.name for x in f.arguments],  # type: ignore
                        expr.value.args,
                    )
                }
                retval = self.exec_stmt(f.body)
                self.locals = old_locals
                return retval
            case _:
                assert False, expr
