# c.srai
.text
.global _start

_start:
    li a0, -8
    c.srai a0, 2          # a0 = a0 >> 2 (arith) = -2
    sw a0, 60(zero)
