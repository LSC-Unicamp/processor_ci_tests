# amoswap.w implementation
.text
.global _start

_start:
    li t0, 0x2000
    li t1, 10
    li t2, 42
    sw t1, 0(t0)

    amoswap.w t3, t2, (t0)   # troca t2 com Mem[t0]; t3 recebe antigo

    sw t3, 60(zero)
