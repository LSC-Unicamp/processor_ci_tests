"""Bitmanip Z cases and the initial Zve32x cases.

Additional Zve32x cases are generated in vector_cases.py. P is excluded
while its specification remains a developing draft.
"""


def _bit(group: str, mnemonic: str, expected: int, body: str) -> tuple:
    extension = group.removeprefix("RV32")
    return group, mnemonic, f"rv32i_{extension.lower()}", expected, body


CASES = [
    _bit("RV32Zba", "sh1add", 11, "li t1, 3\nli t2, 5\nsh1add a0, t1, t2"),
    _bit("RV32Zba", "sh2add", 17, "li t1, 3\nli t2, 5\nsh2add a0, t1, t2"),
    _bit("RV32Zba", "sh3add", 29, "li t1, 3\nli t2, 5\nsh3add a0, t1, t2"),
    _bit("RV32Zbb", "andn", 0x50, "li t1, 0x55\nli t2, 0x0f\nandn a0, t1, t2"),
    _bit("RV32Zbb", "orn", -16, "li t1, 0x50\nli t2, 0x0f\norn a0, t1, t2"),
    _bit("RV32Zbb", "xnor", -256, "li t1, 0x55\nli t2, 0xaa\nxnor a0, t1, t2"),
    _bit("RV32Zbb", "clz", 31, "li t1, 1\nclz a0, t1"),
    _bit("RV32Zbb", "ctz", 4, "li t1, 16\nctz a0, t1"),
    _bit("RV32Zbb", "cpop", 8, "li t1, 0xf0f0\ncpop a0, t1"),
    _bit("RV32Zbb", "min", -3, "li t1, -3\nli t2, 2\nmin a0, t1, t2"),
    _bit("RV32Zbb", "minu", 2, "li t1, -3\nli t2, 2\nminu a0, t1, t2"),
    _bit("RV32Zbb", "max", 2, "li t1, -3\nli t2, 2\nmax a0, t1, t2"),
    _bit("RV32Zbb", "maxu", -3, "li t1, -3\nli t2, 2\nmaxu a0, t1, t2"),
    _bit("RV32Zbb", "sext.b", -128, "li t1, 0x80\nsext.b a0, t1"),
    _bit("RV32Zbb", "sext.h", -32768, "li t1, 0x8000\nsext.h a0, t1"),
    _bit("RV32Zbb", "zext.h", 0x8001, "li t1, 0x8001\nzext.h a0, t1"),
    _bit("RV32Zbb", "rol", 3, "li t1, 0x80000001\nli t2, 1\nrol a0, t1, t2"),
    _bit("RV32Zbb", "ror", 0xc0000000, "li t1, 0x80000001\nli t2, 1\nror a0, t1, t2"),
    _bit("RV32Zbb", "rori", 0xc0000000, "li t1, 0x80000001\nrori a0, t1, 1"),
    _bit("RV32Zbb", "orc.b", 0xff000000, "li t1, 0x01000000\norc.b a0, t1"),
    _bit("RV32Zbb", "rev8", 0x78563412, "li t1, 0x12345678\nrev8 a0, t1"),
    _bit("RV32Zbc", "clmul", 15, "li t1, 3\nli t2, 5\nclmul a0, t1, t2"),
    _bit("RV32Zbc", "clmulh", 1, "li t1, 0x80000000\nli t2, 2\nclmulh a0, t1, t2"),
    _bit("RV32Zbc", "clmulr", 2, "li t1, 0x80000000\nli t2, 2\nclmulr a0, t1, t2"),
    _bit("RV32Zbs", "bclr", 0xf7, "li t1, 0xff\nli t2, 3\nbclr a0, t1, t2"),
    _bit("RV32Zbs", "bclri", 0xf7, "li t1, 0xff\nbclri a0, t1, 3"),
    _bit("RV32Zbs", "bext", 1, "li t1, 8\nli t2, 3\nbext a0, t1, t2"),
    _bit("RV32Zbs", "bexti", 1, "li t1, 8\nbexti a0, t1, 3"),
    _bit("RV32Zbs", "binv", 8, "li t1, 0\nli t2, 3\nbinv a0, t1, t2"),
    _bit("RV32Zbs", "binvi", 8, "li t1, 0\nbinvi a0, t1, 3"),
    _bit("RV32Zbs", "bset", 8, "li t1, 0\nli t2, 3\nbset a0, t1, t2"),
    _bit("RV32Zbs", "bseti", 8, "li t1, 0\nbseti a0, t1, 3"),
    _bit("RV32Zbkb", "pack", 0xabcd1234, "li t1, 0x1234\nli t2, 0xabcd\npack a0, t1, t2"),
    _bit("RV32Zbkb", "packh", 0xcd34, "li t1, 0x34\nli t2, 0xcd\npackh a0, t1, t2"),
    _bit("RV32Zbkb", "brev8", 0x80, "li t1, 1\nbrev8 a0, t1"),
    _bit("RV32Zbkb", "zip", 2, "li t1, 0x00010000\nzip a0, t1"),
    _bit("RV32Zbkb", "unzip", 0x00010000, "li t1, 2\nunzip a0, t1"),
]


_V_PREFIX = "li t6, 0x600\ncsrs mstatus, t6\nvsetivli t0, 4, e32, m1, ta, ma\n"
_V_INPUTS = "vmv.v.i v1, 2\nvmv.v.i v2, 3\n"
_V_MARCH = "rv32im_zicsr_zve32x_zvl128b"


def _vector(mnemonic: str, expected: int, body: str) -> tuple:
    return "RV32Zve32x", mnemonic, _V_MARCH, expected, _V_PREFIX + body


CASES += [
    _vector("vadd.vv", 5, _V_INPUTS + "vadd.vv v3, v1, v2\nvmv.x.s a0, v3"),
    _vector("vsub.vv", -1, _V_INPUTS + "vsub.vv v3, v1, v2\nvmv.x.s a0, v3"),
    _vector("vmul.vv", 6, _V_INPUTS + "vmul.vv v3, v1, v2\nvmv.x.s a0, v3"),
    _vector("vcompress.vm", 2, _V_INPUTS + "vmseq.vi v0, v1, 2\nvcompress.vm v3, v1, v0\nvmv.x.s a0, v3"),
    _vector("vfirst.m", 0, _V_INPUTS + "vmseq.vi v0, v1, 2\nvfirst.m a0, v0"),
    _vector("vmin.vv", 2, _V_INPUTS + "vmin.vv v3, v1, v2\nvmv.x.s a0, v3"),
    _vector("vmax.vv", 3, _V_INPUTS + "vmax.vv v3, v1, v2\nvmv.x.s a0, v3"),
    _vector("vslideup.vx", 0, _V_INPUTS + "li t1, 1\nvmv.v.i v3, 0\nvslideup.vx v3, v1, t1\nvmv.x.s a0, v3"),
    _vector("vslidedown.vx", 2, _V_INPUTS + "li t1, 1\nvslidedown.vx v3, v1, t1\nvmv.x.s a0, v3"),
    _vector("vredsum.vs", 11, _V_INPUTS + "vredsum.vs v3, v1, v2\nvmv.x.s a0, v3"),
    _vector("vcpop.m", 4, _V_INPUTS + "vmseq.vi v0, v1, 2\nvcpop.m a0, v0"),
    _vector("vadd.vx", 5, _V_INPUTS + "li t1, 3\nvadd.vx v3, v1, t1\nvmv.x.s a0, v3"),
    _vector("vadd.vi", 5, _V_INPUTS + "vadd.vi v3, v1, 3\nvmv.x.s a0, v3"),
    _vector("vand.vv", 2, _V_INPUTS + "vand.vv v3, v1, v2\nvmv.x.s a0, v3"),
    _vector("vor.vv", 3, _V_INPUTS + "vor.vv v3, v1, v2\nvmv.x.s a0, v3"),
    _vector("vxor.vv", 1, _V_INPUTS + "vxor.vv v3, v1, v2\nvmv.x.s a0, v3"),
    _vector("vsll.vv", 16, _V_INPUTS + "vsll.vv v3, v1, v2\nvmv.x.s a0, v3"),
    _vector("vsrl.vv", 0, _V_INPUTS + "vsrl.vv v3, v1, v2\nvmv.x.s a0, v3"),
    _vector("vsra.vv", -4, "vmv.v.i v1, -8\nvmv.v.i v2, 1\nvsra.vv v3, v1, v2\nvmv.x.s a0, v3"),
    _vector("vminu.vv", 2, _V_INPUTS + "vminu.vv v3, v1, v2\nvmv.x.s a0, v3"),
    _vector("vmaxu.vv", 3, _V_INPUTS + "vmaxu.vv v3, v1, v2\nvmv.x.s a0, v3"),
    _vector("vdivu.vv", 0, _V_INPUTS + "vdivu.vv v3, v1, v2\nvmv.x.s a0, v3"),
    _vector("vremu.vv", 2, _V_INPUTS + "vremu.vv v3, v1, v2\nvmv.x.s a0, v3"),
    _vector("vmseq.vv", 0, _V_INPUTS + "vmseq.vv v0, v1, v2\nvcpop.m a0, v0"),
    _vector("vmsne.vv", 4, _V_INPUTS + "vmsne.vv v0, v1, v2\nvcpop.m a0, v0"),
    _vector("vmslt.vv", 4, _V_INPUTS + "vmslt.vv v0, v1, v2\nvcpop.m a0, v0"),
    _vector("vmsle.vv", 4, _V_INPUTS + "vmsle.vv v0, v1, v2\nvcpop.m a0, v0"),
    _vector("vmerge.vvm", 3, _V_INPUTS + "vmseq.vi v0, v1, 2\nvmerge.vvm v3, v1, v2, v0\nvmv.x.s a0, v3"),
    _vector("vmv.v.x", 7, "li t1, 7\nvmv.v.x v3, t1\nvmv.x.s a0, v3"),
    _vector("vmv.v.i", 7, "vmv.v.i v3, 7\nvmv.x.s a0, v3"),
    _vector("vsetivli", 4, "mv a0, t0"),
    _vector("vsetvli", 4, "li t1, 4\nvsetvli a0, t1, e32, m1, ta, ma"),
    _vector("vle32.v", 0x80ff7f0a, "la t1, vector_words\nvle32.v v3, (t1)\nla t2, vector_scratch\nvse32.v v3, (t2)\nlw a0, 0(t2)\nlw t3, 4(t2)\nadd a0, a0, t3\nlw t3, 8(t2)\nadd a0, a0, t3\nlw t3, 12(t2)\nadd a0, a0, t3"),
    _vector("vse32.v", 8, _V_INPUTS + "la t1, vector_scratch\nvse32.v v1, (t1)\nlw a0, 0(t1)\nlw t2, 4(t1)\nadd a0, a0, t2\nlw t2, 8(t1)\nadd a0, a0, t2\nlw t2, 12(t1)\nadd a0, a0, t2"),
    _vector("vrgather.vv", 2, _V_INPUTS + "vrgather.vv v3, v1, v2\nvmv.x.s a0, v3"),
    _vector("vid.v", 3, "vid.v v3\nvslidedown.vi v4, v3, 3\nvmv.x.s a0, v4"),
    _vector("vslide1up.vx", 7, _V_INPUTS + "li t1, 7\nvslide1up.vx v3, v1, t1\nvmv.x.s a0, v3"),
    _vector("vslide1down.vx", 7, _V_INPUTS + "li t1, 7\nvslide1down.vx v3, v1, t1\nvslidedown.vi v4, v3, 3\nvmv.x.s a0, v4"),
    _vector("vredmax.vs", 3, _V_INPUTS + "vredmax.vs v3, v1, v2\nvmv.x.s a0, v3"),
    _vector("vredand.vs", 2, _V_INPUTS + "vredand.vs v3, v1, v2\nvmv.x.s a0, v3"),
    _vector("vredor.vs", 3, _V_INPUTS + "vredor.vs v3, v1, v2\nvmv.x.s a0, v3"),
    _vector("vredxor.vs", 3, _V_INPUTS + "vredxor.vs v3, v1, v2\nvmv.x.s a0, v3"),
    _vector("vmacc.vv", 10, _V_INPUTS + "vmv.v.i v3, 4\nvmacc.vv v3, v1, v2\nvmv.x.s a0, v3"),
    _vector("vmadd.vv", 11, _V_INPUTS + "vmv.v.i v3, 4\nvmadd.vv v3, v1, v2\nvmv.x.s a0, v3"),
    _vector("vnmsac.vv", -2, _V_INPUTS + "vmv.v.i v3, 4\nvnmsac.vv v3, v1, v2\nvmv.x.s a0, v3"),
    _vector("vnmsub.vv", -5, _V_INPUTS + "vmv.v.i v3, 4\nvnmsub.vv v3, v1, v2\nvmv.x.s a0, v3"),
]

from vector_cases import CASES as EXTRA_VECTOR_CASES

CASES.extend(EXTRA_VECTOR_CASES)
