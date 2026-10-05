#!/usr/bin/env python3
"""Bounded, read-only inspection of 3GX v2, ARM ELF32 and Luma 1.x dumps.

Formats checked against pinned 3gxtool and Luma v13.4 sources. This is an
independent parser; stack words are candidates, never a reconstructed backtrace.
"""

import argparse
import hashlib
import json
import shutil
import struct
import subprocess
from pathlib import Path

DUMP_HEADER = struct.Struct("<IIHHHHIIIIII")


def limited(path, maximum):
    if path.stat().st_size > maximum:
        raise ValueError("File exceeds inspection limit: " + str(path))
    with path.open("rb") as file:
        raw = file.read(maximum + 1)
    if len(raw) > maximum:
        raise ValueError("File grew beyond inspection limit")
    return raw


def plugin_info(path):
    raw = limited(path, 2 * 1024 * 1024)
    if len(raw) < 160 or raw[:8] != b"3GX$0002":
        raise ValueError("Invalid 3GX v2")
    flags = struct.unpack_from("<I", raw, 48)[0]
    memory = (flags >> 2) & 3
    if memory == 3:
        raise ValueError("Reserved memory size")
    executable = struct.unpack_from("<10I", raw, 88)
    return {
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "flags": flags,
        "privateMemory": bool(flags & (1 << 8)),
        "memoryMiB": [5, 2, 10][memory],
        "codeBytes": executable[3],
        "rodataBytes": executable[4],
        "dataBytes": executable[5],
        "bssBytes": executable[6],
    }


def elf_info(path):
    raw = limited(path, 64 * 1024 * 1024)
    if len(raw) < 52 or raw[:7] != b"\x7fELF\x01\x01\x01":
        raise ValueError("Expected little-endian ARM ELF32")
    header = struct.unpack_from("<16sHHIIIIIHHHHHH", raw)
    if header[2] != 40 or header[11] != 40:
        raise ValueError("Invalid ARM ELF32 section table")
    offset, count, strings = header[6], header[12], header[13]
    if not 1 <= count <= 4096 or strings >= count or offset + count * 40 > len(raw):
        raise ValueError("Truncated ELF section table")
    sections = [struct.unpack_from("<10I", raw, offset + i * 40) for i in range(count)]
    table = sections[strings]
    if table[4] + table[5] > len(raw):
        raise ValueError("Truncated ELF string table")
    names = raw[table[4] : table[4] + table[5]]
    result, ranges = [], []
    for section in sections:
        if section[0] >= len(names):
            raise ValueError("Invalid ELF section name")
        end = names.find(b"\0", section[0])
        if end < 0:
            raise ValueError("Unterminated ELF section name")
        name = names[section[0] : end].decode("ascii")
        if section[1] != 8 and section[4] + section[5] > len(raw):
            raise ValueError("Truncated ELF section")
        result.append({"name": name, "address": section[3], "bytes": section[5]})
        if section[2] & 4 and section[5]:
            ranges.append([section[3], section[3] + section[5]])
    return {
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "entry": header[4],
        "sections": result,
        "executableRanges": ranges,
        "debugInfo": any(s["name"] == ".debug_info" and s["bytes"] for s in result),
        "debugLines": any(s["name"] == ".debug_line" and s["bytes"] for s in result),
    }


def parse_dump(raw):
    if not DUMP_HEADER.size <= len(raw) <= 1024 * 1024:
        raise ValueError("Dump truncated or exceeds 1 MiB")
    magic0, magic1, minor, major, processor, core, kind, total, regs, code, stack, extra = (
        DUMP_HEADER.unpack_from(raw)
    )
    if (magic0, magic1) != (0xDEADC0DE, 0xDEADCAFE):
        raise ValueError("Invalid Luma dump magic")
    if major != 1 or minor > 3 or processor != 11 or kind > 3:
        raise ValueError("Unsupported dump version/processor/type")
    if total != len(raw) or total != 40 + regs + code + stack + extra:
        raise ValueError("Invalid dump sizes")
    if not 68 <= regs <= 256 or regs % 4 or stack > 4096:
        raise ValueError("Invalid register/stack size")
    registers = struct.unpack_from("<17I", raw, 40)
    stack_offset = 40 + regs + code
    words = struct.unpack_from(f"<{stack // 4}I", raw, stack_offset)
    additional = raw[stack_offset + stack :]
    return {
        "format": f"{major}.{minor}",
        "processor": processor,
        "core": core,
        "exceptionType": kind,
        "registers": dict(
            zip([f"r{i}" for i in range(13)] + ["sp", "lr", "pc", "cpsr"], registers)
        ),
        "pc": registers[15],
        "lr": registers[14],
        "sp": registers[13],
        "cpsr": registers[16],
        "stackWords": list(words),
        "stackTailBytes": stack % 4,
        "titleId": f"{struct.unpack_from('<Q', additional, 8)[0]:016X}"
        if len(additional) == 16
        else None,
    }


def candidates(dump, ranges):
    def executable(value):
        return any(start <= (value & ~1) < end for start, end in ranges)

    result = []
    for label in ["pc", "lr"]:
        value = dump[label]
        result.append({"origin": label.upper(), "address": value, "inPlugin": executable(value)})
    for i, value in enumerate(dump["stackWords"]):
        if executable(value) and len(result) < 66:
            result.append(
                {"origin": f"stack+0x{i * 4:X} candidate", "address": value, "inPlugin": True}
            )
    return result


def verify_identity(manifest, variant, elf, plugin):
    expected = manifest["variants"][variant]
    for kind, path in [("elf", elf), ("plugin", plugin)]:
        if hashlib.sha256(limited(path, 64 * 1024 * 1024)).hexdigest() != expected[kind]["sha256"]:
            raise ValueError("Build identity mismatch: " + kind)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dump", type=Path)
    parser.add_argument("--elf", type=Path, required=True)
    parser.add_argument("--plugin", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--variant", choices=["minimal-boot", "minimal", "full"], required=True)
    parser.add_argument("--addr2line", default="arm-none-eabi-addr2line")
    args = parser.parse_args()
    try:
        manifest = json.loads(limited(args.manifest, 128 * 1024))
        verify_identity(manifest, args.variant, args.elf, args.plugin)
        dump = parse_dump(limited(args.dump, 1024 * 1024))
        elf = elf_info(args.elf)
        locations = candidates(dump, elf["executableRanges"])
        tool = shutil.which(args.addr2line)
        if not tool:
            raise ValueError("Install devkitARM or provide --addr2line")
        for location in locations:
            if location["inPlugin"]:
                result = subprocess.run(
                    [tool, "-f", "-C", "-i", "-e", str(args.elf), hex(location["address"] & ~1)],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                location["symbols"] = result.stdout.strip()
        dump.pop("stackWords")
        print(
            json.dumps(
                {
                    "dump": dump,
                    "variant": args.variant,
                    "locations": locations,
                    "warning": "Stack candidates are not a verified backtrace; PC is already adjusted by Luma.",
                },
                indent=2,
            )
        )
        return 0
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as error:
        parser.exit(2, str(error) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
