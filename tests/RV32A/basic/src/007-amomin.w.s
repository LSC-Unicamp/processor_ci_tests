# amomin.w implementation
.text
.global _start

_start:
    li t0, 0x2000
    li t1, -1
    li t2, 42
    sw t1, 0(t0)

    amomin.w t3, t2, (t0)

    sw t3, 60(zero)
