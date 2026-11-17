.text
.globl _start
_start:
  la t0, atomic_word
  li t1, 5
  amoadd.w t2, t1, (t0)
test_done:
  li t3, 1
  la t4, tohost
  sw t3, 0(t4)
1: j 1b
.data
.align 3
.globl tohost
tohost: .dword 0
.align 2
atomic_word: .word 1
