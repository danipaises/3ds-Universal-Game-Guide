"""Synthetic fixtures test parser bounds and build identity, not hardware boot."""

import hashlib
import importlib.util
import json
import struct
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("diagnostics", ROOT / "scripts/diagnostics.py")
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)


def dump():
    regs = [0] * 17
    regs[13:17] = [0x06010000, 0x07000121, 0x07000110, 0x20]
    stack = struct.pack("<3I", 0x07000130, 0x00101234, 0x06000100)
    extra = b"test\0\0\0\0" + struct.pack("<Q", 0x0004000000054000)
    total = 40 + 68 + len(stack) + len(extra)
    return (
        d.DUMP_HEADER.pack(
            0xDEADC0DE, 0xDEADCAFE, 3, 1, 11, 0, 3, total, 68, 0, len(stack), len(extra)
        )
        + struct.pack("<17I", *regs)
        + stack
        + extra
    )


class DiagnosticsTests(unittest.TestCase):
    def test_dump_registers_and_title(self):
        parsed = d.parse_dump(dump())
        self.assertEqual(parsed["pc"], 0x07000110)
        self.assertEqual(parsed["lr"], 0x07000121)
        self.assertEqual(parsed["titleId"], "0004000000054000")
        self.assertEqual(parsed["registers"]["pc"], parsed["pc"])
        self.assertEqual(parsed["registers"]["r0"], 0)
        # Luma copies to the page boundary; a corrupt/unaligned SP can leave
        # valid trailing bytes that are not complete stack words.
        unaligned = bytearray(dump())
        unaligned[120:120] = b"x"
        struct.pack_into("<I", unaligned, 20, len(unaligned))
        struct.pack_into("<I", unaligned, 32, 13)
        self.assertEqual(d.parse_dump(unaligned)["stackTailBytes"], 1)

    def test_dump_rejects_truncation_magic_and_size(self):
        raw = dump()
        for bad in [raw[:39], raw[:-1], b"x" + raw[1:], raw + b"x"]:
            with self.subTest(size=len(bad)):
                self.assertRaises(ValueError, d.parse_dump, bad)
        for offset, value in [(10, 2), (12, 9), (24, 67), (32, 8192)]:
            bad = bytearray(raw)
            struct.pack_into("<H" if offset < 16 else "<I", bad, offset, value)
            self.assertRaises(ValueError, d.parse_dump, bad)

    def test_stack_candidates_are_filtered_and_pc_not_readjusted(self):
        parsed = d.parse_dump(dump())
        addresses = d.candidates(parsed, [[0x07000100, 0x07000200]])
        self.assertEqual(len(addresses), 3)
        self.assertEqual(addresses[0]["address"], parsed["pc"])
        self.assertIn("candidate", addresses[-1]["origin"])
        parsed["pc"] = 0x00101234
        self.assertFalse(d.candidates(parsed, [[0x07000100, 0x07000200]])[0]["inPlugin"])

    def test_binary_memory_flags(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "test.3gx"
            raw = bytearray(160)
            raw[:8] = b"3GX$0002"
            p.write_bytes(raw)
            self.assertFalse(d.plugin_info(p)["privateMemory"])
            self.assertEqual(d.plugin_info(p)["memoryMiB"], 5)
            struct.pack_into("<I", raw, 48, (1 << 8) | (1 << 2))
            p.write_bytes(raw)
            self.assertTrue(d.plugin_info(p)["privateMemory"])
            self.assertEqual(d.plugin_info(p)["memoryMiB"], 2)
            struct.pack_into("<I", raw, 48, 3 << 2)
            p.write_bytes(raw)
            self.assertRaises(ValueError, d.plugin_info, p)

    def test_symbols_must_match_same_binary(self):
        with tempfile.TemporaryDirectory() as temp:
            p, e = Path(temp) / "test.3gx", Path(temp) / "test.elf"
            p.write_bytes(b"binary")
            e.write_bytes(b"ELF")
            manifest = {
                "variants": {
                    "full": {
                        "plugin": {"sha256": hashlib.sha256(b"binary").hexdigest()},
                        "elf": {"sha256": hashlib.sha256(b"ELF").hexdigest()},
                    }
                }
            }
            d.verify_identity(manifest, "full", e, p)
            e.write_bytes(b"another build")
            self.assertRaises(ValueError, d.verify_identity, manifest, "full", e, p)

    def test_invalid_elf(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "test.elf"
            for raw in [b"", b"\x7fELF\x02\x01\x01" + bytes(100), bytes(52)]:
                p.write_bytes(raw)
                self.assertRaises(ValueError, d.elf_info, p)

    def test_real_report_remains_failure_not_retest_success(self):
        report = json.loads((ROOT / "data/hardware-tests.json").read_text())
        self.assertEqual(report["currentStatus"], "NEEDS HARDWARE RETEST")
        self.assertFalse(report["tests"][0]["overlayOpened"])
        self.assertEqual(report["tests"][0]["version"], "0.2.0-alpha")


if __name__ == "__main__":
    unittest.main()
