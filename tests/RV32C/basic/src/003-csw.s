# c.sw - salvar valor na memória
.text
.globl _start

_start:
    li s0, 32          # base = endereço 32
    li s1, 5678        # dado
    c.sw s1, 0(s0)     # Mem[32] = s1
    lw a0, 0(s0)       # a0 = Mem[32]
    sw a0, 60(zero)    # salva a0 no endereço final
