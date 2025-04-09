# c.beqz - branch se for zero
.text
.global _start

_start:
    li s1, 0           # s1 = 0
    c.beqz s1, target  # salta se s1 == 0

    li a0, 0xBAD       # erro, não devia chegar aqui
    sw a0, 60(zero)

target:
    li a0, 0xBE0       # sucesso
    sw a0, 60(zero)
