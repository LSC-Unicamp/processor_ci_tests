.text
.global _start

_start:
# remu - a3 = a1 % a2 (unsigned)
# Caso 73
    li a1, 0     # a1=0x00000000, a2=0x000004D2
    li a2, 1234
    remu a3, a1, a2
    sw a3, 60(zero)
