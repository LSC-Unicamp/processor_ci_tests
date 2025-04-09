# cjjal implementation
# c.jal (jump and link) – somente RV32
.text
.globl _start

_start:
    c.jal target

    li a0, 0xBAD  # se cair aqui, erro
    sw a0, 60(zero)

target:
    li a0, 0xFACE
    sw a0, 60(zero)
