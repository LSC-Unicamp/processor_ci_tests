.section .text.init
.globl _start
_start:
  li t0, 0x600
  csrs mstatus, t0
  vsetivli t0, 4, e32, m1, ta, ma
  vmv.v.i v1, 1
  vmv.v.i v2, 2
  vadd.vv v3, v1, v2
  la a0, vector_output
  vse32.v v3, (a0)
.globl test_done
test_done:
  li gp, 1
  la t0, tohost
  sw gp, 0(t0)
1: j 1b

.section .data
.align 4
vector_output:
  .zero 16

.section .tohost,"aw",@progbits
.align 3
.globl tohost
tohost:
  .dword 0
.globl fromhost
fromhost:
  .dword 0
