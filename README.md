# viper

This project is my third attempt at making a dynamic programming language implementation. It ended up being just enough of a tree-walk interpreter to compute fib(40). As you imagine, it's ridiculously slow, first and foremost because walking the tree and directly executing the code is inherently a slow technique compared to bytecode interpreters. Second, it's written in Python. Yes, PyPy helps, but only so much. That said, let's talk about numbers.

## Numbers

```
(env) alex@smartalex-pc:~/Repositories/viper$ time python3 spam.py
102334155.0

real	33m32,239s
user	33m30,591s
sys	0m0,128s
```

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

[venom](https://github.com/NukedOne/venom) - My first attempt, written in C
[synapse](https://github.com/NukedOne/synapse) - My second attempt, written in C

## Licensing

Licensed under the [MIT License](https://opensource.org/licenses/MIT). For details, see [LICENSE](https://github.com/NukedOne/viper/blob/master/LICENSE).
