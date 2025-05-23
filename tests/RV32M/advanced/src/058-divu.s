.text
.global _start

_start:
# divu - a3 = a1 / a2 (unsigned)
# Caso 58 (divisão por zero)
    li a1, 5     # a1=0x00000005, a2=0x00000000
    li a2, 0
    divu a3, a1, a2      # ERRO esperado: divisão por zero
    sw zero, 60(zero)
