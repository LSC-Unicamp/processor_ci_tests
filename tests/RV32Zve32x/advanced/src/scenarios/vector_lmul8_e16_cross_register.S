# Scenario: vector_lmul8_e16_cross_register; category: vector; ISA: rv32im_zicsr_zve32x_zvl128b
# Initial state: all used registers and memory locations initialized in this program.
# Expected a0: 0x1; completion: status word 1=PASS, 2=FAIL.
.section .text
.global _start
_start:
li t1, 40
vsetvli t0, t1, e16, m8, ta, ma
bne t0, t1, failure
vmv.v.i v8, 7
la t2, vector40_result
vse16.v v8, (t2)
li t3, 0
1: lhu t4, 0(t2)
li t5, 7
bne t4, t5, failure
addi t2, t2, 2
addi t3, t3, 1
blt t3, t1, 1b
li a0, 1
li t0, 1
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
