# xor implementation
.text

.global _start;

_start:
    addi a1, zero, 5; # a1 = zero + 5
    addi a2, zero, 3; # a2 = zero + 3
    
    xor a3, a1, a2; # a3 = a1 ^ a2 // a3 = 5 ^ 3 = 6

    sw a3, 60(zero);
    