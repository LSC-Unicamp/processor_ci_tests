# cjr implementation
# c.jr (jump to register)
.text
.globl _start

_start:
    la t0, target
    c.jr t0

    li a0, 0xBAD
    sw a0, 60(zero)

target:
    li a0, 0xBEEF
    sw a0, 60(zero)
