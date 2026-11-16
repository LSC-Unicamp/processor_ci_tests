# Expected M-mode trap for misaligned_store; mcause=6; mepc=trigger.
.section .text
.global _start
_start:
la t0, trap_handler
csrw mtvec, t0
la t4, misaligned_operand
li t5, 0x12345678

trigger:
sw t5, 1(t4)
j missing_trap
.balign 4
trap_handler:
csrr t1, mcause
li t2, 6
bne t1, t2, wrong_cause
csrr t1, mepc
la t2, trigger
bne t1, t2, wrong_mepc
li t1, 1
j report
missing_trap:
li t1, 3
j report
wrong_cause:
li t1, 5
j report
wrong_mepc:
li t1, 7
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
misaligned_operand: .word 0xabcdef01, 0x23456789

