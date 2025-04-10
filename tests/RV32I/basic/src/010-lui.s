# lui implementation
.text

.global _start;

_start:
    lui a1, 0x6A6A6; # a1 = 446464

    sw a1, 60(zero);
