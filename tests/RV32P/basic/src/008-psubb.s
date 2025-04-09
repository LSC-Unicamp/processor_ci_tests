.text
.global _start

_start:
    li a1, 0x08070605      # bytes: 8,7,6,5
    li a2, 0x01020304      # bytes: 1,2,3,4
    psubb a3, a1, a2       # subtração por byte
    sw a3, 60(zero)
