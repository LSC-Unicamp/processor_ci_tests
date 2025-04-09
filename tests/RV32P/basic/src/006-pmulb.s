.text
.global _start

_start:
    li a1, 0x04040404      # 4 bytes: 4,4,4,4
    li a2, 0x03030303      # 4 bytes: 3,3,3,3
    pmulb a3, a1, a2       # multiplicação por byte
    sw a3, 60(zero)
