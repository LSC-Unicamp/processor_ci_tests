.text
.global _start

_start:
# mulhu - a3 = high(a1 * a2 unsigned)
# Caso 38
    li a1, 5     # a1=0x00000005, a2=0x00000000
    li a2, 0
    mulhu a3, a1, a2
    sw a3, 60(zero)
