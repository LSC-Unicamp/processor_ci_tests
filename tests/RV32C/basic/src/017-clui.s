# c.lui (load upper immediate)
.text
.global _start

_start:
    c.lui a0, 1           # a0 = 0x1000 (para registros x8–x15)
    sw a0, 60(zero)
