import pytest

ASSERTIONS = {
    "for_local": [0, 1, 2, 3, 4],
    "while_local": [0, 1, 2, 3, 4],
    "global_local": [3],
    "fib": [55],
}


def test_viper(capsys):
    from viper.tokenizer import Tokenizer
    from viper._parser import Parser
    from viper.interpreter import Interpreter

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


def test_operators(capsys, tmp_path):
    import textwrap

    from viper.tokenizer import Tokenizer
    from viper._parser import Parser
    from viper.interpreter import Interpreter

    for op in ("<", ">", "<=", ">=", "==", "!="):
        source = textwrap.dedent(
            """
            fn main() {
                let x = 1;
                let y = 2;
                print x %s y;
                return 0;
            }
            main();
            """
            % op
        )

        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        interpreter = Interpreter({}, {}, {})
        interpreter._exec(ast)

        captured = capsys.readouterr()
        output = captured.out.strip().split("\n")

        expected = eval(f"1 {op} 2")

        assert str(expected) in output


def test_arithmetic_operators(capsys, tmp_path):
    import textwrap

    from viper.tokenizer import Tokenizer
    from viper._parser import Parser
    from viper.interpreter import Interpreter

    for op in ("+", "-", "*", "/", "%", "&", "|", "^"):
        source = textwrap.dedent(
            """
            fn main() {
                let x = 1;
                let y = 2;
                print x %s y;
                return 0;
            }
            main();
            """
            % op
        )

        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        interpreter = Interpreter({}, {}, {})
        interpreter._exec(ast)

        captured = capsys.readouterr()
        output = captured.out.strip().split("\n")

        expected = eval(f"1 {op} 2")

        assert ("%.16g" % expected) in output
