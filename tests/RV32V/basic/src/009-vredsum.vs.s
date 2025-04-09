.text
.global _start

_start:
    li a0, 4
    vsetvli zero, a0, e32

    li t0, 1

    vmv.v.x v1, t0
    vmv.v.x v2, zero

    vredsum.vs v3, v1, v2    # v3[0] = 4
    li t2, 0x1000          # endereço base
    vs1r.v v3, (t2)   # Salva v3 na memória a partir do endereço em t1

