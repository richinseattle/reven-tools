; @richinseattle
; reven x86 start/stop trace stubs

; nasm -fwin32 reven_traceme.nasm -o reven_traceme.obj
; nasm -felf32 reven_traceme.nasm -o reven_traceme.o

BITS 32

section .text 

global _start_reven_trace
_start_vm:
	push ebp
	mov  ebp, esp
	mov  eax, 0xeff1cad6
	mov  edx, 0xdeadbabe
	int3
	pop  ebp
	ret


global _stop_reven_trace
_stop_vm: 
	push ebp
	mov  ebp, esp
	mov  eax, 0xeff1cad1
	mov  edx, 0xdeadbabe
	int3
	pop  ebp
	ret
