from lexer import tokenize
from parser import *

with open("main.c", "r") as f:
    text = f.read()

print(text)

tokens = tokenize(text)
for token in tokens:
    print(token)

parser = Parser(tokens)
ast = parser.parse()

printer = ASTPrinter()
generator = ASMGenerator()

print(printer.print(ast))
asm_code = generator.generate(ast)

print("".join(asm_code))

generator.emit()
