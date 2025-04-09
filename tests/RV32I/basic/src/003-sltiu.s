# sltiu implementation
.text

.global _start;

_start:
    addi a1, zero, 8; # a1 = zero + 5

    sltiu a2, a1, 0x7FF; # a2 = a1 < 0xFFF

    sw a2, 60(zero);
