# Takes each token from the token list and constructs a AST 
# 
# <program> ::= <function>
# <function> ::= "int" <id> "(" ")" "{" <statement> "}"
# <statement> ::= "return" <exp> ";"
# <exp> ::= <int>

from os import wait
from tokentype import TokenType

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
        """ <program> ::= <function> """
        
        return Program(self.function())

    def function(self):
        """ <function> ::= "int" <id> "(" ")" "{" <statement> "}" """

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
    
    def statement(self):
        """ <statement> ::= "return" <exp> ";" """

        if self.match(TokenType.RETURN):
            return self.return_statement()
        raise Exception("Expected statement")

    def return_statement(self):
        exp = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after return statement.")
        return ReturnStatement(exp)
    
    def expression(self):
        """ <exp> ::= <logical-and-exp> { "||" <logical-and-exp> } """

        return self.bitwise_or_expression()

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
        """ <logical-and-exp> ::= <equality_exp> { "&&" <equality_exp> } """

        eq_exp = self.equality_expression()
        while self.match(TokenType.AND):
            op = self.previous()
            next_eq_exp = self.equality_expression()
            eq_exp = BinaryOps(op, eq_exp, next_eq_exp)
        return eq_exp

    def equality_expression(self):
        """ <equality_exp> ::= <relational_exp> { ("!=" | "==") <relational_exp> } """

        rel_exp = self.relational_expression()
        while self.match(TokenType.NOT_EQUAL, TokenType.EQUAL):
            op = self.previous()
            next_rel_exp = self.relational_expression()
            rel_exp = BinaryOps(op, rel_exp, next_rel_exp)
        return rel_exp

    def relational_expression(self):
        """ <relational_exp> ::= <additve_exp> { ("<" | ">" | "<=" | ">=") <additve_exp> } """

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
        """ <additve_exp> ::= <term> { ("+" | "-") <term> } """

        term = self.term()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.previous()
            next_term = self.term()
            term = BinaryOps(op, term, next_term)
        return term

    def term(self):
        """ <term> ::= <factor> { ("*" | "/") <factor> } """

        factor = self.factor()
        while self.match(TokenType.STAR, TokenType.SLASH):
            op = self.previous()
            next_factor = self.factor()
            factor = BinaryOps(op, factor, next_factor)
        return factor
    
    def factor(self):
        """ <factor> ::= "(" <exp> ")" | <unary_op> <factor> | <int> """

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
        else:
            return print("Failed!")

    def unary(self):
        """ <unary_op> ::= "!" | "~" | "-" """

        if self.match(TokenType.MINUS, TokenType.LOGICAL_NEGATION, TokenType.BITWISE_COMPLEMENT):
            op = self.previous()
            right = self.unary()
            return UnaryOps(op, right)
        return self.primary()

    def primary(self):
        if self.match(TokenType.NUMBER):
            return Number(self.previous().value)
        self.consume(TokenType.LEFT_PAREN, "Expected '(' before expression.")
        expr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after expression.")
        return expr

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

class ASMGenerator:
    def __init__(self):
        self.assembly = []

    def generate(self, node):
        method_name = f"generate_{type(node).__name__}"
        generator = getattr(self, method_name, self.generic_gen)
        return generator(node)

    def generic_gen(self, node):
        raise NotImplementedError(f"Generation not implemented for {type(node).__name__}")

    def generate_Program(self, node):
        self.generate(node.function)
        return "\n".join(self.assembly)

    def generate_Function(self, node):
        self.assembly.append(f"global {node.name}")
        self.assembly.append(f"{node.name}:")
        self.assembly.append("    push rbp")
        self.assembly.append("    mov rbp, rsp")
        
        for statement in node.body:
            self.generate(statement)

    def generate_ReturnStatement(self, node):
        self.generate(node.expression)
        self.assembly.append("    pop rax")
        self.assembly.append("    mov rsp, rbp")
        self.assembly.append("    pop rbp")
        self.assembly.append("    ret")

    def generate_Number(self, node):
        self.assembly.append(f"    push {node.value.value}")

    def generate_UnaryOps(self, node):
        self.generate(node.right)
        op_type = node.op.type 

        if op_type == TokenType.MINUS:
            self.assembly.append("    pop rax")
            self.assembly.append("    neg rax")
            self.assembly.append("    push rax")
        elif op_type == TokenType.LOGICAL_NEGATION:
            self.assembly.append("    pop rax")
            self.assembly.append("    cmp rax, 0")
            self.assembly.append("    sete al")
            self.assembly.append("    movzx rax, al")
            self.assembly.append("    push rax")
        elif op_type == TokenType.BITWISE_COMPLEMENT:
            self.assembly.append("    pop rax")
            self.assembly.append("    not rax")
            self.assembly.append("    push rax")
        else:
            raise NotImplementedError(f"Unary operation {op_type} not implemented.")

    def generate_BinaryOps(self, node):
        self.generate(node.right)
        self.generate(node.left)
        
        self.assembly.append("    pop rbx") # left operand 
        self.assembly.append("    pop rax") # right operand 

        op_type = node.op.type

        if op_type == TokenType.PLUS:
            self.assembly.append("    add rax, rbx") 
        elif op_type == TokenType.MINUS:
            self.assembly.append("    sub rax, rbx")
        elif op_type == TokenType.STAR:
            self.assembly.append("    imul rbx")
        elif op_type == TokenType.SLASH:
            self.assembly.append("    cqo") # sign-extend eax into edx 
            self.assembly.append("    idiv rbx")
        elif op_type == TokenType.PERCENT:
            self.assembly.append("    cqo")
            self.assembly.append("    idiv rbx")
            self.assembly.append("    mov rax, rdx") # remainder goes in rdx 
        elif op_type == TokenType.BITWISE_AND:
            self.assembly.append("    and rax, rbx")
        elif op_type == TokenType.BITWISE_OR:
            self.assembly.append("    or rax, rbx")
        elif op_type == TokenType.BITWISE_XOR:
            self.assembly.append("    xor rax, rbx")
        elif op_type == TokenType.BITWISE_SHIFT_LEFT:
            self.assembly.append("    mov rcx, rbx")
            self.assembly.append("    shl rax, cl")
        elif op_type == TokenType.BITWISE_SHIFT_RIGHT:
            self.assembly.append("    mov rcx, rbx")
            self.assembly.append("    shr rax, cl")
        elif op_type == TokenType.OR:
            self.assembly.append("    or rax, rbx")
        elif op_type == TokenType.AND:
            self.assembly.append("    and rax, rbx")
        elif op_type in [
                TokenType.EQUAL, TokenType.NOT_EQUAL, 
                TokenType.LESS_THAN, TokenType.LESS_THAN_OR_EQUAL, 
                TokenType.GREATER_THAN, TokenType.GREATER_THAN_OR_EQUAL
            ]:
            self.assembly.append("    cmp rax, rbx")
            if op_type == TokenType.EQUAL:
                self.assembly.append("    sete al")
            elif op_type == TokenType.NOT_EQUAL:
                self.assembly.append("    setne al")
            elif op_type == TokenType.LESS_THAN:
                self.assembly.append("    setl al")
            elif op_type == TokenType.LESS_THAN_OR_EQUAL:
                self.assembly.append("    setle al")
            elif op_type == TokenType.GREATER_THAN:
                self.assembly.append("    setg al")
            elif op_type == TokenType.GREATER_THAN_OR_EQUAL:
                self.assembly.append("    setge al")
            self.assembly.append("    movzx rax, al")
        else:
            raise NotImplementedError(f"Binary operation {op_type} not implemented.")

        self.assembly.append("    push rax") # push result
