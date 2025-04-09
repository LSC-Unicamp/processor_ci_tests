# c.lw - carregar valor da memória
.text
.global _start

_start:
    li s0, 32          # base = endereço 32
    li t0, 1234
    sw t0, 0(s0)       # escreve 1234 no endereço 32
    c.lw s1, 0(s0)     # carrega da base s0 para s1
    sw s1, 60(zero)    # salva em 60(zero)
