# c.bnez - branch se diferente de zero (corrigido)
.text
.global _start

_start:
    li s1, 42          # s1 ≠ 0
    c.bnez s1, target  # válido: s1 está entre x8–x15

    li a0, 0xBAD       # erro, não devia chegar aqui
    sw a0, 60(zero)

target:
    li a0, 0xBEE       # sucesso
    sw a0, 60(zero)
