#!/usr/bin/env python3
"""Inspect actual linked ARM instructions and model the two documented SVC ABIs.

This is a bounded instruction regression, NOT a 3DS/kernel/hardware emulator.
No ROM, game memory or firmware is used. No third-party runtime is required.
"""

import argparse
import importlib.util
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("diagnostics", ROOT / "scripts/diagnostics.py")
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)


def elf_symbols(path):
    d.elf_info(path)  # Existing bounds/machine/encoding validation first.
    raw = d.limited(path, 64 * 1024 * 1024)
    h = struct.unpack_from("<16sHHIIIIIHHHHHH", raw)
    sections = [struct.unpack_from("<10I", raw, h[6] + i * 40) for i in range(h[12])]
    symbols = {}
    for table in sections:
        if table[1] != 2:  # SHT_SYMTAB
            continue
        assert table[9] == 16 and table[6] < len(sections)
        strings = sections[table[6]]
        names = raw[strings[4] : strings[4] + strings[5]]
        assert table[4] + table[5] <= len(raw)
        for offset in range(table[4], table[4] + table[5], 16):
            name, address, size, info, _, index = struct.unpack_from("<IIIBBH", raw, offset)
            if not index or name == 0:
                continue
            assert name < len(names)
            end = names.find(b"\0", name)
            assert end >= name
            label = names[name:end].decode()
            symbols.setdefault(label, []).append((address, size, info, index))
    return raw, sections, symbols


def function_bytes(path, name):
    raw, sections, symbols = elf_symbols(path)
    live = symbols.get(name, [])
    assert len(live) == 1, f"Expected one live {name} in {path}"
    address, size, info, index = live[0]
    assert info >> 4 == 1 and info & 15 == 2, "Expected strong global function"
    if size == 0:  # SDK assembly macros omit .size; bound by the next function.
        following = [
            value[0]
            for entries in symbols.values()
            for value in entries
            if value[3] == index and value[2] & 15 == 2 and value[0] > address
        ]
        assert following, "Unbounded assembly function"
        size = min(following) - address
    section = sections[index]
    offset = section[4] + address - section[3]
    assert 0 < size <= 4096 and offset >= section[4] and offset + size <= len(raw)
    return raw[offset : offset + size]


def execute_wrapper(code, flags, modern):
    """Execute the small ARM wrapper, intercept SVC with an explicit ABI model."""
    assert len(code) % 4 == 0
    words = struct.unpack("<" + "I" * (len(code) // 4), code)
    r = [0] * 16
    r[0:7] = [0xFFFF8001, 0x01E80000, 0xFFFF8001, 0x07400000, 0x44, 0x55, 0x66]
    r[13:15] = [0x10000, 0x12345678]
    saved = r[:]
    memory = {r[13]: 0x2000, r[13] + 4: flags}
    z = False
    call = None
    for word in words:
        cond = word >> 28
        assert cond in (1, 14), f"Unreviewed ARM condition {cond}"
        if cond == 1 and z:
            continue
        instruction = word & 0x0FFFFFFF
        if instruction == 0x092D0070:  # push {r4,r5,r6}
            r[13] -= 12
            for i in range(3):
                memory[r[13] + 4 * i] = r[4 + i]
        elif instruction in (0x059D400C, 0x059D5010):
            destination = (word >> 12) & 15
            r[destination] = memory[r[13] + (word & 0xFFF)]
        elif instruction == 0x03550000:  # cmp r5,#0
            z = r[5] == 0
        elif instruction == 0x01A06000:  # mov[n e] r6,r0
            r[6] = r[0]
        elif instruction == 0x03E0000D:  # mvn[n e] r0,#13
            r[0] = 0xFFFFFFF2
        elif instruction == 0x0F0000A0:
            assert call is None
            call = r[:]
            destination = r[6] if modern and r[0] == 0xFFFFFFF2 else r[0]
            effective_flags = r[5] if modern and r[0] == 0xFFFFFFF2 else 0
            assert r[1:5] == [0x01E80000, 0xFFFF8001, 0x07400000, 0x2000]
            # Old kernel treats the new magic as a nonexistent destination handle.
            r[0] = 0 if destination == 0xFFFF8001 else 0xD8E007F7
            call.append(effective_flags)
        elif instruction == 0x08BD0070:  # pop {r4,r5,r6}
            for i in range(3):
                r[4 + i] = memory[r[13] + 4 * i]
            r[13] += 12
        elif instruction == 0x012FFF1E:  # bx lr
            assert call is not None
            assert r[4:7] == saved[4:7] and r[13:15] == saved[13:15]
            return {"result": r[0], "svcR0": call[0], "svcR6": call[6], "flags": call[16]}
        else:
            raise AssertionError(f"Unreviewed instruction {word:08x}")
    raise AssertionError("Wrapper did not return")


def verify(path, probe=False):
    code = function_bytes(path, "svcMapProcessMemoryEx")
    function_bytes(path, "__system_allocateHeaps")  # Exactly ONE live strong allocator.
    results = {}
    for flags in (0, 1):
        for modern in (False, True):
            result = execute_wrapper(code, flags, modern)
            assert result["result"] == (0xD8E007F7 if flags and not modern else 0)
            assert result["flags"] == (flags if modern else 0)
            assert result["svcR0"] == (0xFFFFFFF2 if flags else 0xFFFF8001)
            results[f"flags={flags}/{'current' if modern else '13.1.1'}"] = result
    if probe:
        _, _, symbols = elf_symbols(path)
        for name in symbols:
            assert not any(
                x in name
                for x in ("ScreenImpl", "OSDImpl", "PluginMenu", "Font", "gspInit", "ncsndInit")
            ), "UI linked into MINIMAL-BOOT: " + name
        function_bytes(path, "initLib")
        function_bytes(path, "__entrypoint")
    return {"elf": path.name, "allocatorProviders": 1, "abiCases": results, "noUI": probe}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-elf", type=Path)
    args = parser.parse_args()
    report = {
        "limitation": "Instruction execution with SVC ABI models; NOT TESTED ON REAL HARDWARE",
        "variants": [
            verify(ROOT / f"plugin/default-{variant}.elf", variant == "minimal-boot")
            for variant in ["minimal-boot", "minimal", "full"]
        ],
    }
    if args.baseline_elf:
        code = function_bytes(args.baseline_elf, "svcMapProcessMemoryEx")
        report["baseline"] = execute_wrapper(code, 0, False)
        assert report["baseline"]["result"] == 0xD8E007F7
    out = ROOT / "build/arm-verification.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
