.text
.global _start

_start:
    li a0, 4
    vsetvli zero, a0, e32

    li t0, 10

    vmv.v.x v1, t0
    li t1, 1

    vslidedown.vx v3, v1, t1    # v3 = {10,10,10,0}

    li t2, 0x1000          # endereço base

    vs1r.v v3, (t2)   # Salva v3 na memória a partir do endereço em t1

