#!/usr/bin/env python3
"""Ship pinned upstream sources and licenses with the binary (no build objects)."""

import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
lock = json.loads((ROOT / "data/dependencies.lock.json").read_text())
for dependency in lock["dependencies"]:
    archive = ROOT / "research" / dependency["archive"]
    if hashlib.sha256(archive.read_bytes()).hexdigest() != dependency["sha256"]:
        raise RuntimeError("Upstream archive checksum mismatch: " + dependency["archive"])
(ROOT / "build").mkdir(exist_ok=True)
with zipfile.ZipFile(
    ROOT / "build/third-party-source.zip", "w", zipfile.ZIP_DEFLATED, compresslevel=9
) as z:
    for d in lock["dependencies"]:
        # The verified pristine archives are enough to reconstruct dependencies.
        p = ROOT / "research" / d["archive"]
        info = zipfile.ZipInfo("archives/" + p.name, (2026, 10, 4, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info, p.read_bytes())
    info = zipfile.ZipInfo("dependencies.lock.json", (2026, 10, 4, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    z.writestr(info, (ROOT / "data/dependencies.lock.json").read_bytes())
    info = zipfile.ZipInfo("CTRPF_FILESYSTEM.patch", (2026, 10, 4, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    z.writestr(info, (ROOT / "docs/CTRPF_FILESYSTEM.patch").read_bytes())
    for p in sorted((ROOT / "docs/licenses").glob("*")):
        info = zipfile.ZipInfo("licenses/" + p.name, (2026, 10, 4, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info, p.read_bytes())
print("build/third-party-source.zip: pristine pinned source archives and license notices")
