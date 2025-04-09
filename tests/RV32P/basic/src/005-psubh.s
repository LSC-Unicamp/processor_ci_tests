.text
.global _start

_start:
    li a1, 0x00400040      # 2 halfwords: 0x0040 e 0x0040
    li a2, 0x00100010      # 2 halfwords: 0x0010 e 0x0010
    psubh a3, a1, a2       # subtração por halfword
    sw a3, 60(zero)
