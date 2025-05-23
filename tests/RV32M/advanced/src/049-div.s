.text
.global _start

_start:
# div - a3 = a1 / a2 (signed)
# Caso 49
    li a1, 0     # a1=0x00000000, a2=0x00000005
    li a2, 5
    div a3, a1, a2
    sw a3, 60(zero)
