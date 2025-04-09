# mulhu implementation
.text

.global _start

_start:
# mulhu
    li a1, 0xFFFFFFFF
    li a2, 2
    mulhu a3, a1, a2     # a3 = high bits of 0xFFFFFFFF * 2 (unsigned x unsigned)
    sw a3, 60(zero)
