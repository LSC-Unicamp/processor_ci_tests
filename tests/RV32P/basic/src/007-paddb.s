.text
.global _start

_start:
    li a1, 0x01020304      # bytes: 1,2,3,4
    li a2, 0x04030201      # bytes: 4,3,2,1
    paddb a3, a1, a2       # soma por byte
    sw a3, 60(zero)
