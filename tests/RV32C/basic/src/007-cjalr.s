# cjalr implementation
# c.jalr (jump and link to register)
.text
.globl _start

_start:
    la t0, target
    c.jalr t0

    li a0, 0xBAD
    sw a0, 60(zero)

target:
    li a0, 0xABCD
    sw a0, 60(zero)
