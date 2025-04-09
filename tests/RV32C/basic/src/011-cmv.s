# cmv implementation
# c.mv (move register)
.text
.globl _start

_start:
    li a1, 7
    c.mv a0, a1           # a0 = a1
    sw a0, 60(zero)
