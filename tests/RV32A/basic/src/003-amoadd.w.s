# amoadd.w implementation
.text
.global _start

_start:
    li t0, 0x2000
    li t1, 20
    li t2, 22
    sw t1, 0(t0)

    amoadd.w t3, t2, (t0)   # t3 = old Mem[t0]; Mem[t0] += t2

    sw t3, 60(zero)
