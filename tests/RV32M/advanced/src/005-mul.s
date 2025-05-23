.text
.global _start

_start:
# mul - a3 = a1 * a2
# Caso 5
    li a1, 0     # a1=0x00000000, a2=0x00000000
    li a2, 0
    mul a3, a1, a2
    sw a3, 60(zero)
