.text
.global _start

_start:
# remu - a3 = a1 % a2 (unsigned)
# Caso 72
    li a1, -1     # a1=0xFFFFFFFF, a2=0xFFFFFFFF
    li a2, -1
    remu a3, a1, a2
    sw a3, 60(zero)
