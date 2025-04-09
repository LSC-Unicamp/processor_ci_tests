# cor implementation
# c.or
.text
.globl _start

_start:
    li a0, 0b0100
    li a1, 0b1000
    c.or a0, a1           # a0 = 0b1100
    sw a0, 60(zero)
