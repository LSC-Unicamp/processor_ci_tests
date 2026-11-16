"""ISA-aware selection of configured legacy test directories."""
import re

from riscv_test_runner.core.march import parse_march


def _extensions(march: str) -> tuple[int, set[str]]:
    parsed = parse_march(march.lower())
    extensions = set(parsed["extensions"])
    if "G" in extensions:
        extensions |= {"I", "M", "A", "F", "D", "Zicsr", "Zifencei"}
    if "B" in extensions:
        extensions |= {"Zba", "Zbb", "Zbs"}
    if "V" in extensions:
        extensions |= {"Zve64d", "Zvl128b"}
    if "Zve64d" in extensions:
        extensions |= {"Zve64f", "D"}
    if "Zve64f" in extensions or "Zve64d" in extensions:
        extensions |= {"Zve32f", "Zve64x", "F"}
    if extensions & {"Zve32f", "Zve64x", "Zve64f", "Zve64d"}:
        extensions.add("Zve32x")
    if "Zve32x" in extensions:
        extensions |= {"Zicsr", "Zvl32b"}
    if "Zve64x" in extensions:
        extensions.add("Zvl64b")
    if "D" in extensions:
        extensions.add("F")
    if "F" in extensions:
        extensions.add("Zicsr")
    for ext in tuple(extensions):
        if ext.startswith("Zvl") and ext.endswith("b") and ext[3:-1].isdigit():
            length = int(ext[3:-1])
            extensions |= {f"Zvl{n}b" for n in (32, 64, 128, 256, 512, 1024) if n <= length}
    return parsed["xlen"], extensions


def isa_compatible(required: str, available: str) -> bool:
    """Return whether an ISA package can run with the advertised XLEN/extensions."""
    required_xlen, required_extensions = _extensions(required)
    available_xlen, available_extensions = _extensions(available)
    return required_xlen == available_xlen and required_extensions <= available_extensions


def select_directories(config: dict, march: str) -> list[dict]:
    xlen, extensions = _extensions(march)
    ambiguous = extensions & {"P"}
    if ambiguous:
        raise ValueError("P remains a developing draft; select a verified P encoding profile before execution")
    result = []
    for directory in config.get("test_directories", []):
        match = re.fullmatch(r"RV(32|64)([A-Za-z][A-Za-z0-9]*)", directory["name"])
        if not match or int(match.group(1)) != xlen:
            continue
        extension = match.group(2)
        if extension in {"B", "V"}:
            continue  # umbrella names are not executable Z test groups
        if extension not in extensions:
            continue
        result.append(directory)
    return result
