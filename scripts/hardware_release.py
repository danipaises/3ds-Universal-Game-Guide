#!/usr/bin/env python3
"""Package the existing six-guide test with three matched binaries and symbols."""

import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def build_retest(root=ROOT, lang="pt-BR"):
    b = module(root / "tools/guide-builder/builder.py", "retest_builder")
    d = module(root / "scripts/diagnostics.py", "diagnostics")
    b.require(lang == "pt-BR", "Reteste atual usa apenas PT-BR")
    version = b.version(root)
    b.coverage(root, lang)
    identity = {"version": version, "status": "NEEDS HARDWARE RETEST", "variants": {}}
    for variant in ["minimal-boot", "minimal", "full"]:
        base = root / "plugin" / f"default-{variant}"
        plugin = d.plugin_info(base.with_suffix(".3gx"))
        elf = d.elf_info(base.with_suffix(".elf"))
        b.require(
            not plugin["privateMemory"] and plugin["memoryMiB"] == 5, "Unexpected memory flags"
        )
        b.require(elf["debugInfo"] and elf["debugLines"], "ELF debug symbols missing")
        map_path = base.with_suffix(".map")
        b.require(map_path.stat().st_size > 1024, "MAP missing or empty")
        identity["variants"][variant] = {
            "plugin": plugin,
            "elf": elf,
            "map": {
                "sha256": hashlib.sha256(map_path.read_bytes()).hexdigest(),
                "bytes": map_path.stat().st_size,
            },
        }
    archive_name = f"UniversalGameGuide-PTBR-Hardware-Test-v{version}.zip"
    result = b.package(root, lang, root / "plugin/default-minimal-boot.3gx", True, archive_name)
    stage = root / "build/hardware-test"
    diagnostic = stage / "diagnostics"
    diagnostic.mkdir()
    for variant in ["minimal-boot", "minimal", "full"]:
        shutil.copy2(root / f"plugin/default-{variant}.3gx", diagnostic / f"default-{variant}.3gx")
    encoded = json.dumps(identity, indent=2) + "\n"
    (diagnostic / "BUILD.json").write_text(encoded)
    for name in ["HARDWARE_RETEST.md", "CHANGELOG.md"]:
        shutil.copy2(root / name, stage / name)
    out = stage / "3ds/UniversalGameGuide"
    manifest = b.read_json(out / "manifest.json")
    manifest["installedVariant"] = "minimal-boot"
    manifest["switchableVariants"] = ["minimal-boot", "minimal", "full"]
    manifest["currentBinaryHardwareTested"] = False
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    checks = {
        p.relative_to(stage).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(stage.rglob("*"))
        if p.is_file() and p != out / "SHA256SUMS.txt"
    }
    (out / "SHA256SUMS.txt").write_text("".join(f"{sha}  {path}\n" for path, sha in checks.items()))
    archive = Path(result["archive"])
    result["sha256"] = b.write_zip(stage, archive)
    symbols = root / "build/hardware-symbols"
    if symbols.exists():
        shutil.rmtree(symbols)
    symbols.mkdir()
    for variant in ["minimal-boot", "minimal", "full"]:
        for ext in [".elf", ".map", ".3gx"]:
            shutil.copy2(
                root / f"plugin/default-{variant}{ext}", symbols / f"default-{variant}{ext}"
            )
    (symbols / "BUILD.json").write_text(encoded)
    shutil.copy2(root / "scripts/diagnostics.py", symbols / "diagnostics.py")
    shutil.copy2(root / "HARDWARE_RETEST.md", symbols / "HARDWARE_RETEST.md")
    shutil.copy2(out / "LICENSES.txt", symbols / "LICENSES.txt")
    symbols_zip = root / "dist" / f"UniversalGameGuide-Debug-Symbols-v{version}.zip"
    symbols_sha = b.write_zip(symbols, symbols_zip)
    source, source_sha = b.source_package(root)
    sums = [
        (result["sha256"], archive.name),
        (symbols_sha, symbols_zip.name),
        (source_sha, source.name),
    ]
    (root / "dist/SHA256SUMS.txt").write_text("".join(f"{sha}  {name}\n" for sha, name in sums))
    return {
        "hardware": result,
        "symbols": str(symbols_zip),
        "symbolsSha256": symbols_sha,
        "source": str(source),
        "sourceSha256": source_sha,
        "status": "NEEDS HARDWARE RETEST",
    }


if __name__ == "__main__":
    print(json.dumps(build_retest(), indent=2))
