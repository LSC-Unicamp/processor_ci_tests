.text
.global _start

_start:
    li a0, 4
    vsetvli zero, a0, e32

    li t0, 10
    vmv.v.x v1, t0
    vmseq.vi v0, v1, 10       # Máscara onde v1 == 10

    vcompress.vm v2, v1, v0   # v2 = {10,10,10,10}
    li t1, 0x1000          # endereço base
    vs1r.v v2, (t1)   # Salva v3 na memória a partir do endereço em t1

