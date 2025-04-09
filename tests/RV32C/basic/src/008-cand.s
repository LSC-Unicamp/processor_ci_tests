# cand implementation
# c.and
.text
.globl _start

_start:
    li a0, 0b1100
    li a1, 0b1010
    c.and a0, a1          # a0 = a0 & a1 = 0b1000
    sw a0, 60(zero)
