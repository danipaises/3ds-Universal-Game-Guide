#!/usr/bin/env python3
"""Restore public factual snapshots by hash; never fetch games, keys or prose."""

import argparse
import hashlib
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", choices=["pokemon", "catalog"])
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    if args.dataset == "pokemon":
        lock = ROOT / "data/pokemon/source-lock.json"
        dest = ROOT / "research/pokeapi"
    else:
        lock = ROOT / "data/catalog-source-lock.json"
        dest = ROOT / "research"
    if not dest.resolve().is_relative_to(ROOT.resolve()):
        raise SystemExit("Snapshot root escapes project")
    dest.mkdir(parents=True, exist_ok=True)
    for name, source in json.loads(lock.read_text())["files"].items():
        if Path(name).name != name or not re.fullmatch(r"[0-9a-f]{64}", source["sha256"]):
            raise SystemExit("Invalid filename/hash in factual snapshot lock")
        p = dest / name
        if not p.resolve().is_relative_to(dest.resolve()):
            raise SystemExit("Snapshot path escapes destination")
        if not p.exists():
            if args.offline:
                raise SystemExit(f"Snapshot absent: {name}")
            if not source["url"].startswith(
                ("https://raw.githubusercontent.com/", "https://3dsdb.com/")
            ):
                raise SystemExit("Unapproved factual-source host")
            request = urllib.request.Request(
                source["url"], headers={"User-Agent": "UniversalGameGuide/0.1"}
            )
            with urllib.request.urlopen(request, timeout=60) as response:
                raw = response.read(32 * 1024 * 1024 + 1)
            if len(raw) > 32 * 1024 * 1024:
                raise SystemExit("Snapshot exceeds budget")
            if hashlib.sha256(raw).hexdigest() != source["sha256"]:
                raise SystemExit(
                    f"Remote snapshot changed: {name}; do not silently accept new facts"
                )
            p.write_bytes(raw)
        if hashlib.sha256(p.read_bytes()).hexdigest() != source["sha256"]:
            raise SystemExit(f"Snapshot changed: {name}")
        print(f"{name}: SHA-256 checked")


if __name__ == "__main__":
    main()
