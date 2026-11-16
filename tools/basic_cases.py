"""Dedicated basic instruction cases."""

import re

CASES = [
    ("RV32I", "addi", "rv32i", 12, "li t1, 5\naddi a0, t1, 7"),
    ("RV32I", "slti", "rv32i", 1, "li t1, -1\nslti a0, t1, 1"),
    ("RV32I", "sltiu", "rv32i", 0, "li t1, -1\nsltiu a0, t1, 1"),
    ("RV32I", "xori", "rv32i", 255, "li t1, 0x55\nxori a0, t1, 0xaa"),
    ("RV32I", "ori", "rv32i", 95, "li t1, 0x50\nori a0, t1, 0x0f"),
    ("RV32I", "andi", "rv32i", 10, "li t1, 0x5a\nandi a0, t1, 0x0f"),
    ("RV32I", "slli", "rv32i", 16, "li t1, 1\nslli a0, t1, 4"),
    ("RV32I", "srli", "rv32i", 1, "li t1, 0x80000000\nsrli a0, t1, 31"),
    ("RV32I", "srai", "rv32i", -1, "li t1, 0x80000000\nsrai a0, t1, 31"),
    ("RV32I", "lui", "rv32i", 0x12345000, "lui a0, 0x12345"),
    ("RV32I", "auipc", "rv32i", 0x80000000, "auipc a0, 0"),
    ("RV32I", "add", "rv32i", 12, "li t1, 5\nli t2, 7\nadd a0, t1, t2"),
    ("RV32I", "sub", "rv32i", -2, "li t1, 5\nli t2, 7\nsub a0, t1, t2"),
    ("RV32I", "sll", "rv32i", 16, "li t1, 1\nli t2, 4\nsll a0, t1, t2"),
    ("RV32I", "slt", "rv32i", 1, "li t1, -1\nli t2, 1\nslt a0, t1, t2"),
    ("RV32I", "sltu", "rv32i", 0, "li t1, -1\nli t2, 1\nsltu a0, t1, t2"),
    ("RV32I", "xor", "rv32i", 255, "li t1, 0x55\nli t2, 0xaa\nxor a0, t1, t2"),
    ("RV32I", "srl", "rv32i", 1, "li t1, 0x80000000\nli t2, 31\nsrl a0, t1, t2"),
    ("RV32I", "sra", "rv32i", -1, "li t1, 0x80000000\nli t2, 31\nsra a0, t1, t2"),
    ("RV32I", "or", "rv32i", 95, "li t1, 0x50\nli t2, 0x0f\nor a0, t1, t2"),
    ("RV32I", "and", "rv32i", 10, "li t1, 0x5a\nli t2, 0x0f\nand a0, t1, t2"),
    ("RV32I", "jal", "rv32i", 1, "jal ra, 1f\nli a0, 99\nj 2f\n1: li a0, 1\n2:"),
    ("RV32I", "jalr", "rv32i", 1, "la t1, 1f\njalr ra, 0(t1)\nli a0, 99\nj 2f\n1: li a0, 1\n2:"),
    ("RV32I", "beq", "rv32i", 1, "li t1, 1\nli t2, 1\nbeq t1, t2, 1f\nli a0, 99\nj 2f\n1: li a0, 1\n2:"),
    ("RV32I", "bne", "rv32i", 1, "li t1, 1\nli t2, 2\nbne t1, t2, 1f\nli a0, 99\nj 2f\n1: li a0, 1\n2:"),
    ("RV32I", "blt", "rv32i", 1, "li t1, -1\nli t2, 1\nblt t1, t2, 1f\nli a0, 99\nj 2f\n1: li a0, 1\n2:"),
    ("RV32I", "bge", "rv32i", 1, "li t1, 1\nli t2, -1\nbge t1, t2, 1f\nli a0, 99\nj 2f\n1: li a0, 1\n2:"),
    ("RV32I", "bltu", "rv32i", 1, "li t1, 1\nli t2, -1\nbltu t1, t2, 1f\nli a0, 99\nj 2f\n1: li a0, 1\n2:"),
    ("RV32I", "bgeu", "rv32i", 1, "li t1, -1\nli t2, 1\nbgeu t1, t2, 1f\nli a0, 99\nj 2f\n1: li a0, 1\n2:"),
    ("RV32I", "lb", "rv32i", -1, "la t1, data_word\nlb a0, 2(t1)"),
    ("RV32I", "lh", "rv32i", -32513, "la t1, data_word\nlh a0, 2(t1)"),
    ("RV32I", "lw", "rv32i", 0x80ff7f01, "la t1, data_word\nlw a0, 0(t1)"),
    ("RV32I", "lbu", "rv32i", 255, "la t1, data_word\nlbu a0, 2(t1)"),
    ("RV32I", "lhu", "rv32i", 33023, "la t1, data_word\nlhu a0, 2(t1)"),
    ("RV32I", "sb", "rv32i", 0x1234ab78, "la t1, scratch\nli t2, 0xab\nsb t2, 1(t1)\nlw a0, 0(t1)"),
    ("RV32I", "sh", "rv32i", 0x1234abcd, "la t1, scratch\nli t2, 0xabcd\nsh t2, 0(t1)\nlw a0, 0(t1)"),
    ("RV32I", "sw", "rv32i", 0xdeadbeef, "la t1, scratch\nli t2, 0xdeadbeef\nsw t2, 0(t1)\nlw a0, 0(t1)"),
    ("RV32I", "fence", "rv32i", 7, "li t1, 7\nfence rw, rw\naddi a0, t1, 0"),
    ("RV32M", "mul", "rv32im", 42, "li t1, 6\nli t2, 7\nmul a0, t1, t2"),
    ("RV32M", "mulh", "rv32im", -1, "li t1, -2\nli t2, 0x40000000\nmulh a0, t1, t2"),
    ("RV32M", "mulhsu", "rv32im", -1, "li t1, -2\nli t2, 0x80000000\nmulhsu a0, t1, t2"),
    ("RV32M", "mulhu", "rv32im", 1, "li t1, -1\nli t2, 2\nmulhu a0, t1, t2"),
    ("RV32M", "div", "rv32im", -2, "li t1, -13\nli t2, 5\ndiv a0, t1, t2"),
    ("RV32M", "divu", "rv32im", 2, "li t1, 13\nli t2, 5\ndivu a0, t1, t2"),
    ("RV32M", "rem", "rv32im", -3, "li t1, -13\nli t2, 5\nrem a0, t1, t2"),
    ("RV32M", "remu", "rv32im", 3, "li t1, 13\nli t2, 5\nremu a0, t1, t2"),
    ("RV32A", "lr.w", "rv32ia", 5, "la t1, atomic_word\nlr.w a0, (t1)"),
    ("RV32A", "sc.w", "rv32ia", 1, "la t1, atomic_word\nlr.w t2, (t1)\nli t3, 7\nsc.w t4, t3, (t1)\nbnez t4, 1f\nlw t5, 0(t1)\nli t6, 7\nbne t5, t6, failure\nli a0, 1\nj 2f\n1: lw t5, 0(t1)\nbne t5, t2, failure\nli a0, 1\n2:"),
    ("RV32A", "amoswap.w", "rv32ia", 5, "la t1, atomic_word\nli t2, 7\namoswap.w a0, t2, (t1)\nlw t3, 0(t1)\nli t4, 7\nbne t3, t4, failure"),
    ("RV32A", "amoadd.w", "rv32ia", 5, "la t1, atomic_word\nli t2, 7\namoadd.w a0, t2, (t1)\nlw t3, 0(t1)\nli t4, 12\nbne t3, t4, failure"),
    ("RV32A", "amoxor.w", "rv32ia", 5, "la t1, atomic_word\nli t2, 3\namoxor.w a0, t2, (t1)\nlw t3, 0(t1)\nli t4, 6\nbne t3, t4, failure"),
    ("RV32A", "amoand.w", "rv32ia", 5, "la t1, atomic_word\nli t2, 3\namoand.w a0, t2, (t1)\nlw t3, 0(t1)\nli t4, 1\nbne t3, t4, failure"),
    ("RV32A", "amoor.w", "rv32ia", 5, "la t1, atomic_word\nli t2, 2\namoor.w a0, t2, (t1)\nlw t3, 0(t1)\nli t4, 7\nbne t3, t4, failure"),
    ("RV32A", "amomin.w", "rv32ia", 5, "la t1, atomic_word\nli t2, -1\namomin.w a0, t2, (t1)\nlw t3, 0(t1)\nli t4, -1\nbne t3, t4, failure"),
    ("RV32A", "amomax.w", "rv32ia", 5, "la t1, atomic_word\nli t2, 7\namomax.w a0, t2, (t1)\nlw t3, 0(t1)\nli t4, 7\nbne t3, t4, failure"),
    ("RV32A", "amominu.w", "rv32ia", 5, "la t1, atomic_word\nli t2, 3\namominu.w a0, t2, (t1)\nlw t3, 0(t1)\nli t4, 3\nbne t3, t4, failure"),
    ("RV32A", "amomaxu.w", "rv32ia", 5, "la t1, atomic_word\nli t2, 7\namomaxu.w a0, t2, (t1)\nlw t3, 0(t1)\nli t4, 7\nbne t3, t4, failure"),
    ("RV32Zicsr", "csrrw", "rv32i_zicsr", 0, "csrrw zero, mscratch, zero\nli t1, 5\ncsrrw a0, mscratch, t1\ncsrr t2, mscratch\nbne t2, t1, failure"),
    ("RV32Zicsr", "csrrs", "rv32i_zicsr", 5, "li t1, 5\ncsrrw zero, mscratch, t1\nli t2, 2\ncsrrs a0, mscratch, t2\ncsrr t3, mscratch\nli t4, 7\nbne t3, t4, failure"),
    ("RV32Zicsr", "csrrc", "rv32i_zicsr", 7, "li t1, 7\ncsrrw zero, mscratch, t1\nli t2, 2\ncsrrc a0, mscratch, t2\ncsrr t3, mscratch\nli t4, 5\nbne t3, t4, failure"),
    ("RV32Zicsr", "csrrwi", "rv32i_zicsr", 0, "csrrw zero, mscratch, zero\ncsrrwi a0, mscratch, 5\ncsrr t2, mscratch\nli t3, 5\nbne t2, t3, failure"),
    ("RV32Zicsr", "csrrsi", "rv32i_zicsr", 5, "li t1, 5\ncsrrw zero, mscratch, t1\ncsrrsi a0, mscratch, 2\ncsrr t2, mscratch\nli t3, 7\nbne t2, t3, failure"),
    ("RV32Zicsr", "csrrci", "rv32i_zicsr", 7, "li t1, 7\ncsrrw zero, mscratch, t1\ncsrrci a0, mscratch, 2\ncsrr t2, mscratch\nli t3, 5\nbne t2, t3, failure"),
    ("RV32C", "c.nop", "rv32ic", 5, "li a0, 5\nc.nop"),
    ("RV32C", "c.addi", "rv32ic", 7, "li a0, 5\nc.addi a0, 2"),
    ("RV32C", "c.li", "rv32ic", 7, "c.li a0, 7"),
    ("RV32C", "c.lui", "rv32ic", 4096, "c.lui a0, 1"),
    ("RV32C", "c.slli", "rv32ic", 16, "li a0, 1\nc.slli a0, 4"),
    ("RV32C", "c.srli", "rv32ic", 4, "li s0, 16\nc.srli s0, 2\naddi a0, s0, 0"),
    ("RV32C", "c.srai", "rv32ic", -4, "li s0, -16\nc.srai s0, 2\naddi a0, s0, 0"),
    ("RV32C", "c.andi", "rv32ic", 3, "li s0, 7\nc.andi s0, 3\naddi a0, s0, 0"),
    ("RV32C", "c.mv", "rv32ic", 9, "li t1, 9\nc.mv a0, t1"),
    ("RV32C", "c.add", "rv32ic", 12, "li a0, 5\nli t1, 7\nc.add a0, t1"),
    ("RV32C", "c.sub", "rv32ic", 5, "li s0, 12\nli s1, 7\nc.sub s0, s1\naddi a0, s0, 0"),
    ("RV32C", "c.xor", "rv32ic", 15, "li s0, 5\nli s1, 10\nc.xor s0, s1\naddi a0, s0, 0"),
    ("RV32C", "c.or", "rv32ic", 15, "li s0, 5\nli s1, 10\nc.or s0, s1\naddi a0, s0, 0"),
    ("RV32C", "c.and", "rv32ic", 0, "li s0, 5\nli s1, 10\nc.and s0, s1\naddi a0, s0, 0"),
    ("RV32C", "c.j", "rv32ic", 1, "c.j 1f\nli a0, 99\nj 2f\n1: li a0, 1\n2:"),
    ("RV32C", "c.jal", "rv32ic", 1, "c.jal 1f\nli a0, 99\nj 2f\n1: li a0, 1\n2:"),
    ("RV32C", "c.jr", "rv32ic", 1, "la t1, 1f\nc.jr t1\nli a0, 99\nj 2f\n1: li a0, 1\n2:"),
    ("RV32C", "c.jalr", "rv32ic", 1, "la t1, 1f\nc.jalr t1\nli a0, 99\nj 2f\n1: li a0, 1\n2:"),
    ("RV32C", "c.beqz", "rv32ic", 1, "li s0, 0\nc.beqz s0, 1f\nli a0, 99\nj 2f\n1: li a0, 1\n2:"),
    ("RV32C", "c.bnez", "rv32ic", 1, "li s0, 1\nc.bnez s0, 1f\nli a0, 99\nj 2f\n1: li a0, 1\n2:"),
    ("RV32C", "c.lw", "rv32ic", 0x80ff7f01, "la s0, data_word\nc.lw s1, 0(s0)\naddi a0, s1, 0"),
    ("RV32C", "c.sw", "rv32ic", 7, "la s0, scratch\nli s1, 7\nc.sw s1, 0(s0)\nlw a0, 0(s0)"),
    ("RV32C", "c.lwsp", "rv32ic", 0x12345678, "la sp, scratch\nc.lwsp a0, 0(sp)"),
    ("RV32C", "c.swsp", "rv32ic", 7, "la sp, scratch\nli t1, 7\nc.swsp t1, 0(sp)\nlw a0, 0(sp)"),
    ("RV32C", "c.addi4spn", "rv32ic", 16, "la sp, scratch\nc.addi4spn s0, sp, 16\nsub a0, s0, sp"),
    ("RV32C", "c.addi16sp", "rv32ic", 16, "la t1, scratch\naddi sp, t1, 0\nc.addi16sp sp, 16\nsub a0, sp, t1"),
    ("RV32C", "c.flw", "rv32ifc_zicsr", 0x3f800000, "li t0, 0x6000\ncsrs mstatus, t0\nla s0, fp_word\nc.flw f8, 0(s0)\nfmv.x.w a0, f8"),
    ("RV32C", "c.fsw", "rv32ifc_zicsr", 0x3f800000, "li t0, 0x6000\ncsrs mstatus, t0\nla t1, fp_word\nflw f8, 0(t1)\nla s0, scratch\nc.fsw f8, 0(s0)\nlw a0, 0(s0)"),
    ("RV32C", "c.flwsp", "rv32ifc_zicsr", 0x3f800000, "li t0, 0x6000\ncsrs mstatus, t0\nla sp, fp_word\nc.flwsp f8, 0(sp)\nfmv.x.w a0, f8"),
    ("RV32C", "c.fswsp", "rv32ifc_zicsr", 0x3f800000, "li t0, 0x6000\ncsrs mstatus, t0\nla t1, fp_word\nflw f8, 0(t1)\nla sp, scratch\nc.fswsp f8, 0(sp)\nlw a0, 0(sp)"),
    ("RV32C", "c.fld", "rv32ifdc_zicsr", 0x89abcdef, "li t0, 0x6000\ncsrs mstatus, t0\nla s0, fp_double\nc.fld f8, 0(s0)\nla t1, scratch_double\nfsd f8, 0(t1)\nlw a0, 0(t1)\nlw t2, 4(t1)\nli t3, 0x01234567\nbne t2, t3, failure"),
    ("RV32C", "c.fsd", "rv32ifdc_zicsr", 0x89abcdef, "li t0, 0x6000\ncsrs mstatus, t0\nla t1, fp_double\nfld f8, 0(t1)\nla s0, scratch_double\nc.fsd f8, 0(s0)\nlw a0, 0(s0)\nlw t2, 4(s0)\nli t3, 0x01234567\nbne t2, t3, failure"),
    ("RV32C", "c.fldsp", "rv32ifdc_zicsr", 0x89abcdef, "li t0, 0x6000\ncsrs mstatus, t0\nla sp, fp_double\nc.fldsp f8, 0(sp)\nla t1, scratch_double\nfsd f8, 0(t1)\nlw a0, 0(t1)\nlw t2, 4(t1)\nli t3, 0x01234567\nbne t2, t3, failure"),
    ("RV32C", "c.fsdsp", "rv32ifdc_zicsr", 0x89abcdef, "li t0, 0x6000\ncsrs mstatus, t0\nla t1, fp_double\nfld f8, 0(t1)\nla sp, scratch_double\nc.fsdsp f8, 0(sp)\nlw a0, 0(sp)\nlw t2, 4(sp)\nli t3, 0x01234567\nbne t2, t3, failure"),
    ("RV32F", "flw", "rv32if_zicsr", 0x3f800000, "li t0, 0x6000\ncsrs mstatus, t0\nla t1, fp_word\nflw f8, 0(t1)\nfmv.x.w a0, f8"),
    ("RV32F", "fsw", "rv32if_zicsr", 0x3f800000, "li t0, 0x6000\ncsrs mstatus, t0\nla t1, fp_word\nflw f8, 0(t1)\nla t2, scratch\nfsw f8, 0(t2)\nlw a0, 0(t2)"),
    ("RV32F", "fadd.s", "rv32if_zicsr", 0x40400000, "li t0, 0x6000\ncsrs mstatus, t0\nla t1, fp_word\nflw f8, 0(t1)\nla t1, fp_two\nflw f9, 0(t1)\nfadd.s f10, f8, f9\nfmv.x.w a0, f10"),
    ("RV32F", "fsub.s", "rv32if_zicsr", 0x3f800000, "li t0, 0x6000\ncsrs mstatus, t0\nla t1, fp_word\nflw f8, 0(t1)\nla t1, fp_two\nflw f9, 0(t1)\nfsub.s f10, f9, f8\nfmv.x.w a0, f10"),
    ("RV32F", "fmul.s", "rv32if_zicsr", 0x40800000, "li t0, 0x6000\ncsrs mstatus, t0\nla t1, fp_two\nflw f8, 0(t1)\nfmul.s f10, f8, f8\nfmv.x.w a0, f10"),
    ("RV32F", "fdiv.s", "rv32if_zicsr", 0x40000000, "li t0, 0x6000\ncsrs mstatus, t0\nla t1, fp_word\nflw f8, 0(t1)\nla t1, fp_two\nflw f9, 0(t1)\nfdiv.s f10, f9, f8\nfmv.x.w a0, f10"),
    ("RV32F", "fsqrt.s", "rv32if_zicsr", 0x40000000, "li t0, 0x6000\ncsrs mstatus, t0\nla t1, fp_four\nflw f8, 0(t1)\nfsqrt.s f10, f8\nfmv.x.w a0, f10"),
    ("RV32F", "fmv.x.w", "rv32if_zicsr", 0x3f800000, "li t0, 0x6000\ncsrs mstatus, t0\nla t1, fp_word\nflw f8, 0(t1)\nfmv.x.w a0, f8"),
    ("RV64I", "addiw", "rv64i", 0, "li t1, -1\naddiw a0, t1, 1"),
    ("RV64I", "slliw", "rv64i", -2147483648, "li t1, 1\nslliw a0, t1, 31"),
    ("RV64I", "srliw", "rv64i", 1, "li t1, 0x80000000\nsrliw a0, t1, 31"),
    ("RV64I", "sraiw", "rv64i", -1, "li t1, 0x80000000\nsraiw a0, t1, 31"),
    ("RV64I", "addw", "rv64i", -2147483648, "li t1, 0x7fffffff\nli t2, 1\naddw a0, t1, t2"),
    ("RV64I", "subw", "rv64i", -1, "li t1, 0\nli t2, 1\nsubw a0, t1, t2"),
    ("RV64I", "sllw", "rv64i", -2147483648, "li t1, 1\nli t2, 31\nsllw a0, t1, t2"),
    ("RV64I", "srlw", "rv64i", 1, "li t1, 0x80000000\nli t2, 31\nsrlw a0, t1, t2"),
    ("RV64I", "sraw", "rv64i", -1, "li t1, 0x80000000\nli t2, 31\nsraw a0, t1, t2"),
    ("RV64I", "lwu", "rv64i", 0x80ff7f01, "la t1, data_word\nlwu a0, 0(t1)"),
    ("RV64I", "ld", "rv64i", 0x0123456789abcdef, "la t1, fp_double\nld a0, 0(t1)"),
    ("RV64I", "sd", "rv64i", 0x0123456789abcdef, "li t1, 0x0123456789abcdef\nla t2, scratch_double\nsd t1, 0(t2)\nld a0, 0(t2)"),
    ("RV64M", "mulw", "rv64im", 42, "li t1, 6\nli t2, 7\nmulw a0, t1, t2"),
    ("RV64M", "divw", "rv64im", -2, "li t1, -13\nli t2, 5\ndivw a0, t1, t2"),
    ("RV64M", "divuw", "rv64im", 2, "li t1, 13\nli t2, 5\ndivuw a0, t1, t2"),
    ("RV64M", "remw", "rv64im", -3, "li t1, -13\nli t2, 5\nremw a0, t1, t2"),
    ("RV64M", "remuw", "rv64im", 3, "li t1, 13\nli t2, 5\nremuw a0, t1, t2"),
    ("RV64A", "lr.d", "rv64ia", 5, "la t1, atomic_double\nlr.d a0, (t1)"),
    ("RV64A", "sc.d", "rv64ia", 1, "la t1, atomic_double\nlr.d t2, (t1)\nli t3, 7\nsc.d t4, t3, (t1)\nbnez t4, 1f\nld t5, 0(t1)\nli t6, 7\nbne t5, t6, failure\nli a0, 1\nj 2f\n1: ld t5, 0(t1)\nbne t5, t2, failure\nli a0, 1\n2:"),
    ("RV64A", "amoswap.d", "rv64ia", 5, "la t1, atomic_double\nli t2, 7\namoswap.d a0, t2, (t1)\nld t3, 0(t1)\nli t4, 7\nbne t3, t4, failure"),
    ("RV64A", "amoadd.d", "rv64ia", 5, "la t1, atomic_double\nli t2, 7\namoadd.d a0, t2, (t1)\nld t3, 0(t1)\nli t4, 12\nbne t3, t4, failure"),
    ("RV64A", "amoxor.d", "rv64ia", 5, "la t1, atomic_double\nli t2, 3\namoxor.d a0, t2, (t1)\nld t3, 0(t1)\nli t4, 6\nbne t3, t4, failure"),
    ("RV64A", "amoand.d", "rv64ia", 5, "la t1, atomic_double\nli t2, 3\namoand.d a0, t2, (t1)\nld t3, 0(t1)\nli t4, 1\nbne t3, t4, failure"),
    ("RV64A", "amoor.d", "rv64ia", 5, "la t1, atomic_double\nli t2, 2\namoor.d a0, t2, (t1)\nld t3, 0(t1)\nli t4, 7\nbne t3, t4, failure"),
    ("RV64A", "amomin.d", "rv64ia", 5, "la t1, atomic_double\nli t2, -1\namomin.d a0, t2, (t1)\nld t3, 0(t1)\nli t4, -1\nbne t3, t4, failure"),
    ("RV64A", "amomax.d", "rv64ia", 5, "la t1, atomic_double\nli t2, 7\namomax.d a0, t2, (t1)\nld t3, 0(t1)\nli t4, 7\nbne t3, t4, failure"),
    ("RV64A", "amominu.d", "rv64ia", 5, "la t1, atomic_double\nli t2, 3\namominu.d a0, t2, (t1)\nld t3, 0(t1)\nli t4, 3\nbne t3, t4, failure"),
    ("RV64A", "amomaxu.d", "rv64ia", 5, "la t1, atomic_double\nli t2, 7\namomaxu.d a0, t2, (t1)\nld t3, 0(t1)\nli t4, 7\nbne t3, t4, failure"),
]

_FP_SETUP = "li t0, 0x6000\ncsrs mstatus, t0\nla t1, fp_word\nflw f8, 0(t1)\nla t1, fp_two\nflw f9, 0(t1)\n"
_F_CASES = [
    ("fmadd.s", 0x40400000, "fmadd.s f10, f8, f9, f8", True),
    ("fmsub.s", 0x40400000, "fmsub.s f10, f9, f9, f8", True),
    ("fnmsub.s", 0xc0400000, "fnmsub.s f10, f9, f9, f8", True),
    ("fnmadd.s", 0xc0a00000, "fnmadd.s f10, f9, f9, f8", True),
    ("fsgnj.s", 0x3f800000, "fsgnj.s f10, f8, f9", True),
    ("fsgnjn.s", 0xbf800000, "fsgnjn.s f10, f8, f9", True),
    ("fsgnjx.s", 0x3f800000, "fsgnjx.s f10, f8, f9", True),
    ("fmin.s", 0x3f800000, "fmin.s f10, f8, f9", True),
    ("fmax.s", 0x40000000, "fmax.s f10, f8, f9", True),
    ("fcvt.w.s", 2, "fcvt.w.s a0, f9", False),
    ("fcvt.wu.s", 2, "fcvt.wu.s a0, f9", False),
    ("feq.s", 1, "feq.s a0, f8, f8", False),
    ("flt.s", 1, "flt.s a0, f8, f9", False),
    ("fle.s", 1, "fle.s a0, f8, f9", False),
    ("fclass.s", 64, "fclass.s a0, f8", False),
    ("fcvt.s.w", 0x40000000, "li t2, 2\nfcvt.s.w f10, t2", True),
    ("fcvt.s.wu", 0x40000000, "li t2, 2\nfcvt.s.wu f10, t2", True),
    ("fmv.w.x", 0x3f800000, "li t2, 0x3f800000\nfmv.w.x f10, t2", True),
]
for _target, _expected, _operation, _raw in _F_CASES:
    CASES.append(("RV32F", _target, "rv32if_zicsr", _expected,
                  _FP_SETUP + _operation + ("\nfmv.x.w a0, f10" if _raw else "")))

_D_SETUP = ("li t0, 0x6000\ncsrs mstatus, t0\n"
            "la t1, double_one\nfld f8, 0(t1)\n"
            "la t1, double_two\nfld f9, 0(t1)\n"
            "la t1, double_four\nfld f11, 0(t1)\n")
_D_CASES = [
    ("fld", 0x3ff0000000000000, "la t1, double_one\nfld f10, 0(t1)", "double"),
    ("fsd", 0x3ff0000000000000, "la t1, scratch_double\nfsd f8, 0(t1)", "stored"),
    ("fmadd.d", 0x4008000000000000, "fmadd.d f10, f8, f9, f8", "double"),
    ("fmsub.d", 0x4008000000000000, "fmsub.d f10, f9, f9, f8", "double"),
    ("fnmsub.d", 0xc008000000000000, "fnmsub.d f10, f9, f9, f8", "double"),
    ("fnmadd.d", 0xc014000000000000, "fnmadd.d f10, f9, f9, f8", "double"),
    ("fadd.d", 0x4008000000000000, "fadd.d f10, f8, f9", "double"),
    ("fsub.d", 0x3ff0000000000000, "fsub.d f10, f9, f8", "double"),
    ("fmul.d", 0x4010000000000000, "fmul.d f10, f9, f9", "double"),
    ("fdiv.d", 0x4000000000000000, "fdiv.d f10, f9, f8", "double"),
    ("fsqrt.d", 0x4000000000000000, "fsqrt.d f10, f11", "double"),
    ("fsgnj.d", 0x3ff0000000000000, "fsgnj.d f10, f8, f9", "double"),
    ("fsgnjn.d", 0xbff0000000000000, "fsgnjn.d f10, f8, f9", "double"),
    ("fsgnjx.d", 0x3ff0000000000000, "fsgnjx.d f10, f8, f9", "double"),
    ("fmin.d", 0x3ff0000000000000, "fmin.d f10, f8, f9", "double"),
    ("fmax.d", 0x4000000000000000, "fmax.d f10, f8, f9", "double"),
    ("fcvt.s.d", 0x40000000, "fcvt.s.d f10, f9", "single"),
    ("fcvt.d.s", 0x3ff0000000000000, "la t1, fp_word\nflw f12, 0(t1)\nfcvt.d.s f10, f12", "double"),
    ("feq.d", 1, "feq.d a0, f8, f8", "integer"),
    ("flt.d", 1, "flt.d a0, f8, f9", "integer"),
    ("fle.d", 1, "fle.d a0, f8, f9", "integer"),
    ("fclass.d", 64, "fclass.d a0, f8", "integer"),
    ("fcvt.w.d", 2, "fcvt.w.d a0, f9", "integer"),
    ("fcvt.wu.d", 2, "fcvt.wu.d a0, f9", "integer"),
    ("fcvt.d.w", 0x4000000000000000, "li t2, 2\nfcvt.d.w f10, t2", "double"),
    ("fcvt.d.wu", 0x4000000000000000, "li t2, 2\nfcvt.d.wu f10, t2", "double"),
]
for _target, _expected, _operation, _kind in _D_CASES:
    _body = _D_SETUP + _operation
    if _kind in ("double", "stored"):
        if _kind == "double":
            _body += "\nla t1, scratch_double\nfsd f10, 0(t1)"
        _body += (f"\nlw a0, 0(t1)\nlw t2, 4(t1)\n"
                  f"li t3, {(_expected >> 32) & 0xffffffff}\nbne t2, t3, failure")
        _result = _expected & 0xffffffff
    elif _kind == "single":
        _body += "\nfmv.x.w a0, f10"
        _result = _expected
    else:
        _result = _expected
    CASES.append(("RV32D", _target, "rv32ifd_zicsr", _result, _body))

_RV64_F_CASES = [
    ("fcvt.l.s", 2, "fcvt.l.s a0, f9", False),
    ("fcvt.lu.s", 2, "fcvt.lu.s a0, f9", False),
    ("fcvt.s.l", 0x40000000, "li t2, 2\nfcvt.s.l f10, t2", True),
    ("fcvt.s.lu", 0x40000000, "li t2, 2\nfcvt.s.lu f10, t2", True),
]
for _target, _expected, _operation, _raw in _RV64_F_CASES:
    CASES.append(("RV64F", _target, "rv64if_zicsr", _expected,
                  _FP_SETUP + _operation + ("\nfmv.x.w a0, f10" if _raw else "")))

_RV64_D_CASES = [
    ("fcvt.l.d", 2, "fcvt.l.d a0, f9", "integer"),
    ("fcvt.lu.d", 2, "fcvt.lu.d a0, f9", "integer"),
    ("fmv.x.d", 0x3ff0000000000000, "fmv.x.d a0, f8", "integer"),
    ("fcvt.d.l", 0x4000000000000000, "li t2, 2\nfcvt.d.l f10, t2", "double"),
    ("fcvt.d.lu", 0x4000000000000000, "li t2, 2\nfcvt.d.lu f10, t2", "double"),
    ("fmv.d.x", 0x3ff0000000000000, "li t2, 0x3ff0000000000000\nfmv.d.x f10, t2", "double"),
]
for _target, _expected, _operation, _kind in _RV64_D_CASES:
    _body = _D_SETUP + _operation
    if _kind == "double":
        _body += (f"\nla t1, scratch_double\nfsd f10, 0(t1)"
                  f"\nlw a0, 0(t1)\nlw t3, 4(t1)\n"
                  f"li t4, {(_expected >> 32) & 0xffffffff}\nbne t3, t4, failure")
        _result = _expected & 0xffffffff
    else:
        _result = _expected
    CASES.append(("RV64D", _target, "rv64ifd_zicsr", _result, _body))


def source(case: tuple) -> str:
    group, target, march, expected, body = case
    mask = (1 << (64 if group.startswith("RV64") else 32)) - 1
    whole_group = re.match(r"(?:vl|vs|vmv)([1248])(?:re|r)", target)
    vector_span = max(1024, int(whole_group.group(1)) * 8192) if whole_group else 1024
    vector_data = (f"vector_blob: .word 7\n.space {vector_span - 4}\n"
                   f"vector_store: .space {vector_span}\n") if group.startswith(("RV32Zve", "RV64Zve")) else ""
    return f'''# Dedicated {group} basic test for {target}; ISA {march}
# Initialized operands in body. Expected a0 = {expected & mask:#x}.
.section .text
.global _start
_start:
{body}
li t0, {expected}
bne a0, t0, failure
li t1, 1
j report
failure:
li t1, 3
report:
la t2, tohost
sw t1, 0(t2)
sw zero, 4(t2)
1: j 1b
.section .tohost,"aw",@progbits
.balign 8
.global tohost
tohost: .dword 0
.global fromhost
fromhost: .dword 0
.section .data
.balign 4
data_word: .word 0x80ff7f01
scratch: .word 0x12345678
atomic_word: .word 5
vector_words: .word 0x80ff7f01, 2, 3, 4
vector_scratch: .word 0, 0, 0, 0
{vector_data}.balign 8
fp_double: .dword 0x0123456789abcdef
scratch_double: .dword 0
fp_word: .word 0x3f800000
fp_two: .word 0x40000000
fp_four: .word 0x40800000
.balign 8
atomic_double: .dword 5
double_one: .dword 0x3ff0000000000000
double_two: .dword 0x4000000000000000
double_four: .dword 0x4010000000000000
'''


from extension_cases import CASES as EXTENSION_CASES
from vector_higher_cases import CASES as HIGHER_VECTOR_CASES
from vector_fp_cases import CASES as VECTOR_FP_CASES

CASES.extend(EXTENSION_CASES)
CASES.extend(HIGHER_VECTOR_CASES)
CASES.extend(VECTOR_FP_CASES)
