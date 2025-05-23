.text
.global _start

_start:
# mulhsu - a3 = high(signed a1 * unsigned a2)
# Caso 26
    li a1, 4294967295     # a1=0xFFFFFFFF, a2=0x00000001
    li a2, 1
    mulhsu a3, a1, a2
    sw a3, 60(zero)
