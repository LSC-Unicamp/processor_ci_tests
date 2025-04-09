# slti implementation
.text

.global _start;

_start:
    addi a1, zero, 4; # a1 = zero + 4

    slti a3, a1, 1; # a3 = a1 < 1
    slti a4, a1, 5; # a4 = a1 < 5

    sw a3, 56(zero);
    sw a4, 60(zero);
    