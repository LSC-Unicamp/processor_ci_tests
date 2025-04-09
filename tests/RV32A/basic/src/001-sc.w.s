# sc.w implementation
# sc.w implementation
.text
.global _start

_start:
    li t0, 0x2000
    li t1, 55
    sw t1, 0(t0)

    lr.w t2, (t0)
    li t3, 42
    sc.w t4, t3, (t0)   # t4 = 0 (success), t3 is written

    sw t4, 60(zero)     # Guarda se foi sucesso (0 = sucesso)
