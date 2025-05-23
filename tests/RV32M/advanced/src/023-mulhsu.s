.text
.global _start

_start:
# mulhsu - a3 = high(signed a1 * unsigned a2)
# Caso 23
    li a1, 0     # a1=0x00000000, a2=0x000004D2
    li a2, 1234
    mulhsu a3, a1, a2
    sw a3, 60(zero)
