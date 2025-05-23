.text
.global _start

_start:
# mulhsu - a3 = high(signed a1 * unsigned a2)
# Caso 24
    li a1, 1234     # a1=0x000004D2, a2=0x00000000
    li a2, 0
    mulhsu a3, a1, a2
    sw a3, 60(zero)
