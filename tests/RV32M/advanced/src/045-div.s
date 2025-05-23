.text
.global _start

_start:
# div - a3 = a1 / a2 (signed)
# Caso 45 (divisão por zero)
    li a1, 0     # a1=0x00000000, a2=0x00000000
    li a2, 0
    div a3, a1, a2      # ERRO esperado: divisão por zero
    sw zero, 60(zero)
