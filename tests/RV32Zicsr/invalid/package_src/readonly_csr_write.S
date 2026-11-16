# Expected M-mode trap for readonly_csr_write; mcause=2; mepc=trigger.
.section .text
.global _start
_start:
la t0, trap_handler
csrw mtvec, t0
li t5, 1

trigger:
csrrw zero, marchid, t5
j missing_trap
.balign 4
trap_handler:
csrr t1, mcause
li t2, 2
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

