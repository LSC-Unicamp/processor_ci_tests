.text
.global _start

_start:
# mulh - a3 = high(a1 * a2 signed)
# Caso 16
    li a1, 4294967295     # a1=0xFFFFFFFF, a2=0x00000001
    li a2, 1
    mulh a3, a1, a2
    sw a3, 60(zero)
