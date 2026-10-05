"""A32 wrapper regression with explicit SVC models; no hardware claims."""

import importlib.util
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("arm", ROOT / "scripts/verify_arm.py")
arm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(arm)

# Exact instructions, not commercial executable data.
OLD = [0xE92D0070, 0xE59D400C, 0xE59D5010, 0xE1A06000, 0xE3E0000D]
TAIL = [0xEF0000A0, 0xE8BD0070, 0xE12FFF1E]
NEW = OLD[:3] + [0xE3550000, 0x11A06000, 0x13E0000D]


def code(words):
    return struct.pack("<" + "I" * len(words), *words)


class ArmABITests(unittest.TestCase):
    def test_original_zero_flags_reproduces_invalid_handle_in_old_abi_model(self):
        self.assertEqual(arm.execute_wrapper(code(OLD + TAIL), 0, False)["result"], 0xD8E007F7)
        self.assertEqual(arm.execute_wrapper(code(OLD + TAIL), 0, True)["result"], 0)

    def test_zero_flags_works_with_both_models_preserving_callee_registers(self):
        for modern in [False, True]:
            result = arm.execute_wrapper(code(NEW + TAIL), 0, modern)
            self.assertEqual(result["result"], 0)
            self.assertEqual(result["svcR0"], 0xFFFF8001)
            self.assertEqual(result["flags"], 0)

    def test_nonzero_flags_still_use_new_abi_and_are_not_silently_dropped(self):
        result = arm.execute_wrapper(code(NEW + TAIL), 1, True)
        self.assertEqual(result["result"], 0)
        self.assertEqual(result["svcR0"], 0xFFFFFFF2)
        self.assertEqual(result["flags"], 1)
        self.assertEqual(arm.execute_wrapper(code(NEW + TAIL), 1, False)["result"], 0xD8E007F7)

    def test_rejects_unknown_or_truncated_instruction_sequences(self):
        for bad in [b"x", code([0xE1A00000]), code(NEW)]:
            self.assertRaises(AssertionError, arm.execute_wrapper, bad, 0, False)

    def test_current_physical_report_is_failure_and_new_build_requires_retest(self):
        import json

        history = json.loads((ROOT / "data/hardware-tests.json").read_text())
        latest = history["tests"][-1]
        self.assertEqual(latest["number"], 2)
        self.assertEqual(latest["status"], "FAIL")
        self.assertEqual(latest["lumaVersion"], "13.1.1")
        self.assertEqual(latest["pc"], "07005B5C")
        self.assertEqual(history["currentStatus"], "NEEDS HARDWARE RETEST")
