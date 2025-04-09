.text
.global _start

_start:
    li a0, 8
    vsetvli zero, a0, e32

    vmv.v.x v1, t0
    vmseq.vi v0, v1, 15       # Máscara: 1 onde v1 == 42

    vpopc.m t0, v0            # t0 = número de elementos igual a 42
    li t2, 0x1000          # endereço base
    sw t0, 0(t1)
