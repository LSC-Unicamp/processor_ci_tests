# caddi implementation
# c.addi
.text
.globl _start

_start:
    li a0, 10
    c.addi a0, 5          # a0 = a0 + 5 = 15
    sw a0, 60(zero)
