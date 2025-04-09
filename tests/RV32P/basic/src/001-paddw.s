.text
.global _start

_start:
    li a1, 10
    li a2, 32
    paddw a3, a1, a2       # a3 = 10 + 32 = 42 (soma palavra)
    sw a3, 60(zero)
