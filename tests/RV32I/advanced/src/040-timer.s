# timer test
.set TIMER_ADDR, 0XFFFFFFF8;
.text

.global _start;

_start:
    addi a1, zero, 5; # a1 = zero + 5

    li a2, TIMER_ADDR;
    lw a3, 0(a2); # read timer value
    lw a4, 4(a2); # read timer value


    sw a2, 52(zero); # write timer value
    sw a3, 56(zero); # write timer value
    sw a4, 60(zero);
