# candi implementation
# c.andi
.text
.globl _start

_start:
    li a0, 0b1101
    c.andi a0, 0b0101     # a0 = 0b1101 & 0b0101 = 0b0101
    sw a0, 60(zero)
