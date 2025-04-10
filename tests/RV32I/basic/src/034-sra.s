# sra implementation
.text

.global _start;

_start:
    li a1, -2
    li a2, 1

    sra a3, a1, a2; # a3 = a1 >>> a2 // a3 = -2 >> 1 = -1

    sw a3, 60(zero);
    