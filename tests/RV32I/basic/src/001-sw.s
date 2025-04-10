# sw implementation
.text

.global _start

_start:
    addi a1, zero, 10      # Carrega o primeiro número (10) em a1

    sw a1, 60(zero)
