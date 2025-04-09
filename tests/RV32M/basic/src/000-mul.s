# mul implementation
.text
.global _start

_start:
    li a1, 6
    li a2, 7
    mul a3, a1, a2       # a3 = 6 * 7 = 42
    sw a3, 60(zero)
