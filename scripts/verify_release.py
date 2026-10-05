#!/usr/bin/env python3
"""Verify all packaged SHA-256 entries, SD-root paths, sources and guide CRCs."""

import hashlib
import argparse
import importlib.util
import json
import struct
import tempfile
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("builder", ROOT / "tools/guide-builder/builder.py")
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


def verify_runtime(archive, hardware=False):
    expected = archive.with_suffix(".zip.sha256").read_text().split()[0]
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == expected, "ZIP SHA mismatch"
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        assert len(names) == len(set(names)), "duplicate ZIP entry"
        assert "luma/plugins/default.3gx" in names
        assert z.read("luma/plugins/default.3gx")[:8] == b"3GX$0002"
        assert not any(".." in Path(n).parts or n.startswith("/") or "\\" in n for n in names)
        assert not any(n.endswith((".cia", ".3ds", ".cxi", ".3dsx", ".sav", ".env")) for n in names)
        prefix = "3ds/UniversalGameGuide/"
        assert not any(
            n == prefix + "config.bin" or n.startswith(prefix + "state/") and n.endswith(".bin")
            for n in names
        ), "user state must not be overwritten"
        sums = z.read(prefix + "SHA256SUMS.txt").decode().splitlines()
        listed = set()
        for line in sums:
            sha, name = line.split("  ", 1)
            assert hashlib.sha256(z.read(name)).hexdigest() == sha, name
            listed.add(name)
        assert listed == set(names) - {prefix + "SHA256SUMS.txt"}, "unhashed file"
        with tempfile.TemporaryDirectory() as temp:
            z.extractall(temp)
            packs = pages = search_records = tiles = 0
            for p in Path(temp).rglob("*.ugg"):
                b.verify_pack(p)
                packs += 1
                raw = p.read_bytes()
                count, fingerprint = struct.unpack_from("<II", raw, 4)
                pages += count
                search = p.with_suffix(".ugs").read_bytes()
                magic, records, linked = struct.unpack_from("<4sII", search)
                assert magic == b"UGS2" and linked == fingerprint
                assert records <= 131072 and len(search) == 12 + records * 68
                search_records += records
                previous = None
                for offset in range(12, len(search), 68):
                    term, page = struct.unpack_from("<64sI", search, offset)
                    assert b"\0" in term and page < count
                    word = term.split(b"\0", 1)[0].decode("utf-8")
                    key = (word, page)
                    assert previous is None or key > previous, "unsorted/duplicate search record"
                    previous = key
            for p in Path(temp).rglob("*.ugm"):
                raw = p.read_bytes()
                magic, levels, crc = struct.unpack_from("<4sII", raw)
                assert magic == b"UGM1" and 1 <= levels <= 3
                assert len(raw) == 12 + levels * 8 and zlib.crc32(raw[12:]) == crc
                for level in range(levels):
                    columns, rows = struct.unpack_from("<II", raw, 12 + level * 8)
                    assert 1 <= columns <= 64 and 1 <= rows <= 64
                    for y in range(rows):
                        for x in range(columns):
                            assert p.with_name(f"{p.stem}-{level}-{x}-{y}.ugi").is_file()
            for p in Path(temp).rglob("*.ugi"):
                raw = p.read_bytes()
                magic, width, height, crc = struct.unpack_from("<4sIII", raw)
                assert magic == b"UGI1" and 1 <= width <= 320 and 1 <= height <= 192
                assert len(raw) == 16 + width * height * 2 and zlib.crc32(raw[16:]) == crc
                tiles += 1
            raw = (Path(temp) / prefix / "titles.bin").read_bytes()
            magic, title_count = struct.unpack_from("<4sI", raw)
            assert magic == b"UGT1" and len(raw) == 8 + title_count * b.TITLE.size
            previous = 0
            for offset in range(8, len(raw), b.TITLE.size):
                tid, gid, name = b.TITLE.unpack_from(raw, offset)
                assert tid > previous and tid >> 32 == 0x00040000
                assert b"\0" in gid and b.slug(gid.split(b"\0", 1)[0].decode("ascii"))
                assert b"\0" in name
                name.split(b"\0", 1)[0].decode("utf-8")
                previous = tid
            report = {
                "files": len(names),
                "hashes": len(sums),
                "packs": packs,
                "pages": pages,
                "titleIds": title_count,
                "searchRecords": search_records,
                "tiles": tiles,
                "sha256": expected,
            }
            assert packs == (6 if hardware else 67)
            assert title_count == (22 if hardware else 211)
            assert not any(
                "/source/" in n or n.endswith((".py", ".cpp", ".hpp", ".elf", ".pyc"))
                for n in names
            )
            assert ("profile=hardware-test" in z.read(prefix + "VERSION").decode()) == hardware
            for path in Path(temp).rglob("*.ugr"):
                raw = path.read_bytes()
                magic, old, new, count, crc = struct.unpack_from("<4sIIII", raw)
                assert magic == b"UGR1" and 0 < count <= 1024
                assert len(raw) == 20 + 4 * count and zlib.crc32(raw[20:]) == crc
                assert new == struct.unpack_from("<I", path.with_suffix(".ugg").read_bytes(), 8)[0]
            return report


def verify_source(archive):
    assert (
        hashlib.sha256(archive.read_bytes()).hexdigest()
        == archive.with_suffix(".zip.sha256").read_text().split()[0]
    )
    with zipfile.ZipFile(archive) as source:
        names = source.namelist()
        assert len(names) == len(set(names))
        for required in [
            "builder.py",
            "VERSION",
            "pyproject.toml",
            ".gitignore",
            ".gitattributes",
            "plugin/source/main.cpp",
            "third-party-source.zip",
        ]:
            assert required in names, "incomplete build source"
        assert not any(".." in Path(n).parts or n.startswith("/") or "\\" in n for n in names)
        assert not any(
            n.endswith(
                (".3gx", ".elf", ".map", ".o", ".d", ".a", ".pyc", ".env", ".sav", ".cia", ".3ds")
            )
            for n in names
        )
        assert source.read("VERSION").decode().strip() == b.version(ROOT)
        with tempfile.TemporaryDirectory() as temp:
            bundle = Path(temp) / "upstream.zip"
            bundle.write_bytes(source.read("third-party-source.zip"))
            with zipfile.ZipFile(bundle) as upstream:
                lock = json.loads(upstream.read("dependencies.lock.json"))
                for dependency in lock["dependencies"]:
                    raw = upstream.read("archives/" + dependency["archive"])
                    assert hashlib.sha256(raw).hexdigest() == dependency["sha256"]
        return {"files": len(names), "sha256": hashlib.sha256(archive.read_bytes()).hexdigest()}


def verify_retest():
    spec = importlib.util.spec_from_file_location("diagnostics", ROOT / "scripts/diagnostics.py")
    d = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(d)
    version = b.version(ROOT)
    installer = ROOT / f"dist/UniversalGameGuide-PTBR-Hardware-Test-v{version}.zip"
    symbols = ROOT / f"dist/UniversalGameGuide-Debug-Symbols-v{version}.zip"
    hardware = verify_runtime(installer, True)
    with zipfile.ZipFile(installer) as sd, zipfile.ZipFile(symbols) as debug:
        identity = json.loads(sd.read("diagnostics/BUILD.json"))
        assert debug.read("BUILD.json") == sd.read("diagnostics/BUILD.json")
        assert identity["version"] == version and identity["status"] == "NEEDS HARDWARE RETEST"
        assert sd.read("luma/plugins/default.3gx") == sd.read("diagnostics/default-minimal.3gx")
        assert "LICENSES.txt" in debug.namelist()
        with tempfile.TemporaryDirectory() as temp:
            for variant in ["minimal", "full"]:
                for ext, kind in [(".3gx", "plugin"), (".elf", "elf"), (".map", "map")]:
                    name = f"default-{variant}{ext}"
                    raw = debug.read(name)
                    assert (
                        hashlib.sha256(raw).hexdigest()
                        == identity["variants"][variant][kind]["sha256"]
                    )
                    if ext == ".3gx":
                        assert raw == sd.read("diagnostics/" + name)
                    p = Path(temp) / name
                    p.write_bytes(raw)
                    if ext == ".elf":
                        info = d.elf_info(p)
                        assert info["debugInfo"] and info["debugLines"]
                    if ext == ".3gx":
                        info = d.plugin_info(p)
                        assert not info["privateMemory"] and info["memoryMiB"] == 5
        manifest = json.loads(sd.read("3ds/UniversalGameGuide/manifest.json"))
        assert manifest["installedVariant"] == "minimal"
        assert manifest["hardwareStatus"] == "NEEDS HARDWARE RETEST"
    return {
        "hardware": hardware,
        "symbols": {
            "files": len(debug.namelist()),
            "sha256": hashlib.sha256(symbols.read_bytes()).hexdigest(),
        },
        "source": verify_source(ROOT / f"dist/3DS-Universal-Game-Guide-SOURCE-v{version}.zip"),
        "previousHardwareResult": "TESTED ON REAL HARDWARE — CURRENT RESULT: CRASH ON PLUGIN LOAD (0.2.0-alpha)",
        "currentStatus": "NEEDS HARDWARE RETEST",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--hardware-retest", action="store_true")
    args = parser.parse_args()
    version = b.version(ROOT)
    report = (
        verify_retest()
        if args.hardware_retest
        else {
            "runtime": verify_runtime(ROOT / f"dist/UniversalGameGuide-PTBR-v{version}.zip"),
            "hardware": verify_runtime(
                ROOT / "dist/UniversalGameGuide-PTBR-Hardware-Test.zip", True
            ),
            "source": verify_source(ROOT / f"dist/3DS-Universal-Game-Guide-SOURCE-v{version}.zip"),
            "hardwareStatus": b.hardware_status(ROOT),
        }
    )
    for line in (ROOT / "dist/SHA256SUMS.txt").read_text().splitlines():
        sha, name = line.split("  ", 1)
        assert hashlib.sha256((ROOT / "dist" / name).read_bytes()).hexdigest() == sha
    (ROOT / "build/release-verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
