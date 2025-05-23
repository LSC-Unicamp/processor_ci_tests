.text
.global _start

_start:
# rem - a3 = a1 % a2 (signed)
# Caso 63
    li a1, 0     # a1=0x00000000, a2=0x000004D2
    li a2, 1234
    rem a3, a1, a2
    sw a3, 60(zero)
