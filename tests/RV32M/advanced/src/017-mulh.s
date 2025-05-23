.text
.global _start

_start:
# mulh - a3 = high(a1 * a2 signed)
# Caso 17
    li a1, 2147483648     # a1=0x80000000, a2=0x00000001
    li a2, 1
    mulh a3, a1, a2
    sw a3, 60(zero)
