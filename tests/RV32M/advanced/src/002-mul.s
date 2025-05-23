.text
.global _start

_start:
# mul - a3 = a1 * a2
# Caso 2
    li a1, -1     # a1=0xFFFFFFFF, a2=0xFFFFFFFF
    li a2, -1
    mul a3, a1, a2
    sw a3, 60(zero)
