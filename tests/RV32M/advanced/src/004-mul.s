.text
.global _start

_start:
# mul - a3 = a1 * a2
# Caso 4
    li a1, 1234     # a1=0x000004D2, a2=0x00000000
    li a2, 0
    mul a3, a1, a2
    sw a3, 60(zero)
