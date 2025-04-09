# rem implementation
.text

.global _start

_start:
# rem
    li a1, 20
    li a2, 3
    rem a3, a1, a2       # a3 = 20 % 3 = 2
    sw a3, 60(zero)
