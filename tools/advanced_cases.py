"""Deterministic advanced scenarios; each entry has a distinct architectural check."""

CASES = [
    ("alu_raw", "dependencies", "rv32i", 15, "li t1, 7\naddi t2, t1, 1\nadd a0, t2, t1"),
    ("alu_chain", "dependencies", "rv32i", 31, "li t1, 1\naddi t1, t1, 2\nslli t1, t1, 3\naddi a0, t1, 7"),
    ("alu_gap", "dependencies", "rv32i", 19, "li t1, 9\naddi t1, t1, 10\nli t2, 4\nadd a0, t1, zero"),
    ("same_register_writes", "dependencies", "rv32i", 23, "li t1, 3\naddi t1, t1, 5\naddi t1, t1, 15\nadd a0, t1, zero"),
    ("two_writers_consumer", "dependencies", "rv32i", 14, "li t1, 7\nli t2, 11\naddi t1, t2, 3\nadd a0, t1, zero"),
    ("load_use", "dependencies", "rv32i", 22, "la t1, data_word\nlw t2, 0(t1)\naddi a0, t2, 17"),
    ("alu_store_data", "dependencies", "rv32i", 13, "la t1, scratch\nli t2, 5\naddi t2, t2, 8\nsw t2, 0(t1)\nlw a0, 0(t1)"),
    ("alu_store_address", "dependencies", "rv32i", 9, "la t1, scratch\naddi t2, t1, 4\nli t3, 9\nsw t3, 0(t2)\nlw a0, 4(t1)"),
    ("load_branch", "dependencies", "rv32i", 1, "la t1, data_word\nlw t2, 0(t1)\nli a0, 0\nbeq t2, zero, 1f\nli a0, 1\n1:"),
    ("mul_consumer", "dependencies", "rv32im", 43, "li t1, 6\nli t2, 7\nmul t3, t1, t2\naddi a0, t3, 1"),
    ("div_consumer", "dependencies", "rv32im", 9, "li t1, 43\nli t2, 5\ndiv t3, t1, t2\naddi a0, t3, 1"),
    ("branch_taken", "control_flow", "rv32i", 7, "li t1, 2\nli a0, 7\nbeq t1, t1, 1f\nli a0, 99\n1:"),
    ("branch_not_taken", "control_flow", "rv32i", 8, "li t1, 2\nli t2, 3\nli a0, 8\nbeq t1, t2, 1f\nj 2f\n1: li a0, 99\n2:"),
    ("consecutive_branches", "control_flow", "rv32i", 12, "li t1, 2\nli a0, 12\nbeq t1, zero, 1f\nbne t1, zero, 2f\n1: li a0, 99\n2:"),
    ("backward_branch", "control_flow", "rv32i", 5, "li t1, 0\nli t2, 5\n1: addi t1, t1, 1\nblt t1, t2, 1b\nadd a0, t1, zero"),
    ("jal_chain", "control_flow", "rv32i", 17, "li a0, 0\njal ra, 1f\nj 3f\n1: addi a0, a0, 7\njal t1, 2f\n2: addi a0, a0, 10\n3:"),
    ("jalr_chain", "control_flow", "rv32i", 4, "la t1, 1f\njalr ra, 0(t1)\nli a0, 99\n1: li a0, 4"),
    ("wrong_path_register", "control_flow", "rv32i", 6, "li a0, 6\nli t1, 1\nbeq t1, t1, 1f\nli a0, 99\n1:"),
    ("wrong_path_store", "control_flow", "rv32i", 0x55, "la t1, scratch\nli t2, 0x55\nsw t2, 0(t1)\nbeq t2, t2, 1f\nsw zero, 0(t1)\n1: lw a0, 0(t1)"),
    ("store_load", "memory", "rv32i", 39, "la t1, scratch\nli t2, 39\nsw t2, 0(t1)\nlw a0, 0(t1)"),
    ("repeated_stores", "memory", "rv32i", 3, "la t1, scratch\nli t2, 1\nsw t2, 0(t1)\nli t2, 3\nsw t2, 0(t1)\nlw a0, 0(t1)"),
    ("overlap_bytes", "memory", "rv32i", 0x1234ab78, "la t1, scratch\nli t2, 0x12345678\nsw t2, 0(t1)\nli t2, 0xab\nsb t2, 1(t1)\nlw a0, 0(t1)"),
    ("signed_unsigned_load", "memory", "rv32i", 256, "la t1, scratch\nli t2, 255\nsb t2, 0(t1)\nlb t3, 0(t1)\nlbu t4, 0(t1)\nsub a0, t4, t3"),
    ("partial_halfword", "memory", "rv32i", 0x3344abcd, "la t1, scratch\nli t2, 0x33445566\nsw t2, 0(t1)\nli t2, 0xabcd\nsh t2, 0(t1)\nlw a0, 0(t1)"),
    ("memory_branch_gap", "memory", "rv32i", 11, "la t1, scratch\nli t2, 11\nsw t2, 0(t1)\nbeq zero, zero, 1f\nsw zero, 0(t1)\n1: lw a0, 0(t1)"),
    ("wraparound", "arithmetic", "rv32i", 0, "li t1, -1\naddi a0, t1, 1"),
    ("signed_unsigned_compare", "arithmetic", "rv32i", 1, "li t1, -1\nli t2, 1\nslt t3, t1, t2\nsltu t4, t1, t2\nsub a0, t3, t4"),
    ("shift_boundary", "arithmetic", "rv32i", 0x80000000, "li t1, 1\nli t2, 31\nsll a0, t1, t2"),
    ("zero_register", "arithmetic", "rv32i", 0, "li t1, 9\nadd zero, t1, t1\nadd a0, zero, zero"),
    ("division_zero", "arithmetic", "rv32im", -1, "li t1, 7\nli t2, 0\ndiv a0, t1, t2"),
    ("division_overflow", "arithmetic", "rv32im", 0x80000000, "li t1, 0x80000000\nli t2, -1\ndiv a0, t1, t2"),
    ("mul_high", "arithmetic", "rv32im", -1, "li t1, -1\nli t2, 2\nmulh a0, t1, t2"),
    ("compressed_dependency", "compressed", "rv32imc", 12, ".option rvc\nli a0, 3\nc.addi a0, 4\nc.addi a0, 5"),
    ("compressed_jump", "compressed", "rv32imc", 8, ".option rvc\nli a0, 8\nc.j 1f\nc.addi a0, 1\n1:"),
    ("atomic_result_load", "atomic", "rv32ia", 19, "la t1, scratch\nli t2, 7\nsw t2, 0(t1)\nli t3, 5\namoadd.w t4, t3, (t1)\nlw t5, 0(t1)\nadd a0, t4, t5"),
    ("fp_single_dependency", "floating", "rv32if_zicsr", 0x40400000, "li t1, 0x3f800000\nfmv.w.x ft0, t1\nli t2, 0x40000000\nfmv.w.x ft1, t2\nfadd.s ft2, ft0, ft1\nfmv.x.w a0, ft2"),
    ("fp_double_to_integer", "floating", "rv32ifd_zicsr", 7, "li t1, 3\nfcvt.d.w ft0, t1\nli t2, 4\nfcvt.d.w ft1, t2\nfadd.d ft2, ft0, ft1\nfcvt.w.d a0, ft2"),
    ("fp_invalid_sqrt_flag", "floating", "rv32if_zicsr", 1,
     "li t1, 0xbf800000\nfmv.w.x ft0, t1\ncsrrw zero, fflags, zero\n"
     "fsqrt.s ft1, ft0\nfmv.x.w t2, ft1\nli t3, 0x7fc00000\n"
     "bne t2, t3, failure\ncsrrs t2, fflags, zero\nli t3, 16\n"
     "bne t2, t3, failure\nli a0, 1"),
    ("fp_dynamic_rounding_flags", "floating", "rv32if_zicsr", 1,
     "li t0, 0x3fc00000\nfmv.w.x ft0, t0\ncsrrwi zero, fflags, 0\n"
     "li t1, 1\ncsrrw zero, frm, t1\nfcvt.w.s t2, ft0, dyn\n"
     "li t3, 1\nbne t2, t3, failure\ncsrrs t4, fflags, zero\n"
     "bne t4, t3, failure\ncsrrwi zero, fflags, 0\n"
     "li t1, 3\ncsrrw zero, frm, t1\nfcvt.w.s t2, ft0, dyn\n"
     "li t3, 2\nbne t2, t3, failure\ncsrrs t4, fflags, zero\n"
     "li t3, 1\nbne t4, t3, failure\nli a0, 1"),
    ("rv64_store_load_dependency", "rv64_memory", "rv64i", 0x100000005, "la t1, scratch64\nli t2, 0x100000002\nsd t2, 0(t1)\nld t3, 0(t1)\naddi a0, t3, 3"),
    ("csr_write_read_dependency", "csr", "rv32if_zicsr", 1,
     "csrrwi zero, fflags, 0\ncsrrsi zero, fflags, 1\n"
     "csrrs a0, fflags, zero"),
    ("rv64_atomic_result_load", "atomic", "rv64ia", 3,
     "la t1, scratch64\nli t2, 3\namoadd.d t3, t2, (t1)\n"
     "ld t4, 0(t1)\nadd a0, t3, t4"),
    ("rv64_fp_single_dependency", "floating", "rv64if_zicsr", 0x40400000,
     "li t1, 0x3f800000\nfmv.w.x ft0, t1\nli t2, 0x40000000\n"
     "fmv.w.x ft1, t2\nfadd.s ft2, ft0, ft1\nfmv.x.w a0, ft2"),
    ("rv64_fp_double_dependency", "floating", "rv64ifd_zicsr", 7,
     "li t1, 3\nfcvt.d.w ft0, t1\nli t2, 4\nfcvt.d.w ft1, t2\n"
     "fadd.d ft2, ft0, ft1\nfcvt.w.d a0, ft2"),
    ("rv64_mul_div_chain", "arithmetic", "rv64im", 0x100000001,
     "li t1, 0x100000001\nli t2, 2\nmul t3, t1, t2\ndivu a0, t3, t2"),
    ("vector_load_add_store", "vector", "rv32im_zicsr_zve32x_zvl128b", 24,
     "vsetivli t0, 2, e32, m1, ta, ma\nla t1, scratch\nli t2, 7\nsw t2, 0(t1)\nli t2, 11\nsw t2, 4(t1)\n"
     "vle32.v v1, (t1)\nvadd.vi v2, v1, 3\nvse32.v v2, (t1)\nlw t3, 0(t1)\nlw t4, 4(t1)\nadd a0, t3, t4"),
    ("vector_e64_two_lane_store", "vector", "rv32im_zicsr_zve64x_zvl128b", 9,
     "vsetivli t0, 2, e64, m1, ta, ma\nla t1, vector64_data\n"
     "vle64.v v1, (t1)\nvadd.vi v2, v1, 3\nla t2, vector64_result\n"
     "vse64.v v2, (t2)\nlw t3, 0(t2)\nlw t4, 8(t2)\nadd a0, t3, t4"),
    ("vector_mask_undisturbed", "vector", "rv32im_zicsr_zve32x_zvl128b", 1,
     "vsetivli t0, 4, e32, m1, tu, mu\nvmv.v.i v1, 2\nvmv.v.i v2, 3\n"
     "vmv.v.i v3, 9\nvid.v v4\nvand.vi v4, v4, 1\nvmsne.vi v0, v4, 0\n"
     "vadd.vv v3, v1, v2, v0.t\nla t1, vector32_result\nvse32.v v3, (t1)\n"
     "lw t2, 0(t1)\nli t3, 9\nbne t2, t3, failure\n"
     "lw t2, 4(t1)\nli t3, 5\nbne t2, t3, failure\n"
     "lw t2, 8(t1)\nli t3, 9\nbne t2, t3, failure\n"
     "lw t2, 12(t1)\nli t3, 5\nbne t2, t3, failure\nli a0, 1"),
    ("vector_tail_undisturbed", "vector", "rv32im_zicsr_zve32x_zvl128b", 1,
     "vsetivli t0, 4, e32, m1, tu, mu\nvmv.v.i v1, 2\nvmv.v.i v2, 3\n"
     "vmv.v.i v3, 9\nvsetivli t0, 2, e32, m1, tu, mu\n"
     "vadd.vv v3, v1, v2\nvsetivli t0, 4, e32, m1, tu, mu\n"
     "la t1, vector32_result\nvse32.v v3, (t1)\n"
     "lw t2, 0(t1)\nli t3, 5\nbne t2, t3, failure\n"
     "lw t2, 4(t1)\nbne t2, t3, failure\n"
     "lw t2, 8(t1)\nli t3, 9\nbne t2, t3, failure\n"
     "lw t2, 12(t1)\nbne t2, t3, failure\nli a0, 1"),
    ("vector_vstart_csr_reset", "vector", "rv32im_zicsr_zve32x_zvl128b", 1,
     "vsetivli t0, 4, e32, m1, tu, mu\nvmv.v.i v1, 2\nvmv.v.i v2, 3\n"
     "vmv.v.i v3, 9\nli t1, 2\ncsrrw zero, vstart, t1\n"
     "csrrs t2, vstart, zero\nbne t1, t2, failure\n"
     "csrrw zero, vstart, zero\nvadd.vv v3, v1, v2\n"
     "csrrs t1, vstart, zero\nbne t1, zero, failure\n"
     "la t1, vector32_result\nvse32.v v3, (t1)\n"
     "lw t2, 0(t1)\nli t3, 5\nbne t2, t3, failure\n"
     "lw t2, 4(t1)\nli t3, 5\nbne t2, t3, failure\n"
     "lw t2, 8(t1)\nli t3, 5\nbne t2, t3, failure\n"
     "lw t2, 12(t1)\nli t3, 5\nbne t2, t3, failure\nli a0, 1"),
    ("vector_vstart_load_resume", "vector", "rv32im_zicsr_zve32x_zvl128b", 1,
     "vsetivli t0, 4, e32, m1, tu, mu\nvmv.v.i v3, 9\n"
     "la t1, vector32_result\nli t2, 2\nsw t2, 0(t1)\nli t2, 3\nsw t2, 4(t1)\n"
     "li t2, 4\nsw t2, 8(t1)\nli t2, 5\nsw t2, 12(t1)\n"
     "li t2, 2\ncsrrw zero, vstart, t2\nvle32.v v3, (t1)\n"
     "csrrs t2, vstart, zero\nbne t2, zero, failure\n"
     "vse32.v v3, (t1)\nlw t2, 0(t1)\nli t3, 9\nbne t2, t3, failure\n"
     "lw t2, 4(t1)\nbne t2, t3, failure\n"
     "lw t2, 8(t1)\nli t3, 4\nbne t2, t3, failure\n"
     "lw t2, 12(t1)\nli t3, 5\nbne t2, t3, failure\nli a0, 1"),
    ("vector_vxsat_sticky", "vector", "rv32im_zicsr_zve32x_zvl128b", 1,
     "vsetivli t0, 4, e8, m1, ta, ma\ncsrrwi zero, vxsat, 0\n"
     "la t1, vector8_data\nvle8.v v1, (t1)\nvsadd.vi v2, v1, 1\n"
     "la t2, vector8_result\nvse8.v v2, (t2)\n"
     "lbu t3, 0(t2)\nli t4, 127\nbne t3, t4, failure\n"
     "lbu t3, 1(t2)\nbne t3, t4, failure\n"
     "lbu t3, 2(t2)\nli t4, 1\nbne t3, t4, failure\n"
     "lbu t3, 3(t2)\nbne t3, zero, failure\n"
     "csrrs t5, vxsat, zero\nbne t5, t4, failure\nli a0, 1"),
    ("vector_lmul2_cross_register", "vector", "rv32im_zicsr_zve32x_zvl128b", 1,
     "li t1, 20\nvsetvli t0, t1, e8, m2, tu, mu\nbne t0, t1, failure\n"
     "la t2, vector20_data\nvle8.v v2, (t2)\nvadd.vi v4, v2, 1\n"
     "la t3, vector20_result\nvse8.v v4, (t3)\n"
     "li t4, 0\n1: lbu t5, 0(t3)\naddi t6, t4, 2\nbne t5, t6, failure\n"
     "addi t3, t3, 1\naddi t4, t4, 1\nblt t4, t1, 1b\nli a0, 1"),
    ("vector_vstart_store_resume", "vector", "rv32im_zicsr_zve32x_zvl128b", 1,
     "vsetivli t0, 4, e32, m1, tu, mu\nvmv.v.i v3, 5\n"
     "la t1, vector32_result\nli t2, 9\nsw t2, 0(t1)\nsw t2, 4(t1)\n"
     "sw t2, 8(t1)\nsw t2, 12(t1)\nli t2, 2\ncsrrw zero, vstart, t2\n"
     "vse32.v v3, (t1)\ncsrrs t2, vstart, zero\nbne t2, zero, failure\n"
     "lw t2, 0(t1)\nli t3, 9\nbne t2, t3, failure\n"
     "lw t2, 4(t1)\nbne t2, t3, failure\n"
     "lw t2, 8(t1)\nli t3, 5\nbne t2, t3, failure\n"
     "lw t2, 12(t1)\nbne t2, t3, failure\nli a0, 1"),
    ("vector_fractional_lmul_half", "vector", "rv32im_zicsr_zve32x_zvl128b", 1,
     "li t1, 8\nvsetvli t0, t1, e8, mf2, ta, ma\nbne t0, t1, failure\n"
     "la t2, vector20_data\nvle8.v v2, (t2)\nvadd.vi v4, v2, 2\n"
     "la t3, vector20_result\nvse8.v v4, (t3)\n"
     "li t4, 0\n1: lbu t5, 0(t3)\naddi t6, t4, 3\nbne t5, t6, failure\n"
     "addi t3, t3, 1\naddi t4, t4, 1\nblt t4, t1, 1b\nli a0, 1"),
    ("vector_lmul8_e16_cross_register", "vector", "rv32im_zicsr_zve32x_zvl128b", 1,
     "li t1, 40\nvsetvli t0, t1, e16, m8, ta, ma\nbne t0, t1, failure\n"
     "vmv.v.i v8, 7\nla t2, vector40_result\nvse16.v v8, (t2)\n"
     "li t3, 0\n1: lhu t4, 0(t2)\nli t5, 7\nbne t4, t5, failure\n"
     "addi t2, t2, 2\naddi t3, t3, 1\nblt t3, t1, 1b\nli a0, 1"),
    ("vector_vxrm_rounding_modes", "vector", "rv32im_zicsr_zve32x_zvl128b", 1,
     "vsetivli t0, 4, e8, m1, ta, ma\nvmv.v.i v1, 3\n"
     "csrrwi zero, vxrm, 0\nvssra.vi v2, v1, 1\nvmv.x.s t1, v2\n"
     "li t2, 2\nbne t1, t2, failure\n"
     "csrrwi zero, vxrm, 2\nvssra.vi v2, v1, 1\nvmv.x.s t1, v2\n"
     "li t2, 1\nbne t1, t2, failure\n"
     "csrrs t1, vxrm, zero\nli t2, 2\nbne t1, t2, failure\nli a0, 1"),
    ("vector_masked_store_preserves_memory", "vector", "rv32im_zicsr_zve32x_zvl128b", 1,
     "vsetivli t0, 4, e32, m1, tu, mu\nvmv.v.i v1, 5\n"
     "vid.v v4\nvand.vi v4, v4, 1\nvmsne.vi v0, v4, 0\n"
     "la t1, vector32_result\nli t2, 9\nsw t2, 0(t1)\nsw t2, 4(t1)\n"
     "sw t2, 8(t1)\nsw t2, 12(t1)\n"
     "vse32.v v1, (t1), v0.t\n"
     "lw t2, 0(t1)\nli t3, 9\nbne t2, t3, failure\n"
     "lw t2, 4(t1)\nli t3, 5\nbne t2, t3, failure\n"
     "lw t2, 8(t1)\nli t3, 9\nbne t2, t3, failure\n"
     "lw t2, 12(t1)\nli t3, 5\nbne t2, t3, failure\nli a0, 1"),
    ("vector_vlmax_sew_lmul_clamp", "vector", "rv32im_zicsr_zve32x_zvl128b", 1,
     "vsetvli t0, zero, e8, m1, ta, ma\n"
     "vsetvli t1, zero, e16, m1, ta, ma\n"
     "slli t2, t1, 1\nbne t0, t2, failure\n"
     "li t3, 1024\nvsetvli t4, t3, e8, m1, ta, ma\n"
     "bne t4, t0, failure\n"
     "vsetvli t4, t3, e8, m2, ta, ma\n"
     "slli t2, t0, 1\nbne t4, t2, failure\nli a0, 1"),
]

VECTOR_SCENARIO_PROFILES = {
    "vector_load_add_store": ("Zve32x", 32, 2),
    "vector_e64_two_lane_store": ("Zve64x", 64, 2),
    "vector_mask_undisturbed": ("Zve32x", 32, 4),
    "vector_tail_undisturbed": ("Zve32x", 32, 2),
    "vector_vstart_csr_reset": ("Zve32x", 32, 4),
    "vector_vstart_load_resume": ("Zve32x", 32, 4),
    "vector_vxsat_sticky": ("Zve32x", 8, 4),
    "vector_lmul2_cross_register": ("Zve32x", 8, 20),
    "vector_vstart_store_resume": ("Zve32x", 32, 4),
    "vector_fractional_lmul_half": ("Zve32x", 8, 8),
    "vector_lmul8_e16_cross_register": ("Zve32x", 16, 40),
    "vector_vxrm_rounding_modes": ("Zve32x", 8, 4),
    "vector_masked_store_preserves_memory": ("Zve32x", 32, 4),
    "vector_vlmax_sew_lmul_clamp": ("Zve32x", 8, "VLEN-dependent"),
}

VECTOR_SCENARIO_LMUL = {"vector_lmul2_cross_register": "m2",
                        "vector_fractional_lmul_half": "mf2",
                        "vector_lmul8_e16_cross_register": "m8"}


def source_group(case: tuple) -> str:
    """Keep directed package sources with the extension they exercise."""
    _, category, march, _, _ = case
    xlen = "64" if march.startswith("rv64") else "32"
    base = march.split("_", 1)[0]
    if category == "vector":
        return "RV32Zve64x" if "zve64x" in march else "RV32Zve32x"
    if category == "csr":
        return "RV32Zicsr"
    if category == "compressed":
        return "RV32C"
    if category == "atomic":
        return f"RV{xlen}A"
    if category == "floating":
        return f"RV{xlen}{'D' if 'd' in base[4:] else 'F'}"
    if "m" in base[4:]:
        return f"RV{xlen}M"
    return f"RV{xlen}I"


def source(case: tuple) -> str:
    name, category, march, expected, body = case
    xlen = 64 if march.startswith("rv64") else 32
    return f'''# Scenario: {name}; category: {category}; ISA: {march}
# Initial state: all used registers and memory locations initialized in this program.
# Expected a0: {expected & ((1 << xlen) - 1):#x}; completion: status word 1=PASS, 2=FAIL.
.section .text
.global _start
_start:
{body}
li t0, {expected}
bne a0, t0, failure
la t1, result_status
li t2, 1
sw t2, 0(t1)
li a0, 0
j completion
failure:
la t1, result_status
li t2, 2
sw t2, 0(t1)
li a0, 1
completion:
li a7, 93
ecall
.section .data
.balign 4
data_word: .word 5
scratch: .word 0, 0
result_status: .word 0
.balign 8
scratch64: .dword 0
vector64_data: .dword 1, 2
vector64_result: .dword 0, 0
vector32_result: .word 0, 0, 0, 0
vector8_data: .byte 127, 126, 0, 255
vector8_result: .byte 0, 0, 0, 0
vector20_data: .byte 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20
vector20_result: .space 20
vector40_result: .space 80
'''
