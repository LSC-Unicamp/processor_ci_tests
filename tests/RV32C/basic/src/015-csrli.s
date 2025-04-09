# c.srli
.text
.global _start

_start:
    li a0, 8
    c.srli a0, 2          # a0 = a0 >> 2 = 2
    sw a0, 60(zero)
