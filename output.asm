default rel
section .text
global main
extern printf
main:
    push rbp
    mov rbp, rsp
    push 9
    push 6
    pop rbx
    pop rax
    add rax, rbx
    push rax
    pop rax
    mov rsp, rbp
    pop rbp
    ret
