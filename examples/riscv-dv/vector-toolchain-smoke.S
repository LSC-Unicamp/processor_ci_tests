.text
.globl _start
_start:
  vsetvli t0, zero, e32, m1, ta, ma
  vadd.vv v1, v2, v3
