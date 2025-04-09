# mulh implementation
.text

.global _start

_start:
# mulh
    li a1, -3
    li a2, 2
    mulh a3, a1, a2      # a3 = high bits of -3 * 2 (signed x signed)
    sw a3, 60(zero)
