"""Validate and inspect sparse self-checking ELF packages on the host."""
from __future__ import annotations

from riscv_test_runner.core.selection import isa_compatible


class InvalidPackage(ValueError):
    pass


TRAP_FAILURE_CODES = {"3": "EXPECTED_TRAP_MISSING", "5": "UNEXPECTED_TRAP",
                      "7": "ARCHITECTURAL_MISMATCH"}


def initial_memory(package: dict, *, supported_isa: set[str] | None = None) -> dict[int, int]:
    if not isinstance(package, dict):
        raise InvalidPackage("package must be an object")
    if package.get("schema_version") != 1 or package.get("test_source") not in ("ACT4", "basic", "invalid", "advanced", "riscv-dv"):
        raise InvalidPackage("unsupported package schema or source")
    isa = package.get("isa")
    if not isinstance(isa, str) or not isa.startswith(("rv32", "rv64")):
        raise InvalidPackage("missing ISA")
    if supported_isa is not None and not any(isa_compatible(isa, available) for available in supported_isa):
        raise InvalidPackage(f"unsupported ISA: {isa}")
    segments = package.get("segments")
    if not isinstance(segments, list) or not segments:
        raise InvalidPackage("missing LOAD segments")
    memory: dict[int, int] = {}
    for segment in segments:
        if not isinstance(segment, dict):
            raise InvalidPackage("malformed segment")
        try:
            base, file_size, mem_size = (segment[k] for k in ("address", "file_size", "memory_size"))
            data = bytes.fromhex(segment["hex"])
        except (KeyError, ValueError, TypeError) as exc:
            raise InvalidPackage("malformed segment") from exc
        if not all(type(v) is int and v >= 0 for v in (base, file_size, mem_size)) or len(data) != file_size or mem_size < file_size:
            raise InvalidPackage("invalid segment bounds")
        if mem_size > 16 * 1024 * 1024:
            raise InvalidPackage("segment exceeds host mock limit")
        for offset in range(mem_size):
            address = base + offset
            if address in memory:
                raise InvalidPackage("overlapping segments")
            memory[address] = data[offset] if offset < file_size else 0
    entry = package.get("entry")
    oracle = package.get("oracle", {})
    if not isinstance(oracle, dict):
        raise InvalidPackage("malformed oracle")
    status = oracle.get("address")
    if type(entry) is not int or entry not in memory:
        raise InvalidPackage("entry outside initialized memory")
    expected_oracle = "act4_tohost" if package["test_source"] == "ACT4" else (
        "trap_selfcheck_tohost" if package["test_source"] == "invalid" else "selfcheck_tohost")
    if (oracle.get("type") != expected_oracle or type(status) is not int or
            any(status + i not in memory for i in range(8)) or
            oracle.get("pass_value") != 1 or
            oracle.get("failure_rule") != "odd value greater than 1"):
        raise InvalidPackage("missing tohost status word")
    if "trap_failure_codes" in oracle and (package["test_source"] != "invalid" or
                                           oracle["trap_failure_codes"] != TRAP_FAILURE_CODES):
        raise InvalidPackage("invalid trap failure codes")
    completion = package.get("completion", {})
    if not isinstance(completion, dict):
        raise InvalidPackage("invalid completion rule")
    if completion.get("type") != "tohost_write" or type(completion.get("max_cycles")) is not int or completion["max_cycles"] <= 0:
        raise InvalidPackage("invalid completion rule")
    return memory


def flat_memory_fit(package: dict, *, base: int, size: int, reset_pc: int,
                    supported_isa: set[str]) -> list[str]:
    """Explain why a sparse package cannot run in one mapped DUT memory."""
    initial_memory(package, supported_isa=supported_isa)
    if type(base) is not int or type(size) is not int or type(reset_pc) is not int or base < 0 or size <= 0:
        raise ValueError("invalid DUT memory description")
    end = base + size
    reasons = []
    required_bytes = sum(segment["memory_size"] for segment in package["segments"])
    if required_bytes > size:
        reasons.append(f"LOAD memory requirement {required_bytes} bytes exceeds {size}-byte controller memory")
    if package["entry"] != reset_pc:
        reasons.append(f"entry {package['entry']:#x} differs from reset PC {reset_pc:#x}")
    for index, segment in enumerate(package["segments"]):
        start = segment["address"]
        if start < base or start + segment["memory_size"] > end:
            reasons.append(f"LOAD segment {index} [{start:#x}, {start + segment['memory_size']:#x}) outside [{base:#x}, {end:#x})")
    status = package["oracle"]["address"]
    if status < base or status + 8 > end:
        reasons.append(f"tohost [{status:#x}, {status + 8:#x}) outside [{base:#x}, {end:#x})")
    return reasons


def outcome(package: dict, memory: dict[int, int], *, stopped: bool, timed_out: bool = False,
            trapped: bool = False) -> str:
    codes = package["oracle"].get("trap_failure_codes")
    if codes is not None and (package.get("test_source") != "invalid" or codes != TRAP_FAILURE_CODES):
        raise InvalidPackage("invalid trap failure codes")
    if timed_out:
        return "TIMEOUT"
    if trapped:
        return "UNEXPECTED_TRAP"
    address = package["oracle"]["address"]
    try:
        status_bytes = [memory[address + i] for i in range(8)]
    except KeyError as exc:
        raise InvalidPackage("status word missing from observed memory") from exc
    if any(type(byte) is not int or not 0 <= byte <= 255 for byte in status_bytes):
        raise InvalidPackage("status word contains invalid bytes")
    value = int.from_bytes(bytes(status_bytes), "little")
    if not stopped or value == 0:
        return "INCONCLUSIVE"
    if value == 1:
        return "PASS"
    if value & 1:
        if codes is not None:
            return codes.get(str(value), "SELF_CHECK_FAILURE")
        return "SELF_CHECK_FAILURE"
    return "INVALID_TEST"
