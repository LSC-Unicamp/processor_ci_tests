.text
.global _start

_start:
# remu - a3 = a1 % a2 (unsigned)
# Caso 74 (divisão por zero)
    li a1, 1234     # a1=0x000004D2, a2=0x00000000
    li a2, 0
    remu a3, a1, a2      # ERRO esperado: divisão por zero
    sw zero, 60(zero)
