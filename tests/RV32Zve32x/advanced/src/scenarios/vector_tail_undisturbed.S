# Scenario: vector_tail_undisturbed; category: vector; ISA: rv32im_zicsr_zve32x_zvl128b
# Initial state: all used registers and memory locations initialized in this program.
# Expected a0: 0x1; completion: status word 1=PASS, 2=FAIL.
.section .text
.global _start
_start:
vsetivli t0, 4, e32, m1, tu, mu
vmv.v.i v1, 2
vmv.v.i v2, 3
vmv.v.i v3, 9
vsetivli t0, 2, e32, m1, tu, mu
vadd.vv v3, v1, v2
vsetivli t0, 4, e32, m1, tu, mu
la t1, vector32_result
vse32.v v3, (t1)
lw t2, 0(t1)
li t3, 5
bne t2, t3, failure
lw t2, 4(t1)
bne t2, t3, failure
lw t2, 8(t1)
li t3, 9
bne t2, t3, failure
lw t2, 12(t1)
bne t2, t3, failure
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
