# csub implementation
# c.sub
.text
.globl _start

_start:
    li a0, 10
    li a1, 3
    c.sub a0, a1          # a0 = a0 - a1 = 7
    sw a0, 60(zero)
