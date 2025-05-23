.text
.global _start

_start:
# mulhsu - a3 = high(signed a1 * unsigned a2)
# Caso 29
    li a1, 0     # a1=0x00000000, a2=0x00000005
    li a2, 5
    mulhsu a3, a1, a2
    sw a3, 60(zero)
