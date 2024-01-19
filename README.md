# viper

This project is my third attempt at making a dynamic programming language implementation. It is a tree-walk interpreter with a Pratt parser.

The language features

- basic data types
  - numbers (floats and ints)
  - booleans
  - strings
  - structures
- operators for the said types
  - `==`, `!=`, `<`, `>`, `<=`, `>=`
  - `+`, `-`, `*`, `/`, `%`
  - `+=`, `-=`, `*=`, `/=`, `%=` (compound assignment)
  - `&`, `|`, `^`, `~`, `<<`, `>>` (bitwise and/or/xor/not/shift (left|right))
  - `&=`, `|=`, `^=`, `<<=`, `>>=` (bitwise compound assignment)
  - `&&`, `||`, `!` (logical and/or/not)
  - `++` (string concatenation)
  - `.` (member access)
  - `,` (comma)
- control flow
  - `if`, `else`
  - `while`
  - `for` (C-style)
- functions
  - `return` is mandatory
  - recursion!
- `print` statement
- methods
- global scope

The system includes:

  - a tokenizer
  - a Pratt parser
  - an interpterer

## Let's talk numbers

As you imagine, it's ridiculously slow, first and foremost because walking the tree and directly executing the code is inherently a slow technique compared to bytecode interpreters. Second, it's written in Python.

### Fibonacci:

```rust
fn fib(n) { 
  if (n < 2) return n;
  return fib(n-1) + fib(n-2);
}

print fib(40);
```

## Numbers

```
(env) alex@smartalex-pc:~/Repositories/viper$ time python3 spam.py
102334155.0

real	33m32,239s
user	33m30,591s
sys	0m0,128s
```

Yes, PyPy helps, but only so much.

```
(env-pypy) alex@smartalex-pc:~/Repositories/viper$ time pypy spam.py
102334155.0

real	2m58,150s
user	2m48,651s
sys	0m8,946s
```

## FAQ

Q: Why?

A: I wanted to know how slow tree-walk interpreters are compared to their bytecode cousins, and also how slow CPython is compared to its cousin PyPy.

Q: Is this...?

A: Yes, this is where the development stops.

## See also

- [venom](https://github.com/NukedOne/venom) - My first attempt, written in C
- [synapse](https://github.com/NukedOne/synapse) - My second attempt, written in Rust

## Licensing

Licensed under the [MIT License](https://opensource.org/licenses/MIT). For details, see [LICENSE](https://github.com/NukedOne/viper/blob/master/LICENSE).
