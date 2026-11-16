# ProcessorCI controller timer: lower 32 bits at 0xfffffffc.
# A later read must advance. Unsigned subtraction also handles counter wrap.
.text
.global _start
_start:
    li t0, -4
    lw t1, 0(t0)
    addi zero, zero, 0
    lw t2, 0(t0)
    sub t3, t2, t1
    sltu t4, zero, t3
    sw t4, 60(zero)
