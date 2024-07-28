# Takes each token from the token list and constructs a AST 
# 
# <program> ::= <function>
# <function> ::= "int" <id> "(" ")" "{" <statement> "}"
# <statement> ::= "return" <exp> ";"
# <exp> ::= <int>

from lexer import TokenType

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

class Literal(ASTNode):
    def __init__(self, value):
        self.value = value

class UnaryOps(ASTNode):
    def __init__(self, op, exp):
        self.op = op
        self.exp = exp

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
    
    def statement(self):
        if self.match(TokenType.RETURN):
            return self.return_statement()
        raise Exception("Expected statement")

    def return_statement(self):
        exp = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after return statement.")
        return ReturnStatement(exp)
    
    def expression(self):
        return self.unary()

    def unary(self):
        if self.match(TokenType.NEGATION, TokenType.LOGICAL_NEGATION, TokenType.BITWISE_COMPLEMENT):
            op = self.previous()
            right = self.unary()
            return UnaryOps(op, right)
        return self.primary()

    def primary(self):
        if self.match(TokenType.LITERAL):
            return Literal(self.previous().value)
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

    def print_Literal(self, node):
        return self.indented(f"Literal: {node.value}")

    def print_UnaryOps(self, node):
        result = self.indented(f"UnaryOps: {node.op.type.name}") + "\n"
        result += self.print(node.exp)
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
        self.assembly.append("    push ebp")
        self.assembly.append("    mov ebp, esp")
        
        for statement in node.body:
            self.generate(statement)

    def generate_ReturnStatement(self, node):
        self.generate(node.expression)
        self.assembly.append("    pop eax")
        self.assembly.append("    mov esp, ebp")
        self.assembly.append("    pop ebp")
        self.assembly.append("    ret")

    def generate_Literal(self, node):
        self.assembly.append(f"    push {node.value}")

    def generate_UnaryOps(self, node):
        self.generate(node.exp)
        op_type = node.op.type 

        if op_type == TokenType.NEGATION:
            self.assembly.append("    pop eax")
            self.assembly.append("    neg eax")
            self.assembly.append("    push eax")
        elif op_type == TokenType.LOGICAL_NEGATION:
            self.assembly.append("    pop eax")
            self.assembly.append("    cmp eax, 0")
            self.assembly.append("    sete al")
            self.assembly.append("    movzx eax, al")
            self.assembly.append("    push eax")
        elif op_type == TokenType.BITWISE_COMPLEMENT:
            self.assembly.append("    pop eax")
            self.assembly.append("    not eax")
            self.assembly.append("    push eax")
        else:
            raise NotImplementedError(f"Unary operation {op_type} not implemented.")
