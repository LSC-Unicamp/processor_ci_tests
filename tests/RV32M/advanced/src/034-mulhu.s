.text
.global _start

_start:
# mulhu - a3 = high(a1 * a2 unsigned)
# Caso 34
    li a1, 1234     # a1=0x000004D2, a2=0x00000000
    li a2, 0
    mulhu a3, a1, a2
    sw a3, 60(zero)
