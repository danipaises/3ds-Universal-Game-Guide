#!/usr/bin/env python3
"""Recheck every regional association directly against locked public snapshots."""

import hashlib
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def audit(root=ROOT):
    lock = json.loads((root / "data/catalog-source-lock.json").read_text())
    hashes = {}
    for name, entry in lock["files"].items():
        raw = (root / "research" / name).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != entry["sha256"]:
            raise ValueError("Changed snapshot: " + name)
        hashes[name] = digest
    facts = set()
    for region, country in [
        ("USA", "US"),
        ("EUR", "GB"),
        ("JPN", "JP"),
        ("KOR", "KR"),
        ("TWN", "TW"),
    ]:
        for item in json.loads((root / f"research/list_{country}.json").read_text()):
            facts.add(
                (region, item.get("TitleID", "").upper(), item.get("Name", ""), "eshop-metadata")
            )
    for release in ET.parse(root / "research/3dsdb.xml").findall("release"):
        facts.add(
            (
                release.findtext("region"),
                (release.findtext("titleid") or "").upper(),
                release.findtext("name"),
                "physical-release-metadata",
            )
        )
    evidence = json.loads((root / "data/title-id-evidence.json").read_text())["entries"]
    bykey = {(e["gameId"], e["region"], e["titleId"]): e for e in evidence}
    if len(bykey) != len(evidence):
        raise ValueError("Duplicate evidence association")
    games = json.loads((root / "data/games.json").read_text())["games"]
    assign = {}
    checked = 0
    for game in games:
        for region, ids in game["titleIds"].items():
            for tid in ids:
                if not re.fullmatch(r"00040000[0-9A-F]{8}", tid):
                    raise ValueError("Non-base Title ID")
                if tid in assign and assign[tid] != game["id"]:
                    raise ValueError("Conflicting lookup")
                assign[tid] = game["id"]
                entry = bykey[(game["id"], region, tid)]
                for src in entry["sources"]:
                    if (region, tid, src["name"], src["dataset"]) not in facts:
                        raise ValueError("Evidence does not match snapshot: " + tid)
                    if src["datasetSha256"] not in hashes.values():
                        raise ValueError("Unpinned evidence")
                    if re.search(r"\b(demo|trailer|trial)\b", src["name"], re.I):
                        raise ValueError("Demo/trailer assigned")
                checked += 1
    if checked != len(evidence):
        raise ValueError("Orphan evidence")
    report = {
        "date": "2026-10-04",
        "catalogGames": len(games),
        "uniqueTitleIds": len(assign),
        "regionalAssociationsChecked": checked,
        "verification": dict(Counter(e["verification"] for e in evidence)),
        "snapshotSha256": hashes,
        "pendingGames": [g["id"] for g in games if not g["titleIds"]],
        "hardware": "NOT TESTED ON REAL HARDWARE",
        "scope": "Direct snapshot/value/category cross-check; not proof of regional completeness or vendor confirmation.",
    }
    (root / "docs/TITLE_ID_REAUDIT.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    audit()
