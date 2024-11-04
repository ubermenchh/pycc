# Generates x86-64 Assembly from an AST

import subprocess
import os

from .parser import *

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
