.text
.global _start

_start:
    li a1, 0x00100010      # 2 halfwords: 0x0010 e 0x0010
    li a2, 0x00200012      # 2 halfwords: 0x0020 e 0x0012
    paddh a3, a1, a2       # soma por halfword
    sw a3, 60(zero)
