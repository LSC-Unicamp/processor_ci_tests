# cj implementation
# c.j (jump)
.text
.globl _start

_start:
    c.j target

    li a0, 0xBAD  # se cair aqui, erro

    sw a0, 60(zero)

target:
    li a0, 0xC0DE
    sw a0, 60(zero)
