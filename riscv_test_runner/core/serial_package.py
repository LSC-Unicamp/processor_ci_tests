"""Load a fitting sparse package through ProcessorCI's existing serial API."""
from __future__ import annotations

import re

from riscv_test_runner.core.package import InvalidPackage, flat_memory_fit, initial_memory, outcome

RESPONSE_MAGIC = b"luck"


def read_act_diagnostics(device, base: int) -> dict:
    """Read the CV32E40S controller's 1024-byte virtual-printer ring."""
    def word(address: int) -> int:
        raw = device.read_memory(address)
        if len(raw) != 4:
            raise RuntimeError(f"short ACT diagnostic read at {address:#x}")
        return int.from_bytes(raw, "big")

    count = word(base)
    capacity = word(base + 4)
    if capacity != 1024:
        raise RuntimeError(f"unexpected ACT diagnostic capacity: {capacity}")
    start = max(0, count - capacity)
    cached: dict[int, int] = {}
    characters = []
    for offset in range(start, count):
        index = offset % capacity
        address = base + 0x100 + (index & ~3)
        if address not in cached:
            cached[address] = word(address)
        characters.append((cached[address] >> (8 * (index & 3))) & 0xff)
    message = bytes(characters).decode("utf-8", errors="replace")
    cause = re.search(r"XCAUSE:\s+0x([0-9a-fA-F]+)", message)
    epc = re.search(r"XEPC:\s+0x([0-9a-fA-F]+)", message)
    trap = "TRAP FAILURE DIAGNOSTICS" in message and cause is not None and epc is not None
    return {"count": count, "truncated": count > capacity, "text": message,
            "unexpected_trap": trap,
            "trap_cause": int(cause.group(1), 16) if trap else None,
            "trap_epc": int(epc.group(1), 16) if trap else None}


def run_package(device, package: dict, *, supported_isa: set[str],
                memory_base: int, memory_size: int, reset_pc: int,
                host_timeout: float = 30.0, diagnostic_base: int | None = None) -> dict:
    """Run a package on one flat memory; return the observed host result.

    The controller's end-address logic does not prove a write or report a trap
    cause. PASS therefore requires its completion response and a readback of
    the self-checking status word. This function does not establish RTL or
    hardware correctness by itself.
    """
    memory = initial_memory(package, supported_isa=supported_isa)
    reasons = flat_memory_fit(package, base=memory_base, size=memory_size,
                              reset_pc=reset_pc, supported_isa=supported_isa)
    if reasons:
        raise InvalidPackage("DUT package does not fit: " + "; ".join(reasons))
    if memory_base != 0:
        raise InvalidPackage("serial adapter currently requires zero-based controller memory")
    status = package["oracle"]["address"]
    if memory_base % 4 or memory_size % 4 or status % 4 or memory_base + memory_size > 1 << 32:
        raise InvalidPackage("controller requires aligned 32-bit memory and status addresses")
    cycles = package["completion"]["max_cycles"]
    if cycles > 0xffffff:
        raise InvalidPackage("controller timeout exceeds 24-bit command range")
    if any(memory[status + offset] for offset in range(8)):
        raise InvalidPackage("tohost must be zero before execution")

    # Write the whole mapped RAM to remove stale bytes between sparse segments.
    words = [int.from_bytes(bytes(memory.get(address + offset, 0) for offset in range(4)), "little")
             for address in range(memory_base, memory_base + memory_size, 4)]
    device.stop_clk()
    if diagnostic_base is not None:
        if diagnostic_base % 4 or diagnostic_base < memory_base + memory_size:
            raise InvalidPackage("diagnostic region must be aligned and above program RAM")
        device.write_memory(diagnostic_base, 0)
    device.load_msb_accumulator(memory_base >> 8)
    device.load_lsb_accumulator(memory_base & 0xff)
    device.write_from_accumulator(len(words), words)
    device.set_timeout(cycles)
    device.set_execution_end_address(status >> 2)
    response = device.execute_until_stop(host_timeout=host_timeout)
    if len(response) != 8 or response[:4] != RESPONSE_MAGIC:
        raise RuntimeError(f"invalid controller completion response: {response.hex()}")
    completion_word = int.from_bytes(response[4:], "big")
    elapsed_cycles = completion_word >> 1
    stopped = bool(completion_word & 1) and elapsed_cycles < cycles
    observed = dict(memory)
    for address in (status & ~3, (status & ~3) + 4):
        raw = device.read_memory(address)
        if len(raw) != 4:
            raise RuntimeError(f"short status read at {address:#x}: {len(raw)}/4 bytes")
        value = int.from_bytes(raw, "big")
        for offset in range(4):
            observed[address + offset] = (value >> (8 * offset)) & 0xff
    result = outcome(package, observed, stopped=stopped, timed_out=not stopped)
    diagnostics = None
    if diagnostic_base is not None and result in ("SELF_CHECK_FAILURE", "TIMEOUT"):
        diagnostics = read_act_diagnostics(device, diagnostic_base)
        if result == "SELF_CHECK_FAILURE" and diagnostics["unexpected_trap"]:
            result = "UNEXPECTED_TRAP"
    return {"outcome": result, "completion_word": completion_word,
            "elapsed_cycles": elapsed_cycles,
            "tohost": int.from_bytes(bytes(observed[status + i] for i in range(8)), "little"),
            "diagnostics": diagnostics,
            "hardware_validated": False}
