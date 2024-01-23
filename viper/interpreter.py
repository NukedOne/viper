import typing as t

from viper._parser import FnStatement, StructStatement


class Interpreter:
    def __init__(self, depth: int = 0) -> None:
        self.globals: dict[str, t.Any] = {}
        self.locals: dict[str, t.Any] = {}
        self.functions: dict[str, FnStatement] = {}
        self.structs: dict[str, StructStatement] = {}
        self.depth = depth

    def _exec(self, ast) -> t.Any:
        assert isinstance(ast, list)
        for stmt in ast:
            retval = stmt.exec(self)
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
