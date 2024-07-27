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
print(printer.print(ast))
