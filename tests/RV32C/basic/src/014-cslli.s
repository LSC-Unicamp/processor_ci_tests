# c.slli
.text
.global _start

_start:
    li a0, 2
    c.slli a0, 2          # a0 = a0 << 2 = 8
    sw a0, 60(zero)
