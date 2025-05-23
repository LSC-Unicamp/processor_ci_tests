.text
.global _start

_start:
# mulh - a3 = high(a1 * a2 signed)
# Caso 18
    li a1, 5     # a1=0x00000005, a2=0x00000000
    li a2, 0
    mulh a3, a1, a2
    sw a3, 60(zero)
