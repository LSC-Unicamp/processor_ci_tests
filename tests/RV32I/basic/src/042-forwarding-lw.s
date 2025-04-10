.global _start

_start:
    addi a1, zero, 10      # Carrega o primeiro número (10) em a1
    addi a2, zero, 20      # Carrega o segundo número (20) em a2

    add a3, a1, a2       # Soma a1 e a2, armazena o resultado em a3 - 
                          # a3 = 10 + 20 = 30
    
    sw a3, 40(zero)

    addi a4, zero, 1     # Carrega o número 1 em a4

    lw a5, 40(zero)   # Carrega o valor de a3 (30) em a5 
    
    add a5, a5, a4

    sw a5, 60(zero)