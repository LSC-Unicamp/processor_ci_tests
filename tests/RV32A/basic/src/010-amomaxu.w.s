# amomaxu.w implementation
.text
.global _start

_start:
    li t0, 0x2000
    li t1, 123
    li t2, 200
    sw t1, 0(t0)

    amomaxu.w t3, t2, (t0)

    sw t3, 60(zero)
