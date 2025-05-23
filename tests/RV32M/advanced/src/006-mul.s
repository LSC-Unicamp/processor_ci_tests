.text
.global _start

_start:
# mul - a3 = a1 * a2
# Caso 6
    li a1, 4294967295     # a1=0xFFFFFFFF, a2=0x00000001
    li a2, 1
    mul a3, a1, a2
    sw a3, 60(zero)
