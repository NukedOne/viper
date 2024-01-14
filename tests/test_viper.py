import pytest

ASSERTIONS = {
    "for_local": [0.0, 1.0, 2.0, 3.0, 4.0],
    "while_local": [0.0, 1.0, 2.0, 3.0, 4.0],
    "global_local": [3.0],
    "fib": [55.0],
}


def test_viper(capsys):
    from viper import Tokenizer, Parser, Interpreter

    for filename, assertions in ASSERTIONS.items():
        with open(f"tests/cases/{filename}.vpr", "r") as f:
            source = f.read()
            tokenizer = Tokenizer(source)
            tokens = tokenizer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()
            interpreter = Interpreter({}, {}, {})
            interpreter._exec(ast)

            captured = capsys.readouterr()
            output = captured.out.strip().split("\n")

            for assertion in assertions:
                assert str(assertion) in output
