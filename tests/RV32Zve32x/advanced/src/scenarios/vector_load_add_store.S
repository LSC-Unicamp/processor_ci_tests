# Scenario: vector_load_add_store; category: vector; ISA: rv32im_zicsr_zve32x_zvl128b
# Initial state: all used registers and memory locations initialized in this program.
# Expected a0: 0x18; completion: status word 1=PASS, 2=FAIL.
.section .text
.global _start
_start:
vsetivli t0, 2, e32, m1, ta, ma
la t1, scratch
li t2, 7
sw t2, 0(t1)
li t2, 11
sw t2, 4(t1)
vle32.v v1, (t1)
vadd.vi v2, v1, 3
vse32.v v2, (t1)
lw t3, 0(t1)
lw t4, 4(t1)
add a0, t3, t4
li t0, 24
bne a0, t0, failure
la t1, result_status
li t2, 1
sw t2, 0(t1)
li a0, 0
j completion
failure:
la t1, result_status
li t2, 2
sw t2, 0(t1)
li a0, 1
completion:
li a7, 93
ecall
.section .data
.balign 4
data_word: .word 5
scratch: .word 0, 0
result_status: .word 0
.balign 8
scratch64: .dword 0
vector64_data: .dword 1, 2
vector64_result: .dword 0, 0
vector32_result: .word 0, 0, 0, 0
vector8_data: .byte 127, 126, 0, 255
vector8_result: .byte 0, 0, 0, 0
vector20_data: .byte 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20
vector20_result: .space 20
vector40_result: .space 80
