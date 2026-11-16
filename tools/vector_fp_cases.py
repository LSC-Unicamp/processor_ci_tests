"""Dedicated RV32Zve32f FP32 vector opcode-form cases.

The operands are exactly representable FP32 values. Each case checks either
raw result bits, an integer conversion, or all four comparison mask bits.
"""

import struct

MARCH = "rv32imf_zicsr_zve32f_zvl128b"
CASES: list[tuple] = []
CASE_PROFILES: dict[str, dict] = {}


def bits(value: float) -> int:
    return int.from_bytes(struct.pack("<f", value), "little")


SETUP = ("li t6, 0x6600\ncsrs mstatus, t6\n"
         "vsetivli t0, 4, e32, m1, ta, ma\n"
         "li t1, 0x3f800000\nfmv.w.x f1, t1\n"
         "li t1, 0x40000000\nfmv.w.x f2, t1\n"
         "li t1, 0x40800000\nfmv.w.x f4, t1\n"
         "vfmv.v.f v1, f1\nvfmv.v.f v2, f2\n")
EXTRACT_FP = "vfmv.f.s f3, v3\nfmv.x.w a0, f3"


def add(name: str, expected: int, operation: str, *, result: str = EXTRACT_FP) -> None:
    CASES.append(("RV32Zve32f", name, MARCH, expected, SETUP + operation + "\n" + result))
    CASE_PROFILES[name] = {"extension": "Zve32f", "minimum_vlen_bits": 128,
                           "sew_bits": 32, "lmul": "m1", "vl": 4,
                           "reference_vlen_bits": 1024}


for root, expected in (("vfadd", 3.0), ("vfsub", -1.0),
                       ("vfmul", 2.0), ("vfdiv", 0.5),
                       ("vfmin", 1.0), ("vfmax", 2.0),
                       ("vfsgnj", 1.0), ("vfsgnjn", -1.0),
                       ("vfsgnjx", 1.0)):
    for form, right in (("vv", "v2"), ("vf", "f2")):
        name = f"{root}.{form}"
        add(name, bits(expected), f"{name} v3, v1, {right}")

for name, expected in (("vfrsub.vf", 1.0), ("vfrdiv.vf", 2.0)):
    add(name, bits(expected), f"{name} v3, v1, f2")
add("vfsqrt.v", bits(1.0), "vfsqrt.v v3, v1")

# Both approximation instructions have an exact architected +zero case.
for name in ("vfrec7.v", "vfrsqrt7.v"):
    add(name, 0x7f800000,
        f"fmv.w.x f0, zero\nvfmv.v.f v1, f0\ncsrwi fflags, 0\n"
        f"{name} v3, v1\ncsrr t2, fflags\nli t3, 8\nbne t2, t3, failure")

for root, expected in (("vfmacc", 6.0), ("vfmadd", 6.0),
                       ("vfmsac", -2.0), ("vfmsub", 2.0),
                       ("vfnmacc", -6.0), ("vfnmadd", -6.0),
                       ("vfnmsac", 2.0), ("vfnmsub", -2.0)):
    for form, right in (("vv", "v2"), ("vf", "f2")):
        name = f"{root}.{form}"
        operands = f"v3, f2, v1" if form == "vf" else f"v3, v1, {right}"
        form_expected = ({"vfmadd": 9.0, "vfmsub": 7.0,
                          "vfnmadd": -9.0, "vfnmsub": -7.0}.get(root, expected)
                         if form == "vf" else expected)
        add(name, bits(form_expected), f"vfmv.v.f v3, f4\n{name} {operands}")

for name, expected in (("vfredmax.vs", 2.0), ("vfredmin.vs", 1.0),
                       ("vfredosum.vs", 6.0), ("vfredusum.vs", 6.0)):
    add(name, bits(expected), f"{name} v3, v1, v2")

add("vfclass.v", 0x40, "vfclass.v v3, v1", result="vmv.x.s a0, v3")

for name in ("vfcvt.f.x.v", "vfcvt.f.xu.v"):
    add(name, bits(2.0), f"vmv.v.i v1, 2\n{name} v3, v1")
for name in ("vfcvt.x.f.v", "vfcvt.xu.f.v",
             "vfcvt.rtz.x.f.v", "vfcvt.rtz.xu.f.v"):
    add(name, 1, f"{name} v3, v1", result="vmv.x.s a0, v3")

add("vfmv.f.s", bits(1.0), "vfmv.f.s f3, v1", result="fmv.x.w a0, f3")
add("vfmv.s.f", bits(2.0), "vfmv.v.f v3, f1\nvfmv.s.f v3, f2")
add("vfmv.v.f", bits(2.0), "vfmv.v.f v3, f2")
add("vfmerge.vfm", bits(2.0), "vmv.v.i v4, 0\nvmseq.vi v0, v4, 0\n"
    "vfmerge.vfm v3, v1, f2, v0")

add("vfslide1up.vf", bits(2.0), "vfslide1up.vf v3, v1, f2")
add("vfslide1down.vf", bits(2.0), "vfslide1down.vf v3, v1, f2\n"
    "vslidedown.vi v4, v3, 3", result="vfmv.f.s f3, v4\nfmv.x.w a0, f3")

for root, expected in (("vmfeq", 0), ("vmfne", 4),
                       ("vmflt", 4), ("vmfle", 4)):
    for form, right in (("vv", "v2"), ("vf", "f2")):
        name = f"{root}.{form}"
        add(name, expected, f"{name} v0, v1, {right}", result="vcpop.m a0, v0")
for name in ("vmfge.vf", "vmfgt.vf"):
    add(name, 0, f"{name} v0, v1, f2", result="vcpop.m a0, v0")


def add64f(name: str, expected: int, body: str) -> None:
    march = "rv32imf_zicsr_zve64f_zvl128b"
    prefix = "li t6, 0x6600\ncsrs mstatus, t6\nvsetivli t0, 4, e32, m1, ta, ma\n"
    CASES.append(("RV32Zve64f", name, march, expected, prefix + body))
    CASE_PROFILES[name] = {"extension": "Zve64f", "minimum_vlen_bits": 128,
                           "sew_bits": 32, "lmul": "m1", "vl": 4,
                           "reference_vlen_bits": 1024}


for name in ("vfncvt.f.x.w", "vfncvt.f.xu.w"):
    add64f(name, bits(1.0), "vsetivli t0, 4, e64, m2, ta, ma\n"
           "vmv.v.i v8, 1\nvsetivli t0, 4, e32, m1, ta, ma\n"
           f"{name} v3, v8\n{EXTRACT_FP}")
for name in ("vfwcvt.x.f.v", "vfwcvt.xu.f.v",
             "vfwcvt.rtz.x.f.v", "vfwcvt.rtz.xu.f.v"):
    add64f(name, 1, "li t1, 0x3f800000\nfmv.w.x f1, t1\n"
           "vfmv.v.f v1, f1\n"
           f"{name} v8, v1\nvmv.x.s a0, v8")


def high_word(value: float) -> int:
    return int.from_bytes(struct.pack("<d", value)[4:], "little")


FP32_SETUP = ("li t1, 0x3f800000\nfmv.w.x f1, t1\n"
              "li t1, 0x40000000\nfmv.w.x f2, t1\n"
              "vfmv.v.f v1, f1\nvfmv.v.f v2, f2\n")
WIDE4_SETUP = ("li t1, 0x40800000\nfmv.w.x f4, t1\n"
               "vfmv.v.f v1, f4\nvfwcvt.f.f.v v8, v1\n" + FP32_SETUP)
CHECK_FP64 = ("la t1, vector_store\nvse64.v v16, (t1)\n"
              "lw t2, 0(t1)\nbnez t2, failure\nlw a0, 4(t1)")


def add64d(name: str, expected: int, body: str) -> None:
    march = "rv32imfd_zicsr_zve64d_zvl128b"
    prefix = "li t6, 0x6600\ncsrs mstatus, t6\nvsetivli t0, 4, e32, m1, ta, ma\n"
    CASES.append(("RV32Zve64d", name, march, expected, prefix + body))
    CASE_PROFILES[name] = {"extension": "Zve64d", "minimum_vlen_bits": 128,
                           "sew_bits": 32, "lmul": "m1", "vl": 4,
                           "reference_vlen_bits": 1024}


for root, narrow, wide in (("vfwadd", 3.0, 5.0), ("vfwsub", -1.0, 3.0)):
    for form, operand in (("vv", "v2"), ("vf", "f2")):
        name = f"{root}.{form}"
        add64d(name, high_word(narrow), FP32_SETUP + f"{name} v16, v1, {operand}\n" + CHECK_FP64)
    for form, operand in (("wv", "v1"), ("wf", "f2")):
        name = f"{root}.{form}"
        result = wide if form == "wv" else (6.0 if root == "vfwadd" else 2.0)
        add64d(name, high_word(result), WIDE4_SETUP + f"{name} v16, v8, {operand}\n" + CHECK_FP64)

for form, operand in (("vv", "v2"), ("vf", "f2")):
    name = f"vfwmul.{form}"
    add64d(name, high_word(2.0), FP32_SETUP + f"{name} v16, v1, {operand}\n" + CHECK_FP64)

for root, expected in (("vfwmacc", 6.0), ("vfwmsac", -2.0),
                       ("vfwnmacc", -6.0), ("vfwnmsac", 2.0)):
    for form, operand in (("vv", "v2"), ("vf", "f2")):
        name = f"{root}.{form}"
        operands = "v16, f2, v1" if form == "vf" else f"v16, v1, {operand}"
        add64d(name, high_word(expected), WIDE4_SETUP +
               "vmv.v.v v16, v8\n" + f"{name} {operands}\n" + CHECK_FP64)

for name in ("vfwredosum.vs", "vfwredusum.vs"):
    add64d(name, high_word(6.0), FP32_SETUP +
           "li t1, 0x40000000\nfmv.w.x f4, t1\n"
           "vfwcvt.f.f.v v8, v2\n" + f"{name} v16, v1, v8\n" + CHECK_FP64)

for name in ("vfwcvt.f.f.v", "vfwcvt.f.x.v", "vfwcvt.f.xu.v"):
    integer_input = "vmv.v.i v1, 2\n" if ".x" in name else ""
    expected = 2.0 if integer_input else 1.0
    add64d(name, high_word(expected), FP32_SETUP + integer_input +
           f"{name} v16, v1\n" + CHECK_FP64)

NARROW_SOURCE = ("la t1, double_one\nfld f1, 0(t1)\n"
                 "vsetivli t0, 4, e64, m2, ta, ma\n"
                 "vfmv.v.f v8, f1\n"
                 "vsetivli t0, 4, e32, m1, ta, ma\n")
for name in ("vfncvt.f.f.w", "vfncvt.rod.f.f.w"):
    add64d(name, bits(1.0), NARROW_SOURCE + f"{name} v3, v8\n" + EXTRACT_FP)
for name in ("vfncvt.x.f.w", "vfncvt.xu.f.w",
             "vfncvt.rtz.x.f.w", "vfncvt.rtz.xu.f.w"):
    add64d(name, 1, NARROW_SOURCE + f"{name} v3, v8\nvmv.x.s a0, v3")
