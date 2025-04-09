.text
.global _start

_start:
    li a0, 4
    vsetvli zero, a0, e32

    li t0, 5
    li t1, 7

    vmv.v.x v1, t0
    vmv.v.x v2, t1

    vmax.vv v4, v1, v2       # v4 = {7,7,7,7}

    li t2, 0x1000          # endereço base
    vs1r.v v4, (t2)   # Salva v4 na memória a partir do endereço em t1

