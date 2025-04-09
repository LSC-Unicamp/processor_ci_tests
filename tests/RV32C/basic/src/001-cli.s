# c.li (load immediate)
.text
.global _start

_start:
    c.li a0, 10           # a0 = 10
    sw a0, 60(zero)
