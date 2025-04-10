# lh implementation
.text

.global _start

_start:
    li a1, 0x6A6AFFFF

    sw a1, 40(zero);
    lh a2, 40(zero);

    sw a2, 60(zero);
