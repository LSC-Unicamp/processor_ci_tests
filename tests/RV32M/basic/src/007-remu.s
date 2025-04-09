# remu implementation
.text

.global _start

_start:
# remu
    li a1, 20
    li a2, 3
    remu a3, a1, a2      # a3 = 20 % 3 = 2 (unsigned)
    sw a3, 60(zero)
