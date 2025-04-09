# cadd implementation
# c.add
.text
.globl _start

_start:
    li a0, 5
    li a1, 10
    c.add a0, a1          # a0 = a0 + a1 = 15
    sw a0, 60(zero)
