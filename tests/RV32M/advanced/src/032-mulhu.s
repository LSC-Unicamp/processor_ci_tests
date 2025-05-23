.text
.global _start

_start:
# mulhu - a3 = high(a1 * a2 unsigned)
# Caso 32
    li a1, -1     # a1=0xFFFFFFFF, a2=0xFFFFFFFF
    li a2, -1
    mulhu a3, a1, a2
    sw a3, 60(zero)
