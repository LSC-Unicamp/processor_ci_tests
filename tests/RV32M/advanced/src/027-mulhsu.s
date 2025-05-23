.text
.global _start

_start:
# mulhsu - a3 = high(signed a1 * unsigned a2)
# Caso 27
    li a1, 2147483648     # a1=0x80000000, a2=0x00000001
    li a2, 1
    mulhsu a3, a1, a2
    sw a3, 60(zero)
