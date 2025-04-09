# mulhsu implementation
.text

.global _start

_start:
# mulhsu
    li a1, -3
    li a2, 2
    mulhsu a3, a1, a2    # a3 = high bits of -3 (signed) * 2 (unsigned)
    sw a3, 60(zero)
