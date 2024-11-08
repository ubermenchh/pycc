from src.lexer import *
from src.parser import *
from src.codegen import ASMGenerator

import sys
import argparse

def process(file_path, args):
    try: 
        with open(file_path, "r") as f:
            text = f.read()

        if args.all:
            args.lex = args.parse = args.codegen = True
    
        tokens = tokenize(text)
        if args.lex:
            print()
            print("---------- TOKENS ----------")
            for token in tokens:
                print(token)

        parser = Parser(tokens)
        ast = parser.parse()

        printer = ASTPrinter()
        if args.parse:
            print()
            print("---------- Abstract Syntax Tree ----------")
            print(printer.print(ast))
            print()

        generator = ASMGenerator()
        asm_code = generator.generate(ast)

        if args.codegen:
            print()
            print("---------- Assembly Generated ----------")
            print(asm_code)
            print()

        if not (args.lex or args.parse or args.codegen):
            generator.emit()

    except FileNotFoundError:
        print(f"[ERROR]: File `{file_path}` not found")
        sys.exit(1);
    except Exception as e:
        print(f"Error during compilation: {str(e)}")
        sys.exit(1)

if __name__=="__main__":
    parser = argparse.ArgumentParser(
        description="Tiny C Compiler written in Python",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument("input_file", help="Input source file to compile")
    parser.add_argument("-l", "--lex", action="store_true", help="Print tokens from lexical analysis")
    parser.add_argument("-p", "--parse", action="store_true", help="Show parsing completion status")
    parser.add_argument("-cg", "--codegen", action="store_true", help="Print generated assembly code")
    parser.add_argument("--all", action="store_true", help="Enable all output phases")

    args = parser.parse_args()
    process(args.input_file, args)
