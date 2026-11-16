"""Additional dedicated RV32Zve32x cases, grouped by opcode form.

The expected values are fixed architectural results. Sail execution is the
independent reference check, and the basic builder checks target disassembly.
"""

V_MARCH = "rv32im_zicsr_zve32x_zvl128b"
CASES: list[tuple] = []
CASE_PROFILES: dict[str, dict] = {}


def add(mnemonic: str, expected: int, body: str, *, sew: int = 32, vl: int = 4) -> None:
    prefix = f"li t6, 0x600\ncsrs mstatus, t6\nvsetivli t0, {vl}, e{sew}, m1, ta, ma\n"
    CASES.append(("RV32Zve32x", mnemonic, V_MARCH, expected, prefix + body))
    CASE_PROFILES[mnemonic] = {"extension": "Zve32x", "minimum_vlen_bits": 128,
                               "sew_bits": sew, "lmul": "m1", "vl": vl,
                               "reference_vlen_bits": 1024}


# Configuration: use a previously established legal vtype as the register input.
add("vsetvl", 4, "csrr t2, vtype\nli t1, 4\nvsetvl a0, t1, t2")


# Whole-register transfers use an area large enough for eight registers at
# the architectural maximum VLEN; the basic source generator sizes it.
for group in (1, 2, 4, 8):
    for width in (8, 16, 32):
        name = f"vl{group}re{width}.v"
        add(name, 7, f"la t1, vector_blob\n{name} v8, (t1)\nvmv.x.s a0, v8")
    name = f"vs{group}r.v"
    add(name, 2, f"la t1, vector_blob\nvl{group}re8.v v8, (t1)\n"
        f"vmv.v.i v8, 2\nla t1, vector_store\n{name} v8, (t1)\nlw a0, 0(t1)")


LOAD_FIRST = {8: 1, 16: 0x7F01, 32: 0x80FF7F01}
for width, expected in LOAD_FIRST.items():
    for suffix in ("", "ff"):
        name = f"vle{width}{suffix}.v"
        if name != "vle32.v":
            add(name, expected, f"la t1, vector_words\n{name} v3, (t1)\nvmv.x.s a0, v3", sew=width)
    name = f"vse{width}.v"
    if name != "vse32.v":
        load = {8: "lbu", 16: "lhu", 32: "lw"}[width]
        add(name, 2, f"vmv.v.i v1, 2\nla t1, vector_scratch\n{name} v1, (t1)\n{load} a0, 0(t1)", sew=width)
    for prefix in ("vlse", "vsse"):
        name = f"{prefix}{width}.v"
        if prefix == "vlse":
            add(name, expected, f"la t1, vector_words\nli t2, 4\n{name} v3, (t1), t2\nvmv.x.s a0, v3", sew=width)
        else:
            load = {8: "lbu", 16: "lhu", 32: "lw"}[width]
            add(name, 2, f"vmv.v.i v1, 2\nla t1, vector_scratch\nli t2, 4\n{name} v1, (t1), t2\n{load} a0, 0(t1)", sew=width)


for width in (8, 16, 32):
    for prefix in ("vluxei", "vloxei", "vsuxei", "vsoxei"):
        name = f"{prefix}{width}.v"
        if prefix.startswith("vl"):
            add(name, 0x80FF7F01, f"vmv.v.i v2, 0\nla t1, vector_words\n{name} v3, (t1), v2\nvmv.x.s a0, v3")
        else:
            add(name, 2, f"vmv.v.i v1, 2\nvmv.v.i v2, 0\nla t1, vector_scratch\n{name} v1, (t1), v2\nlw a0, 0(t1)")


add("vlm.v", 1, "la t1, vector_words\nvlm.v v0, (t1)\nvcpop.m a0, v0")
add("vsm.v", 15, "vmv.v.i v1, 2\nvmseq.vi v0, v1, 2\nla t1, vector_scratch\nvsm.v v0, (t1)\nlbu a0, 0(t1)")


def binary(root: str, forms: str, expected: int, *, lhs: int = 2, rhs: int = 3) -> None:
    for form in forms.split():
        name = f"{root}.{form}"
        operand = {"vv": "v2", "vx": "t1", "vi": str(rhs)}[form]
        add(name, expected, f"vmv.v.i v1, {lhs}\nvmv.v.i v2, {rhs}\nli t1, {rhs}\n"
            f"{name} v3, v1, {operand}\nvmv.x.s a0, v3")


for root, forms, expected in (
    ("vand", "vi vx", 2), ("vor", "vi vx", 3), ("vxor", "vi vx", 1),
    ("vmin", "vx", 2), ("vminu", "vx", 2),
    ("vmax", "vx", 3), ("vmaxu", "vx", 3),
    ("vsub", "vx", -1), ("vrsub", "vi vx", 1),
    ("vmul", "vx", 6), ("vdiv", "vv vx", 0), ("vdivu", "vx", 0),
    ("vrem", "vv vx", 2), ("vremu", "vx", 2),
    ("vsll", "vi vx", 16), ("vsrl", "vi vx", 0),
    ("vslidedown", "vi", 2),
):
    binary(root, forms, expected)

for form in ("vi", "vx"):
    name = f"vsra.{form}"
    shift = "1" if form == "vi" else "t1"
    add(name, -4, f"vmv.v.i v1, -8\nli t1, 1\n{name} v3, v1, {shift}\nvmv.x.s a0, v3")

add("vslideup.vi", 2, "vmv.v.i v1, 2\nvmv.v.i v3, 0\n"
    "vslideup.vi v3, v1, 1\nvslidedown.vi v4, v3, 1\nvmv.x.s a0, v4")

for name, expected in (("vredmaxu.vs", 3), ("vredmin.vs", 2), ("vredminu.vs", 2)):
    add(name, expected, f"vmv.v.i v1, 2\nvmv.v.i v2, 3\n{name} v3, v1, v2\nvmv.x.s a0, v3")

for name, expected in (("vrgather.vi", 2), ("vrgather.vx", 2)):
    index = "3" if name.endswith(".vi") else "t1"
    add(name, expected, f"vmv.v.i v1, 2\nli t1, 3\n{name} v3, v1, {index}\nvmv.x.s a0, v3")

add("vrgatherei16.vv", 2, "vsetivli t0, 4, e16, m1, ta, ma\nvmv.v.i v2, 3\n"
    "vsetivli t0, 4, e32, m1, ta, ma\nvmv.v.i v1, 2\n"
    "vrgatherei16.vv v3, v1, v2\nvmv.x.s a0, v3")

for name in ("vmv.s.x", "vmv.v.v", "vmv.x.s"):
    if name == "vmv.s.x":
        add(name, 3, "li t1, 3\nvmv.v.i v3, 0\nvmv.s.x v3, t1\nvmv.x.s a0, v3")
    elif name == "vmv.v.v":
        add(name, 2, "vmv.v.i v1, 2\nvmv.v.v v3, v1\nvmv.x.s a0, v3")
    else:
        add(name, 2, "vmv.v.i v1, 2\nvmv.x.s a0, v1")

for group in (1, 2, 4, 8):
    name = f"vmv{group}r.v"
    add(name, 7, f"la t1, vector_blob\nvl{group}re8.v v8, (t1)\n{name} v16, v8\n"
        "vmv.x.s a0, v16")


# Integer compares produce masks; counting all four active bits checks every
# lane rather than only the first destination bit.
COMPARE = {
    "vmseq": [("vi", 2, 4), ("vx", 3, 0)],
    "vmsne": [("vi", 3, 4), ("vx", 3, 4)],
    "vmslt": [("vx", 3, 4)],
    "vmsltu": [("vv", 3, 4), ("vx", 3, 4)],
    "vmsle": [("vi", 3, 4), ("vx", 3, 4)],
    "vmsleu": [("vi", 3, 4), ("vv", 3, 4), ("vx", 3, 4)],
    "vmsgt": [("vi", 3, 0), ("vx", 3, 0)],
    "vmsgtu": [("vi", 3, 0), ("vx", 3, 0)],
}
for root, forms in COMPARE.items():
    for form, value, expected in forms:
        name = f"{root}.{form}"
        operand = {"vv": "v2", "vx": "t1", "vi": str(value)}[form]
        add(name, expected, f"vmv.v.i v1, 2\nvmv.v.i v2, 3\nli t1, 3\n"
            f"{name} v0, v1, {operand}\nvcpop.m a0, v0")

for root, forms, expected in (("vmadc", "vi vim vv vvm vx vxm", 4),
                              ("vmsbc", "vv vvm vx vxm", 4),
                              ("vadc", "vim vvm vxm", 1),
                              ("vsbc", "vvm vxm", -2)):
    for form in forms.split():
        name = f"{root}.{form}"
        addition = root in ("vmadc", "vadc")
        operand = "1" if form in ("vi", "vim") else "v2" if form.startswith("vv") else "t1"
        mask_operand = ", v0" if form.endswith("m") else ""
        lhs = -1 if addition else 0
        add(name, expected, f"vmv.v.i v1, {lhs}\nvmv.v.i v2, 1\nli t1, 1\n"
            "vmv.v.i v4, 0\nvmseq.vi v0, v4, 0\n"
            f"{name} v3, v1, {operand}{mask_operand}\n"
            + ("vcpop.m a0, v3" if root.startswith("vm") else "vmv.x.s a0, v3"))

for name, expected in (("vmand.mm", 0), ("vmandn.mm", 4),
                       ("vmnand.mm", 4), ("vmnor.mm", 0),
                       ("vmor.mm", 4), ("vmorn.mm", 4),
                       ("vmxor.mm", 4), ("vmxnor.mm", 0)):
    add(name, expected, "vmv.v.i v4, 2\nvmseq.vi v1, v4, 2\nvmseq.vi v2, v4, 3\n"
        f"{name} v3, v1, v2\nvcpop.m a0, v3")

for name in ("vmerge.vim", "vmerge.vxm"):
    operand = "3" if name.endswith(".vim") else "t1"
    add(name, 3, "vmv.v.i v1, 2\nli t1, 3\nvmseq.vi v0, v1, 2\n"
        f"{name} v3, v1, {operand}, v0\nvmv.x.s a0, v3")

for name, expected in (("vmsbf.m", 2), ("vmsif.m", 3), ("vmsof.m", 1)):
    add(name, expected, "vid.v v1\nvmseq.vi v0, v1, 2\n"
        f"{name} v3, v0\nvcpop.m a0, v3")

add("viota.m", 3, "vmv.v.i v1, 2\nvmseq.vi v0, v1, 2\n"
    "viota.m v3, v0\nvslidedown.vi v4, v3, 3\nvmv.x.s a0, v4")


# Averaging uses even sums and differences so the expected result is stable
# across all legal vxrm rounding modes.
for root, expected in (("vaadd", 3), ("vaaddu", 3),
                       ("vasub", 1), ("vasubu", 1)):
    binary(root, "vv vx", expected, lhs=4, rhs=2)

for root, forms, expected in (("vsadd", "vi vv vx", 5),
                              ("vsaddu", "vi vv vx", 5),
                              ("vssub", "vv vx", -1)):
    binary(root, forms, expected)

for form in ("vv", "vx"):
    name = f"vssubu.{form}"
    operand = "v2" if form == "vv" else "t1"
    add(name, 1, "csrwi vxsat, 0\nvmv.v.i v1, 2\nvmv.v.i v2, 3\nli t1, 3\n"
        f"{name} v3, v1, {operand}\nvmv.x.s a0, v3\ncsrr t2, vxsat\nadd a0, a0, t2")

for root, expected in (("vmulh", -1), ("vmulhsu", -1), ("vmulhu", 1)):
    for form in ("vv", "vx"):
        name = f"{root}.{form}"
        operand = "v2" if form == "vv" else "t1"
        add(name, expected, "vmv.v.i v1, -1\nvmv.v.i v2, 2\nli t1, 2\n"
            f"{name} v3, v1, {operand}\nvmv.x.s a0, v3")

for root, expected in (("vmacc", 10), ("vmadd", 14),
                       ("vnmsac", -2), ("vnmsub", -10)):
    name = f"{root}.vx"
    add(name, expected, "vmv.v.i v1, 2\nvmv.v.i v3, 4\nli t1, 3\n"
        f"{name} v3, t1, v1\nvmv.x.s a0, v3")

for root, expected in (("vsext", -1), ("vzext", 0xFFFF)):
    for factor in (2, 4):
        name = f"{root}.vf{factor}"
        value = expected if factor == 2 or root == "vsext" else 0xFF
        add(name, value, f"vmv.v.i v1, -1\n{name} v3, v1\nvmv.x.s a0, v3")

for root in ("vssra", "vssrl"):
    for form in ("vi", "vv", "vx"):
        name = f"{root}.{form}"
        operand = "1" if form == "vi" else "v2" if form == "vv" else "t1"
        add(name, 4, f"vmv.v.i v1, 8\nvmv.v.i v2, 1\nli t1, 1\n"
            f"{name} v3, v1, {operand}\nvmv.x.s a0, v3")

for form in ("vv", "vx"):
    name = f"vsmul.{form}"
    operand = "v2" if form == "vv" else "t1"
    add(name, 0x20000000, "li t1, 0x40000000\nvmv.v.x v1, t1\nvmv.v.x v2, t1\n"
        f"{name} v3, v1, {operand}\nvmv.x.s a0, v3")


# Narrowing cases use SEW 16 and a 32-bit wide source group. The wide source
# occupies v8-v9, and the destination v4 does not overlap it.
for root in ("vnclip", "vnclipu", "vnsra", "vnsrl"):
    for form in ("wi", "wv", "wx"):
        name = f"{root}.{form}"
        shift = "1" if form == "wi" else "v1" if form == "wv" else "t1"
        add(name, 4, "vsetivli t0, 4, e32, m2, ta, ma\nvmv.v.i v8, 8\n"
            "vsetivli t0, 4, e16, m1, ta, ma\nvmv.v.i v1, 1\nli t1, 1\n"
            f"{name} v4, v8, {shift}\nvmv.x.s a0, v4", sew=16)


def widening_setup() -> str:
    return ("vsetivli t0, 4, e32, m2, ta, ma\nvmv.v.i v4, 8\nvmv.v.i v8, 1\n"
            "vsetivli t0, 4, e16, m1, ta, ma\nvmv.v.i v1, 4\nvmv.v.i v2, 2\nli t1, 2\n")


def widening_result() -> str:
    return "\nvsetivli t0, 4, e32, m1, ta, ma\nvmv.x.s a0, v8"


for root in ("vwadd", "vwaddu", "vwsub", "vwsubu"):
    for form in ("vv", "vx", "wv", "wx"):
        name = f"{root}.{form}"
        wide = form.startswith("w")
        lhs = "v4" if wide else "v1"
        rhs = "v2" if form.endswith("v") else "t1"
        expected = (10 if wide else 6) if root.startswith("vwadd") else (6 if wide else 2)
        add(name, expected, widening_setup() + f"{name} v8, {lhs}, {rhs}" + widening_result(), sew=16)

for root, forms in (("vwmul", "vv vx"), ("vwmulu", "vv vx"),
                    ("vwmulsu", "vv vx")):
    for form in forms.split():
        name = f"{root}.{form}"
        rhs = "v2" if form == "vv" else "t1"
        add(name, 8, widening_setup() + f"{name} v8, v1, {rhs}" + widening_result(), sew=16)

for root, forms in (("vwmacc", "vv vx"), ("vwmaccu", "vv vx"),
                    ("vwmaccsu", "vv vx"), ("vwmaccus", "vx")):
    for form in forms.split():
        name = f"{root}.{form}"
        lhs = "v1" if form == "vv" else "t1"
        add(name, 9 if form == "vv" else 5,
            widening_setup() + f"{name} v8, {lhs}, v2" + widening_result(), sew=16)

for name in ("vwredsum.vs", "vwredsumu.vs"):
    add(name, 24, widening_setup() + f"{name} v8, v1, v4" + widening_result(), sew=16)
