.text
.global _start

_start:
    li a0, 4
    vsetvli zero, a0, e32

    li t0, 3
    vmv.v.x v1, t0
    li t1, 4
    vmv.v.x v2, t1

    vmul.vv v3, v1, v2       # v3 = {12,12,12,12}
    li t1, 0x1000          # endereço base
    vs1r.v v3, (t1)   # Salva v3 na memória a partir do endereço em t1

