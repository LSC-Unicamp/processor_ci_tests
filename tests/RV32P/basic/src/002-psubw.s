.text
.global _start

_start:
    li a1, 100
    li a2, 58
    psubw a3, a1, a2       # a3 = 100 - 58 = 42 (sub palavra)
    sw a3, 60(zero)
