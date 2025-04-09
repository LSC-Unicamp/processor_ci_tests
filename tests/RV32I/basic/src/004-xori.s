# xori implementation
.text

.global _start;

_start:
    addi a1, zero, 5; # a1 = zero + 5
    
    xori a3, a1, 3;  # a3 = a1 ^ 3 = 5 ^ 3 = 6

    sw a3, 60(zero);
    