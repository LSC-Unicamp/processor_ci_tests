# sb implementation
.text

.global _start

_start:
    li a1, 0x6A6ACADE
    
    sb a1, 48(zero);

    lw a2, 48(zero);

    sw a2, 60(zero);
