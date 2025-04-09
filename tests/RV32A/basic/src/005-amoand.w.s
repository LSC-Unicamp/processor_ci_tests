# amoand.w implementation
.text
.global _start

_start:
    li t0, 0x2000
    li t1, 0xFF
    li t2, 0x0F
    sw t1, 0(t0)

    amoand.w t3, t2, (t0)

    sw t3, 60(zero)
