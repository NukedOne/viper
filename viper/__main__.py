import sys

from viper.tokenizer import Tokenizer
from viper._parser import Parser
from viper.interpreter import Interpreter


def main() -> None:
    source = read_file(sys.argv[1])
    tokenizer = Tokenizer(source)
    tokens = tokenizer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter({}, {}, {}, {})
    interpreter._exec(ast)


def read_file(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


if __name__ == "__main__":
    main()
