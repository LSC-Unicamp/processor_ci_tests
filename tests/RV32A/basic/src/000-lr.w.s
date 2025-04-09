# lr.w implementation
# lr.w implementation
.text
.global _start

_start:
    li t0, 0x2000
    li t1, 123
    sw t1, 0(t0)

    lr.w t2, (t0)       # t2 = Mem[0x2000]
    sw t2, 60(zero)
