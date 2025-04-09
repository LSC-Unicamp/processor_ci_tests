.text
.global _start

_start:
    li a1, 6
    li a2, 7
    pmulh a3, a1, a2       # operação definida por extensão: parte alta
    sw a3, 60(zero)
