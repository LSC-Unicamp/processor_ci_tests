# amoxor.w implementation
.text
.global _start

_start:
    li t0, 0x2000
    li t1, 0x0F
    li t2, 0xF0
    sw t1, 0(t0)

    amoxor.w t3, t2, (t0)

    sw t3, 60(zero)
