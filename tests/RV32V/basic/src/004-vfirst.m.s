.text
.global _start

_start:
    li a0, 8                     # VL = 8 elementos
    vsetvli zero, a0, e32

    # Preenche um vetor na memória com [0, 0, 42, 0, 0, 0, 0, 0]
    li t2, 0x2000                # Base dos dados
    li t3, 0
    sw t3, 0(t2)
    sw t3, 4(t2)
    li t4, 42
    sw t4, 8(t2)
    sw t3, 12(t2)
    sw t3, 16(t2)
    sw t3, 20(t2)
    sw t3, 24(t2)
    sw t3, 28(t2)

    # Carrega vetor para v1
    vle32.v v1, (t2)

    # Gera máscara: v1 == 42 → v0
    vmseq.vi v0, v1, 13

    # Encontra índice da primeira ocorrência
    vfirst.m t0, v0

    # Salva resultado
    li t5, 0x1000
    sw t0, 0(t5)
