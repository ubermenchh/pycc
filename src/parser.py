from .tokentype import TokenType
import subprocess, os

class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, function):
        self.function = function 

class Function(ASTNode):
    def __init__(self, return_type, name, parameters, body):
        self.return_type = return_type 
        self.name = name 
        self.parameters = parameters 
        self.body = body 

class ReturnStatement(ASTNode):
    def __init__(self, expression):
        self.expression = expression 

class Number(ASTNode):
    def __init__(self, value):
        self.value = value

class UnaryOps(ASTNode):
    def __init__(self, op, right):
        self.op = op
        self.right = right

class BinaryOps(ASTNode):
    def __init__(self, op, left, right):
        self.op = op 
        self.left = left 
        self.right = right

class Declaration(ASTNode):
    def __init__(self, name, exp=None):
        self.name = name 
        self.exp = exp

class Assign(ASTNode):
    def __init__(self, name, exp):
        self.name = name 
        self.exp = exp

class Variable(ASTNode):
    def __init__(self, name):
        self.name = name

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens 
        self.current = 0

    def peek(self): return self.tokens[self.current]
    def previous(self): return self.tokens[self.current - 1]
    def is_at_end(self): return self.peek() == TokenType.EOF
    
    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def check(self, type):
        if not self.is_at_end(): 
            return self.peek().type == type 
        return False
    
    def match(self, *types):
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False 

    def consume(self, type, message):
        if self.check(type):
            return self.advance()
        raise Exception(message)

    def parse(self): return self.program()
    
    def program(self):
        return Program(self.function())

    def function(self):
        self.consume(TokenType.INT, "Expected 'int' as return type.")
        name = self.consume(TokenType.IDENTIFIER, "Expected function name.").value
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after function name.")
        parameters = self.parameter_list()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters.")
        body = self.block()
        return Function("int", name, parameters, body)

    def parameter_list(self):
        params = []
        return params

    def block(self):
        self.consume(TokenType.LEFT_BRACE, "Expected '{' before block.")
        statements = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.statement())
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after block.")
        return statements 
    
    def declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expected variable name.").value
        exp = None 
        if self.match(TokenType.ASSIGN):
            exp = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after variable declaration.")
        return Declaration(name, exp)

    def statement(self):
        if self.match(TokenType.RETURN):
            return self.return_statement()
        elif self.match(TokenType.INT):
            return self.declaration()
        else:
            return self.expression_statement()
        #raise Exception("Expected statement")

    def expression_statement(self):
        exp = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after expression.")
        return exp

    def return_statement(self):
        exp = self.expression()
        if not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            self.consume(TokenType.SEMICOLON, "Expected ';' after return statement.")
        return ReturnStatement(exp)
    
    def expression(self):
        return self.assignment()

    def assignment(self):
        exp = self.bitwise_or_expression()
        if self.match(TokenType.ASSIGN):
            name = exp.name if isinstance(exp, Variable) else None 
            if name is None:
                raise Exception("Invalid assignment target.")
            value = self.assignment()
            return Assign(name, value)

        return exp

    def bitwise_or_expression(self):
        exp = self.bitwise_xor_expression()
        while self.match(TokenType.BITWISE_OR):
            op = self.previous()
            right = self.bitwise_xor_expression()
            exp = BinaryOps(op, exp, right)
        return exp 

    def bitwise_xor_expression(self):
        exp = self.bitwise_and_expression()
        while self.match(TokenType.BITWISE_XOR):
            op = self.previous()
            right = self.bitwise_and_expression()
            exp = BinaryOps(op, exp, right)
        return exp 

    def bitwise_and_expression(self):
        exp = self.logical_or_expression()
        while self.match(TokenType.BITWISE_AND):
            op = self.previous()
            right = self.logical_or_expression()
            exp = BinaryOps(op, exp, right)
        return exp

    def logical_or_expression(self):
        exp = self.logical_and_expression()
        while self.match(TokenType.OR):
            op = self.previous()
            right = self.logical_and_expression()
            exp = BinaryOps(op, exp, right)
        return exp

    def logical_and_expression(self):
        eq_exp = self.equality_expression()
        while self.match(TokenType.AND):
            op = self.previous()
            next_eq_exp = self.equality_expression()
            eq_exp = BinaryOps(op, eq_exp, next_eq_exp)
        return eq_exp

    def equality_expression(self):
        rel_exp = self.relational_expression()
        while self.match(TokenType.NOT_EQUAL, TokenType.EQUAL):
            op = self.previous()
            next_rel_exp = self.relational_expression()
            rel_exp = BinaryOps(op, rel_exp, next_rel_exp)
        return rel_exp

    def relational_expression(self):
        add_exp = self.shift_expression()
        while self.match(TokenType.LESS_THAN, 
                         TokenType.GREATER_THAN,
                         TokenType.LESS_THAN_OR_EQUAL,
                         TokenType.GREATER_THAN_OR_EQUAL):
            op = self.previous()
            next_add_exp = self.shift_expression()
            add_exp = BinaryOps(op, add_exp, next_add_exp)
        return add_exp

    def shift_expression(self):
        exp = self.additve_expression()
        while self.match(TokenType.BITWISE_SHIFT_LEFT, TokenType.BITWISE_SHIFT_RIGHT):
            op = self.previous()
            right = self.additve_expression()
            exp = BinaryOps(op, exp, right)
        return exp
    
    def additve_expression(self):
        term = self.term()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.previous()
            next_term = self.term()
            term = BinaryOps(op, term, next_term)
        return term

    def term(self):
        factor = self.factor()
        while self.match(TokenType.STAR, TokenType.SLASH):
            op = self.previous()
            next_factor = self.factor()
            factor = BinaryOps(op, factor, next_factor)
        return factor
    
    def factor(self):
        if self.match(TokenType.LEFT_PAREN):
            exp = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after expression.")
            return exp 
        elif self.match(TokenType.LOGICAL_NEGATION, TokenType.BITWISE_COMPLEMENT, TokenType.MINUS):
            op = self.previous()
            factor = self.factor()
            return UnaryOps(op, factor)
        elif self.match(TokenType.NUMBER):
            return Number(self.previous())
        elif self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())
        else:
            return print("Failed!")

    def unary(self):
        if self.match(TokenType.MINUS, TokenType.LOGICAL_NEGATION, TokenType.BITWISE_COMPLEMENT):
            op = self.previous()
            right = self.unary()
            return UnaryOps(op, right)
        return self.primary()

    def primary(self):
        if self.match(TokenType.NUMBER):
            return Number(self.previous().value)
        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous().value)
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after expression.")
            return expr
        raise Exception("Expected expression.")

class ASTPrinter:
    def __init__(self):
        self.indent_level = 0

    def print(self, node):
        method_name = f"print_{type(node).__name__}"
        printer = getattr(self, method_name, self.generic_print)
        return printer(node)

    def indented(self, string):
        return "  " * self.indent_level + string

    def generic_print(self, node):
        return self.indented(f"{type(node).__name__}")

    def print_Program(self, node):
        result = self.indented("Program\n")
        self.indent_level += 1
        result += self.print(node.function)
        self.indent_level -= 1
        return result 

    def print_Function(self, node):
        result = self.indented(f"Function: {node.return_type} {node.name}\n")
        self.indent_level += 1
        if node.parameters:
            result += self.indented("Parameters:\n")
            self.indent_level += 1
            for param in node.parameters:
                result += self.indented(f"{param}\n")
            self.indent_level -= 1
        result += self.indented("Body:\n")
        self.indent_level += 1
        for statement in node.body:
            result += self.print(statement) + "\n"
        self.indent_level -= 1
        return result 

    def print_ReturnStatement(self, node):
        result = self.indented("Return:\n")
        self.indent_level += 1
        result += self.print(node.expression)
        self.indent_level -= 1
        return result 

    def print_Number(self, node):
        return self.indented(f"Number: {node.value.value}")

    def print_UnaryOps(self, node):
        result = self.indented(f"UnaryOps: {node.op.type.name}") + "\n"
        result += self.print(node.right)
        return result

    def print_BinaryOps(self, node):
        result = self.indented(f"BinaryOps: {node.op.type.name}") + "\n"
        result += self.print(node.left) + "\n"
        result += self.print(node.right)
        return result

    def print_Declaration(self, node):
        result = self.indented(f"Declaration: {node.name}\n")
        if node.exp:
            self.indent_level += 1
            result += self.indented("Initializer: \n")
            self.indent_level += 1
            result += self.print(node.exp)
            self.indent_level -= 2
        return result

    def print_Variable(self, node):
        return self.indented(f"Variable: {node.name.value}")

    def print_Assign(self, node):
        result = self.indented(f"Assign: {node.name}\n")
        self.indent_level += 1
        result += self.indent_level("Value:\n")
        self.indent_level += 1
        result += self.print(node.value)
        self.indent_level -= 2
        return result

class ASMGenerator:
    def __init__(self):
        self.assembly = []
        self.variables = {}
        self.stack_index = 0
        self.label_count = 0

    def generate(self, node):
        method_name = f"generate_{type(node).__name__}"
        generator = getattr(self, method_name, self.generic_gen)
        return generator(node)

    def generic_gen(self, node):
        raise NotImplementedError(f"Generation not implemented for {type(node).__name__}")

    def generate_Program(self, node):
        self.assembly.extend([
            "section .text",
            "global main",
            "extern printf"
        ])
        self.generate(node.function)
        return "\n".join(self.assembly)

    def generate_Function(self, node):
        self.assembly.extend([
            f"{node.name}:",
            "    push rbp",
            "    mov rbp, rsp"
        ])

        # Reserve space for local variables
        for statement in node.body:
            if isinstance(statement, Declaration):
                self.stack_index += 8
                self.variables[statement.name] = self.stack_index

        # Align stack
        if self.stack_index % 16 != 0:
            self.stack_index += 16 - (self.stack_index % 16)

        if self.stack_index > 0:
            self.assembly.append(f"    sub rsp, {self.stack_index}")

        # Generate assembly for function body
        for statement in node.body:
            self.generate(statement)

        # Function epilogue
        self.assembly.extend([
            "    mov rsp, rbp",
            "    pop rbp",
            "    ret"
        ])

    def generate_ReturnStatement(self, node):
        self.generate(node.expression)
        self.assembly.append("    pop rax")

    def generate_Number(self, node):
        self.assembly.append(f"    push {node.value.value}")

    def generate_UnaryOps(self, node):
        self.generate(node.right)
        self.assembly.append("    pop rax")

        op_map = {
            TokenType.MINUS: "    neg rax",
            TokenType.LOGICAL_NEGATION: [
                "    cmp rax, 0",
                "    sete al",
                "    movzx rax, al"
            ],
            TokenType.BITWISE_COMPLEMENT: "    not rax"
        }

        op_asm = op_map.get(node.op.type)
        if op_asm:
            if isinstance(op_asm, list):
                self.assembly.extend(op_asm)
            else:
                self.assembly.append(op_asm)
        else:
            raise NotImplementedError(f"Unary operation {node.op.type} not implemented.")

        self.assembly.append("    push rax")

    def generate_BinaryOps(self, node):
        self.generate(node.right)
        self.generate(node.left)
        self.assembly.extend([
            "    pop rbx",  # left operand
            "    pop rax"   # right operand
        ])

        op_map = {
            TokenType.PLUS: "    add rax, rbx",
            TokenType.MINUS: "    sub rax, rbx",
            TokenType.STAR: "    imul rbx",
            TokenType.SLASH: [
                "    xor rdx, rdx",
                "    idiv rbx",
            ],
            TokenType.PERCENT:  [
                "    xor rdx, rdx",
                "    idiv rbx",
                "    mov rax, rdx"
            ],
            TokenType.BITWISE_OR: "    or rax, rbx",
            TokenType.BITWISE_AND: "    and rax, rbx",
            TokenType.BITWISE_XOR: "    xor rax, rbx",
            TokenType.BITWISE_SHIFT_LEFT: [
                "    mov rcx, rbx",
                "    shl rax, cl"
            ],
            TokenType.BITWISE_SHIFT_RIGHT:  [
                "    mov rcx, rbx",
                "    shr rax, cl"
            ]
        }

        compare_ops = {
            TokenType.EQUAL: "sete",
            TokenType.NOT_EQUAL: "setne",
            TokenType.LESS_THAN: "setl",
            TokenType.LESS_THAN_OR_EQUAL: "setle",
            TokenType.GREATER_THAN: "setg",
            TokenType.GREATER_THAN_OR_EQUAL: "setge"
        }

        if node.op.type in compare_ops:
            self.assembly.extend([
                "    cmp rax, rbx",
                f"    {compare_ops[node.op.type]} al",
                "    movzx rax, al"
            ])
        else:
            op_asm = op_map.get(node.op.type)
            if op_asm:
                if isinstance(op_asm, list):
                    self.assembly.extend(op_asm)
                else:
                    self.assembly.append(op_asm)
            else:
                raise NotImplementedError(f"Binary operation {node.op.type} not implemented.")

        self.assembly.append("    push rax")

    def generate_Declaration(self, node):
        if node.exp:
            self.generate(node.exp)
            self.assembly.extend([
                "    pop rax",
                f"    mov [rbp - {self.variables[node.name]}], rax"
            ])
        else:
            self.assembly.append(f"    mov qword [rbp - {self.variables[node.name]}], 0")

    def generate_Assign(self, node):
        if node.name not in self.variables:
            raise Exception(f"Undefined variable: {node.name}")

        self.generate(node.value)
        self.assembly.extend([
            "    pop rax",
            f"    mov [rbp - {self.variables[node.name]}], rax"
        ])

    def generate_Variable(self, node):
        if node.name.value not in self.variables:
            raise Exception(f"Undefined variable: {node.name.value}")

        self.assembly.extend([
            f"    mov rax, [rbp - {self.variables[node.name.value]}]",
            "    push rax"
        ])

    def emit(self, output_file="output.s", output_exe="out.exe"):
        output_dir = "./bin"
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(output_dir, output_file)
        output_exe = os.path.join(output_dir, output_exe)

        with open(output_file, "w") as f:
            f.write("default rel\n")  # Important for position-independent code
            f.write("\n".join(self.assembly) + "\n")

        print(f"Assembly written to {output_file}.")

        try:
            subprocess.run(["nasm", "-f", "elf64", output_file], check=True)

            object_file = output_file.rsplit(".", 1)[0] + ".o"
            subprocess.run(["gcc", "-no-pie", object_file, "-o", output_exe], check=True)
            
            print(f"Executable created: {output_exe}.")
        except subprocess.CalledProcessError as e:
            print(f"Error during compilation or linking: {e}")
        except FileNotFoundError:
            print("Error: nasm or gcc not found. Make sure they are installed and in your PATH.")