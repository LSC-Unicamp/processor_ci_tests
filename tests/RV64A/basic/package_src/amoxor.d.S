# Dedicated RV64A basic test for amoxor.d; ISA rv64ia
# Initialized operands in body. Expected a0 = 0x5.
.section .text
.global _start
_start:
la t1, atomic_double
li t2, 3
amoxor.d a0, t2, (t1)
ld t3, 0(t1)
li t4, 6
bne t3, t4, failure
li t0, 5
bne a0, t0, failure
li t1, 1
j report
failure:
li t1, 3
report:
la t2, tohost
sw t1, 0(t2)
sw zero, 4(t2)
1: j 1b
.section .tohost,"aw",@progbits
.balign 8
.global tohost
tohost: .dword 0
.global fromhost
fromhost: .dword 0
.section .data
.balign 4
data_word: .word 0x80ff7f01
scratch: .word 0x12345678
atomic_word: .word 5
vector_words: .word 0x80ff7f01, 2, 3, 4
vector_scratch: .word 0, 0, 0, 0
.balign 8
fp_double: .dword 0x0123456789abcdef
scratch_double: .dword 0
fp_word: .word 0x3f800000
fp_two: .word 0x40000000
fp_four: .word 0x40800000
.balign 8
atomic_double: .dword 5
double_one: .dword 0x3ff0000000000000
double_two: .dword 0x4000000000000000
double_four: .dword 0x4010000000000000
