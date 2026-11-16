"""RV32 integer-vector forms that first become legal in Zve64x.

The four EEW64 indexed-memory forms in the full-V catalog require RV64 and
are deliberately absent from this RV32 group.
"""

V_MARCH = "rv32im_zicsr_zve64x_zvl128b"
CASES: list[tuple] = []
CASE_PROFILES: dict[str, dict] = {}


def add(mnemonic: str, expected: int, body: str) -> None:
    prefix = "li t6, 0x600\ncsrs mstatus, t6\nvsetivli t0, 2, e64, m1, ta, ma\n"
    CASES.append(("RV32Zve64x", mnemonic, V_MARCH, expected, prefix + body))
    CASE_PROFILES[mnemonic] = {"extension": "Zve64x", "minimum_vlen_bits": 128,
                               "sew_bits": 64, "lmul": "m1", "vl": 2,
                               "reference_vlen_bits": 1024}


for group in (1, 2, 4, 8):
    name = f"vl{group}re64.v"
    add(name, 7, f"la t1, vector_blob\n{name} v8, (t1)\nvmv.x.s a0, v8")

for name in ("vle64.v", "vle64ff.v"):
    add(name, 7, f"la t1, vector_blob\n{name} v8, (t1)\nvmv.x.s a0, v8")

add("vlse64.v", 7, "la t1, vector_blob\nli t2, 8\n"
    "vlse64.v v8, (t1), t2\nvmv.x.s a0, v8")
add("vse64.v", 7, "la t1, vector_blob\nvle64.v v8, (t1)\n"
    "la t2, vector_store\nvse64.v v8, (t2)\nlw a0, 0(t2)")
add("vsse64.v", 7, "la t1, vector_blob\nvle64.v v8, (t1)\n"
    "la t2, vector_store\nli t3, 8\nvsse64.v v8, (t2), t3\nlw a0, 0(t2)")

for name, expected in (("vsext.vf8", -1), ("vzext.vf8", 255)):
    add(name, expected, "vsetivli t0, 16, e8, m1, ta, ma\n"
        "vmv.v.i v1, -1\nvsetivli t0, 2, e64, m1, ta, ma\n"
        f"{name} v8, v1\nvmv.x.s a0, v8")


RV64_MARCH = "rv64im_zicsr_zve64x_zvl128b"


def add_rv64(name: str, body: str) -> None:
    prefix = "li t6, 0x600\ncsrs mstatus, t6\nvsetivli t0, 2, e64, m1, ta, ma\n"
    CASES.append(("RV64Zve64x", name, RV64_MARCH, 7, prefix + body))
    CASE_PROFILES[name] = {"extension": "Zve64x", "minimum_vlen_bits": 128,
                           "sew_bits": 64, "lmul": "m1", "vl": 2,
                           "reference_vlen_bits": 1024}


for name in ("vloxei64.v", "vluxei64.v"):
    add_rv64(name, "vmv.v.i v2, 0\nla t1, vector_blob\n"
             f"{name} v8, (t1), v2\nvmv.x.s a0, v8")
for name in ("vsoxei64.v", "vsuxei64.v"):
    add_rv64(name, "vmv.v.i v2, 0\nvmv.v.i v8, 7\nla t1, vector_store\n"
             f"{name} v8, (t1), v2\nld a0, 0(t1)")
