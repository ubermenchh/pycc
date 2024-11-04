# pycc
A Tiny C Compiler written in Python

Based on [Nora Sandler's blog](https://norasandler.com/2017/11/29/Write-a-Compiler.html)
- It can handle basic C code, like functions (recursive functions need a little tweaking)

Usage:
```bash
python main.py <input_file.c>
```

- For running each stage separately use the following flags
```
options:
  -h, --help      show this help message and exit
  -l, --lex       Print tokens from lexical analysis
  -p, --parse     Show parsing completion status
  -cg, --codegen  Print generated assembly code
  --all           Enable all output phases
```

References:
- [Blog Post](https://norasandler.com/2017/11/29/Write-a-Compiler.html)
- [pylox](https://github.com/ubermenchh/pylox) - language i wrote based on the book Crafting Interpreters
