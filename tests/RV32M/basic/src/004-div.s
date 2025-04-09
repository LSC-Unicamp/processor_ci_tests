# div implementation
.text

.global _start

_start:
# div
    li a1, 20
    li a2, 3
    div a3, a1, a2       # a3 = 20 / 3 = 6
    sw a3, 60(zero)
