.text
.global _start

_start:
# rem - a3 = a1 % a2 (signed)
# Caso 62
    li a1, -1     # a1=0xFFFFFFFF, a2=0xFFFFFFFF
    li a2, -1
    rem a3, a1, a2
    sw a3, 60(zero)
