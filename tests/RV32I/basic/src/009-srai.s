# srai implementation
.text

.global _start;

_start:
    li a1, -2; # a1 = -2

    srai a2, a1, 1; # a2 = a1 >>> 1 // a2 = -2 >> 1 = -1

    sw a2, 60(zero);
