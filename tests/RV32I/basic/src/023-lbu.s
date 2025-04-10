# lbu implementation
.text

.global _start

_start:
    li a1, 0x6A6A6AFF

    sw a1, 40(zero);
    lbu a2, 40(zero);

    sw a2, 60(zero);
