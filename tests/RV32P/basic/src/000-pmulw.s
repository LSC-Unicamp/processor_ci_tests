.text
.global _start

_start:
    li a1, 6
    li a2, 7
    pmulw a3, a1, a2       # a3 = 6 * 7 = 42 (produto palavra)
    sw a3, 60(zero)
