#!/usr/bin/env python3
"""Fetch checksum-pinned public build dependencies; extract regular files safely."""

import argparse
import hashlib
import json
import re
import shutil
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def extract(archive, target):
    target.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive) as tf:
        for member in tf.getmembers():
            parts = Path(member.name).parts[1:]
            if not parts:
                continue
            if any(p in {"..", ""} for p in parts) or member.issym() or member.islnk():
                raise ValueError("archive traversal/link refused")
            if not member.isfile():
                continue
            output = target.joinpath(*parts)
            if not output.resolve().is_relative_to(target.resolve()):
                raise ValueError("archive escapes destination")
            output.parent.mkdir(parents=True, exist_ok=True)
            with tf.extractfile(member) as src, output.open("wb") as dst:
                shutil.copyfileobj(src, dst)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    lock = json.loads((ROOT / "data/dependencies.lock.json").read_text())
    if not (ROOT / ".deps").resolve().is_relative_to(ROOT.resolve()) or not (
        ROOT / "research"
    ).resolve().is_relative_to(ROOT.resolve()):
        raise ValueError("dependency/cache root escapes project")
    (ROOT / "research").mkdir(exist_ok=True)
    for dep in lock["dependencies"]:
        if Path(dep["archive"]).name != dep["archive"] or not re.fullmatch(
            r"[0-9a-f]{64}", dep["sha256"]
        ):
            raise ValueError("invalid pinned archive/hash")
        archive = ROOT / "research" / dep["archive"]
        target = ROOT / dep["destination"]
        if (
            not dep["destination"].startswith(".deps/")
            or ".." in Path(dep["destination"]).parts
            or not target.resolve().is_relative_to((ROOT / ".deps").resolve())
            or not archive.resolve().is_relative_to((ROOT / "research").resolve())
        ):
            raise ValueError("dependency path escapes project")
        if not archive.exists():
            if args.offline:
                raise SystemExit(f"archive absent: {archive}")
            request = urllib.request.Request(
                dep["url"], headers={"User-Agent": "UniversalGameGuide/0.1"}
            )
            with urllib.request.urlopen(request, timeout=60) as response:
                body = response.read(32 * 1024 * 1024 + 1)
            if len(body) > 32 * 1024 * 1024:
                raise ValueError("dependency above download budget")
            archive.write_bytes(body)
        if hashlib.sha256(archive.read_bytes()).hexdigest() != dep["sha256"]:
            raise ValueError(f"checksum mismatch: {dep['name']}")
        if not target.exists():
            extract(archive, target)
        print(dep["name"] + ": SHA-256 checked")


if __name__ == "__main__":
    main()
