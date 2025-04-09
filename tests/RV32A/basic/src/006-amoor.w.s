# amoor.w implementation
.text
.global _start

_start:
    li t0, 0x2000
    li t1, 0xA0
    li t2, 0x0A
    sw t1, 0(t0)

    amoor.w t3, t2, (t0)

    sw t3, 60(zero)
