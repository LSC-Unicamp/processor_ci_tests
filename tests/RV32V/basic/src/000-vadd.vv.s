.text
.global _start

_start:
    li a0, 4
    vsetvli zero, a0, e32

    li t0, 10
    vmv.v.x v1, t0
    li t1, 20
    vmv.v.x v2, t1

    vadd.vv v3, v1, v2       # v3 = v1 + v2 = {30,30,30,30}
    li t1, 0x1000          # endereço base
    vs1r.v v3, (t1)   # Salva v3 na memória a partir do endereço em t1

