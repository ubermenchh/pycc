from .tokentype import TokenType
import subprocess, os

class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, function_list):
        self.function_list = function_list 

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
    def __init__(self, type, name, exp=None):
        self.type = type
        self.name = name 
        self.exp = exp

class Assign(ASTNode):
    def __init__(self, name, exp):
        self.name = name 
        self.exp = exp

class Variable(ASTNode):
    def __init__(self, name):
        self.name = name

class Conditional(ASTNode):
    def __init__(self, condition, if_stmt, else_stmt=None):
        self.condition = condition
        self.if_stmt = if_stmt 
        self.else_stmt = else_stmt

class Block(ASTNode):
    def __init__(self, statements):
        self.statements = statements

class For(ASTNode):
    def __init__(self, init, condition, update, stmt):
        self.init = init  
        self.condition = condition 
        self.update = update
        self.stmt = stmt 

class While(ASTNode):
    def __init__(self, condition, stmt):
        self.condition = condition 
        self.stmt = stmt 

class Do(ASTNode):
    def __init__(self, stmt, exp):
        self.stmt = stmt 
        self.exp = exp 

class Break(ASTNode): pass 
class Continue(ASTNode): pass

class FunctionDeclaration(ASTNode):
    def __init__(self, type, name, params):
        self.type = type 
        self.name = name 
        self.params = params

class FunctionCall(ASTNode):
    def __init__(self, name, params):
        self.name = name 
        self.params = params

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
        func_list = []
        while self.check(TokenType.INT):
            func_list.append(self.function())
        return Program(func_list)

    def function(self):
        type = self.consume(TokenType.INT, "Expected function return type.").value
        name = self.consume(TokenType.IDENTIFIER, "Expected function name.").value
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after function name.")
        parameters = self.parameter_list()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters.")
        body = None 
        if self.match(TokenType.SEMICOLON):
            return FunctionDeclaration(type, name, parameters)
        elif self.check(TokenType.LEFT_BRACE):
            body = self.block()
            return Function(type, name, parameters, body)
        else:
            raise Exception("Expected ';' or '{' after function name.")

    def parameter_list(self):
        params = []
        if self.match(TokenType.INT):
            self.consume(TokenType.IDENTIFIER, "Expected variable name.")
            params.append(Variable(self.previous()))
            while self.match(TokenType.COMMA):
                self.consume(TokenType.INT, "Expected variable type.")
                self.consume(TokenType.IDENTIFIER, "Expected variable name.")
                params.append(Variable(self.previous()))
        return params

    def block(self):
        self.consume(TokenType.LEFT_BRACE, "Expected '{' before block.")
        statements = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration_or_statement())
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after block.")
        return Block(statements) 
    
    def declaration(self):
        type = self.previous().value
        name = self.consume(TokenType.IDENTIFIER, "Expected variable name.").value
        exp = None 
        if self.match(TokenType.ASSIGN):
            exp = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after variable declaration.")
        return Declaration(type, name, exp)

    def statement(self):
        if self.match(TokenType.RETURN):
            return self.return_statement()
        elif self.match(TokenType.INT):
            return self.declaration()
        elif self.match(TokenType.IF):
            return self.if_statement()
        elif self.check(TokenType.LEFT_BRACE):
            return self.block()
        elif self.match(TokenType.FOR):
            return self.for_statement()
        elif self.match(TokenType.WHILE):
            return self.while_statement()
        elif self.match(TokenType.DO):
            return self.do_while_statement()
        elif self.match(TokenType.BREAK):
            self.consume(TokenType.SEMICOLON, "Expected ';' after break.")
            return Break()
        elif self.match(TokenType.CONTINUE): 
            self.consume(TokenType.SEMICOLON, "Expected ';' after continue.")
            return Continue();
        else:
            return self.expression_statement()
    
    def declaration_or_statement(self):
        if self.match(TokenType.INT):
            return self.declaration()
        return self.statement()

    def expression_statement(self):
        exp = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after expression.")
        return exp

    def return_statement(self):
        exp = self.expression()
        if not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            self.consume(TokenType.SEMICOLON, "Expected ';' after return statement.")
        return ReturnStatement(exp)

    def if_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after if.")
        cond = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after condition.")
        
        if self.check(TokenType.LEFT_BRACE):
            then_branch = self.block()
        else:
            then_branch = self.statement()
        else_branch = None 
        if self.match(TokenType.ELSE):    
            if self.check(TokenType.LEFT_BRACE):
                else_branch = self.block()
            else:
                else_branch = self.statement()
        return Conditional(cond, then_branch, else_branch)
    
    def for_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after for.")
        if self.match(TokenType.SEMICOLON):
            init = None 
        else:
            init = self.declaration_or_statement()
        
        if self.match(TokenType.SEMICOLON):
            condition = None
        else:
            condition = self.expression()
            self.consume(TokenType.SEMICOLON, "Expected ';' after condition.")
        
        if self.match(TokenType.RIGHT_PAREN):
            update = None
        else:
            update = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' before for block.")
        
        if self.check(TokenType.LEFT_BRACE):
            stmt = self.block()
        else:
            stmt = self.statement()
        return For(init, condition, update, stmt) 
    
    def while_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after while.")
        exp = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after condition.")
        if self.check(TokenType.LEFT_BRACE):
            stmt = self.block()
        else:
            stmt = self.statement()
        return While(exp, stmt)

    def do_while_statement(self):
        if self.check(TokenType.LEFT_BRACE):
            stmt = self.block()
        else:
            stmt = self.statement()
        self.consume(TokenType.WHILE, "Expected 'while' after do block.")
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after while.")
        exp = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after condition.") 
        self.consume(TokenType.SEMICOLON, "Expected ';' after while.")
        return Do(stmt, exp)

    def expression(self):
        return self.assignment()

    def assignment(self):
        exp = self.conditional_expression()
        if self.match(TokenType.ASSIGN):
            if isinstance(exp, Variable):
                name = exp.name 
                value = self.assignment()
                return Assign(name, value)
            elif isinstance(exp, BinaryOps) and isinstance(exp.left, Variable):
                name = exp.left.name 
                value = Assign(exp.right, self.assignment())
                return Assign(name, value)
            else:
                raise Exception("Invalid assignment target.")
        return exp

    def conditional_expression(self):
        exp = self.bitwise_or_expression()
        if self.match(TokenType.QUESTION):
            if_stmt = self.expression()
            self.consume(TokenType.COLON, "Expected ':' after '?' in ternary statement.")
            else_stmt = self.conditional_expression()
            return Conditional(exp, if_stmt, else_stmt)
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
        while self.match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
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
            if self.check(TokenType.LEFT_PAREN):
                return self.function_call()
            else:
                return Variable(self.previous())
        else:
            return print("Failed!")
    
    def argument_list(self):
        args = [self.expression()]
        while self.match(TokenType.COMMA):
            if len(args) > 255:
                raise Exception("Cannot have more than 255 arguments.")
            args.append(self.expression())
        return args

    def function_call(self):
        name = self.previous()
        args = []
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after function name.")
        if not self.check(TokenType.RIGHT_PAREN):
            args = self.argument_list()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters.")
        return FunctionCall(name, args)

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
        for function in node.function_list:
            result += self.print(function)
        self.indent_level -= 1
        return result 

    def print_Function(self, node):        
        result = self.indented(f"Function: {node.return_type} {node.name}\n")    
        self.indent_level += 1
        if node.parameters:
            result += self.indented("Parameters: \n")
            self.indent_level += 1
            for param in node.parameters:
                result += self.print(param) + "\n"
            self.indent_level -= 1
        if node.body:
            result += self.indented("Body:\n")
            self.indent_level += 1
            for statement in node.body.statements:
                result += self.print(statement) + "\n"
            self.indent_level -= 1
        self.indent_level -= 1
        return result 

    def print_FunctionDeclaration(self, node):
        result = self.indented(f"Function Declaration: {node.type} {node.name}\n")
        return result

    def print_FunctionCall(self, node):
        result = self.indented(f"FunctionCall: {node.name.value}\n")
        self.indent_level += 1 
        if node.params:
            result += self.indented(f"Arguments: \n")
            self.indent_level += 1
            for p in node.params:
                result += self.print(p) + "\n"
            self.indent_level -= 1
        self.indent_level -= 1
        return result

    def print_ReturnStatement(self, node):
        result = self.indented("Return:\n")
        self.indent_level += 1
        result += self.print(node.expression) + "\n"
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
            result += self.print(node.exp) + "\n"
            self.indent_level -= 2
        return result

    def print_Variable(self, node):
        return self.indented(f"Variable: {node.name.value}")

    def print_Assign(self, node):
        print(node.name)
        result = self.indented(f"Assign: {node.name.value}\n")
        self.indent_level += 1
        result += self.indented("Value:\n")
        self.indent_level += 1
        result += self.print(node.exp)
        self.indent_level -= 2
        return result

    def print_Conditional(self, node):
        result = self.indented(f"Conditional: \n")
        self.indent_level += 1
        result += self.indented(f"If: \n")
        self.indent_level += 1
        result += self.print(node.condition) + "\n"
        self.indent_level -= 1
        result += self.indented(f"Then: \n")
        self.indent_level += 1
        if isinstance(node.if_stmt, list):
            for stmt in node.if_stmt:
                result += self.print(stmt) + "\n"
        else:
            result += self.print(node.if_stmt) + "\n"
        self.indent_level -= 1
        result += self.indented(f"Else: \n")
        self.indent_level += 1
        if isinstance(node.else_stmt, list):
            for stmt in node.else_stmt:
                result += self.print(stmt) + "\n"
        else:
            result += self.print(node.else_stmt)
        self.indent_level -= 2
        return result

    def print_Block(self, node):
        result = self.indented("Block: \n")
        self.indent_level += 1
        if isinstance(node.statements, list):
            for stmt in node.statements:
                result += self.print(stmt)
        else:
            result += self.print(node.statements)
        self.indent_level -= 1
        return result 

    def print_For(self, node):
        result = self.indented("For: \n")
        self.indent_level += 1
        result += self.indented("Init: \n")
        self.indent_level += 1
        result += self.print(node.init)
        self.indent_level -= 1
        result += self.indented("Condition: \n")
        self.indent_level += 1
        result += self.print(node.condition) + "\n"
        self.indent_level -= 1 
        result += self.indented("Update: \n")
        self.indent_level += 1
        result += self.print(node.update) + "\n"
        self.indent_level -= 1
        result += self.print(node.stmt)
        self.indent_level -= 1 
        return result

    def print_While(self, node):
        result = self.indented("While:\n")
        self.indent_level += 1 
        result += self.indented("Condition:\n")
        self.indent_level += 1 
        result += self.print(node.condition) + "\n"
        self.indent_level -= 1 
        result += self.print(node.stmt)
        self.indent_level -= 1
        return result

    def print_Do(self, node):
        result = self.indented("Do:\n")
        self.indent_level += 1 
        result += self.print(node.stmt) + "\n"
        result += self.indented("While:\n")
        self.indent_level += 1
        result += self.print(node.exp) + "\n"
        self.indent_level -= 2
        return result
    
    def print_Break(self, node):
        result = self.indented("Break\n")
        return result 

    def print_Continue(self, node):
        result = self.indented("Continue\n")
        return result

class ASMGenerator:
    def __init__(self):
        self.assembly = []
        self.scopes = [{}]
        self.loop_stack = []
        self.stack_index = 0
        self.label_count = 0
        self.arg_registers = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]
        self.external_functions = set()
        self.function_prototypes = {}
        self.defined_functions = set()
    
    def enter_scope(self): 
        self.scopes.append({})

    def exit_scope(self):
        scope = self.scopes.pop()
        if scope:
            self.stack_index -= 8 * len(scope) 
            self.assembly.append(f"    add rsp, {8 * len(scope)}")

    def enter_loop(self, start_label, end_label):
        self.loop_stack.append((start_label, end_label))

    def exit_loop(self):
        self.loop_stack.pop()

    def find_variable(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise Exception(f"Undefined Variable : {name}")

    def generate(self, node):
        method_name = f"generate_{type(node).__name__}"
        generator = getattr(self, method_name, self.generic_gen)
        return generator(node)

    def generic_gen(self, node):
        raise NotImplementedError(f"Generation not implemented for {type(node).__name__}")

    def generate_Program(self, node):
        self.assembly.extend([
            "default rel",
            "section .text",
            "global main",
        ])

        # generate code for all functions
        for function in node.function_list:
            if isinstance(function, FunctionDeclaration):
                self.function_prototypes[function.name] = len(function.params)
            elif isinstance(function, Function):
                self.defined_functions.add(function.name)
                self.function_prototypes[function.name] = len(function.parameters)
        
        for function in node.function_list:
            if isinstance(function, Function):
                self.generate(function)

        # remove defined functions from prototypes 
        for func in self.defined_functions:
            self.function_prototypes.pop(func, None)

        # add external function declaratiions at the beginning, after the initial directives
        extern_declarations = [f"extern {func}" for func in self.function_prototypes.keys()]
        self.assembly = self.assembly[:3] + extern_declarations + self.assembly[3:] 
        
        return "\n".join(self.assembly)
    
    def generate_FunctionDeclaration(self, node):
        self.scopes[0][node.name] = "function"

    def generate_Function(self, node):
        self.scopes[0][node.name] = "function"
        if not node.body: return

        self.current_function = self.new_label("function_end") # function end label
        self.assembly.extend([
            f"{node.name}:",
            "    push rbp",
            "    mov rbp, rsp"
        ])
        
        self.enter_scope()
        
        # handle function parameters 
        for i, param in enumerate(node.parameters):
            self.stack_index += 8 
            self.scopes[-1][param.name.value] = self.stack_index 
            if i < len(self.arg_registers):
                self.assembly.append(f"    mov [rbp - {self.stack_index}], {self.arg_registers[i]}")

        self.generate_statements(node.body)
        self.exit_scope()

        # Function epilogue
        self.assembly.extend([
            f"{self.current_function}:",
            "    mov rsp, rbp",
            "    pop rbp",
            "    ret"
        ])

    def generate_FunctionCall(self, node): 
        #param_count = self.function_prototypes.get(node.name.value, len(node.params))
        param_count = len(node.params)

        # evaluate and push arguments in reverse order 
        for arg in reversed(node.params):
            self.generate(arg)
            self.assembly.append("    push rax")

        # pop arguments into the appropriate registers 
        for i in range(min(param_count, len(self.arg_registers))):
            self.assembly.append(f"    pop {self.arg_registers[i]}")
        
        # align stack to 16 bytes 
        if param_count % 2 != 0:
            self.assembly.append("    sub rsp, 8")

        # call the function 
        self.assembly.append(f"    call {node.name.value}")

        # restore stack alignment if adjusted
        #stack_cleanup = max(0, param_count - len(self.arg_registers)) * 8
        #if stack_cleanup > 0 or param_count % 2 == 1:
        #    cleanup_amount = stack_cleanup + (8 if param_count % 2 == 1 else 0)
        #    self.assembly.append(f"    add rsp, {cleanup_amount}")
        if param_count % 2 != 0:
            self.assembly.append("    add rsp, 8")

    def generate_Block(self, node):
        self.enter_scope()
        self.generate_statements(node.statements)
        self.exit_scope()

    def generate_statements(self, statements):
        if isinstance(statements, list):
            for stmt in statements:
                self.generate(stmt)
        else:
            self.generate(statements)

    def generate_ReturnStatement(self, node):
        if node.expression:
            self.generate(node.expression)
        else:
            self.assembly.append("    xor rax, rax") # return 0 if no expression
        self.assembly.append(f"    jmp {self.current_function}")

    def generate_Number(self, node):
        self.assembly.append(f"    mov rax, {node.value.value}")

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
        if node.op.type in [TokenType.OR, TokenType.AND]:
            end_label = self.new_label("logical_end")
            self.generate(node.left)
            self.assembly.append("    pop rax")
            self.assembly.append("    cmp rax, 0")

            if node.op.type == TokenType.OR:
                self.assembly.append(f"    jne {end_label}")
            else:
                self.assembly.append(f"    je {end_label}")

            self.generate(node.right)
            self.assembly.append(f"{end_label}:")
            return

        self.generate(node.left)
        self.assembly.append("    push rax") # save left operand result
        self.generate(node.right)
        self.assembly.append("    pop rbx") # retrieve left operand result

        op_map = {
            TokenType.PLUS: "    add rax, rbx",
            TokenType.MINUS: [
                "    sub rbx, rax",
                "    mov rax, rbx"
            ],
            TokenType.STAR: "    imul rbx",
            TokenType.SLASH: [
                "    mov rcx, rax", # save divisor
                "    mov rax, rbx", # move dividend to rax 
                "    cqo",          # sign-extend rax into rdx:rax
                "    idiv rcx",     # divide rdx:rax by rcx
            ],
            TokenType.PERCENT:  [
                "    mov rcx, rax", # save divisor
                "    mov rax, rbx", # move dividend to rax 
                "    cqo",          # sign-extend rax into rdx:rax 
                "    idiv rcx",     # divide rdx:rax by rcx 
                "    mov rax, rdx"  # move remainder to rax
            ],
            TokenType.BITWISE_OR: "    or rax, rbx",
            TokenType.BITWISE_AND: "    and rax, rbx",
            TokenType.BITWISE_XOR: "    xor rax, rbx",
            TokenType.BITWISE_SHIFT_LEFT: [
                "    mov rcx, rbx",
                "    mov rax, rbx",
                "    shl rax, cl"
            ],
            TokenType.BITWISE_SHIFT_RIGHT:  [
                "    mov rcx, rbx",
                "    mov rax, rbx",
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


    def generate_Declaration(self, node):
        self.stack_index += 8 
        self.scopes[-1][node.name] = self.stack_index 
        self.assembly.append(f"    sub rsp, 8")

        if node.exp:
            self.generate(node.exp)
            self.assembly.append(f"    mov [rbp - {self.stack_index}], rax")
        else:
            self.assembly.append(f"    mov qword [rbp - {self.stack_index}], 0")

    def generate_Assign(self, node):
        self.generate(node.exp)
        offset = self.find_variable(node.name.value)
        self.assembly.append(f"    mov [rbp - {offset}], rax")

    def generate_Variable(self, node):
        offset = self.find_variable(node.name.value)
        self.assembly.append(f"    mov rax, [rbp - {offset}]")

    def generate_Conditional(self, node):
        end_label = self.new_label("end")
        else_label = self.new_label("else")

        self.generate(node.condition)
        self.assembly.extend([
            "    cmp rax, 0",
            f"    je {else_label}"
        ])

        self.generate(node.if_stmt)
        self.assembly.append(f"    jmp {end_label}")

        self.assembly.append(f"{else_label}:")
        if node.else_stmt:
            self.generate(node.else_stmt)

        self.assembly.append(f"{end_label}:")

    def generate_For(self, node):
        loop_start = self.new_label("for_start")
        loop_end = self.new_label("for_end")

        self.enter_loop(loop_start, loop_end)
        # Generate Initialization 
        if node.init:
            self.generate(node.init)
        self.assembly.append(f"{loop_start}:")

        # Generate Condition 
        if node.condition:
            self.generate(node.condition)
            self.assembly.extend([
                "    cmp rax, 0",
                f"    je {loop_end}"
            ])

        # Generate loop body 
        self.generate(node.stmt)

        # Generate Update 
        if node.update:
            self.generate(node.update)

        # jump back to start 
        self.assembly.append(f"    jmp {loop_start}")
        # end of loop
        self.assembly.append(f"{loop_end}:")
        self.exit_loop()

    def generate_While(self, node):
        loop_start = self.new_label("while_start")
        loop_end = self.new_label("while_end")

        self.enter_loop(loop_start, loop_end)
        self.assembly.append(f"{loop_start}:") # loop start
        # Generate Condition 
        if node.condition:
            self.generate(node.condition)
            self.assembly.extend([
                "    cmp rax, 0",
                f"    je {loop_end}"
            ])
        # Generate loop body 
        self.generate(node.stmt)
        # jump back to start 
        self.assembly.append(f"    jmp {loop_start}")
        # end of loop 
        self.assembly.append(f"{loop_end}:")
        self.exit_loop()

    def generate_Do(self, node):
        loop_start = self.new_label("do_start")
        loop_end = self.new_label("do_end")

        self.enter_loop(loop_start, loop_end)
        self.assembly.append(f"{loop_start}:") # loop start 
        self.generate(node.stmt) # loop body

        self.generate(node.exp) # while condition
        self.assembly.extend([
            "    cmp rax, 0",
            f"    jne {loop_start}" # jump back to start if condition is true
        ])
        self.assembly.append(f"{loop_end}:") # loop end
        self.exit_loop()

    def generate_Break(self, node):
        if not self.loop_stack:
            raise Exception("Break statement outside of loop")
        _, end_label = self.loop_stack[-1]
        self.assembly.append(f"    jmp {end_label}")

    def generate_Continue(self, node):
        if not self.loop_stack:
            raise Exception("Continue statement outside of loop")
        start_label, _ = self.loop_stack[-1]
        self.assembly.append(f"    jmp {start_label}")

    def new_label(self, prefix):
        self.label_count += 1
        return f".{prefix}_{self.label_count}"

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

