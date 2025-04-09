# divu implementation
.text

.global _start

_start:
# divu
    li a1, 20
    li a2, 3
    divu a3, a1, a2      # a3 = 20 / 3 = 6 (unsigned)
    sw a3, 60(zero)
