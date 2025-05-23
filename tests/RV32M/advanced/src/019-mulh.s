.text
.global _start

_start:
# mulh - a3 = high(a1 * a2 signed)
# Caso 19
    li a1, 0     # a1=0x00000000, a2=0x00000005
    li a2, 5
    mulh a3, a1, a2
    sw a3, 60(zero)
