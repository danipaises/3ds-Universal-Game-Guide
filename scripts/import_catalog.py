#!/usr/bin/env python3
"""Curate public Title ID facts. Never derive or fabricate an ID from another region.
Requires snapshots in research/. Classification rules live in data/catalog-rules.json.
"""

import hashlib
import json
import re
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-10-04"


def norm(s):
    s = re.sub(r"<[^>]*>", " ", s).replace("™", "").replace("’", "'").replace("&", " and ")
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    return re.sub(r"[\W_]+", " ", s.lower()).strip()


def main():
    rules = json.loads((ROOT / "data/catalog-rules.json").read_text())
    facts = []
    source_lock = json.loads((ROOT / "data/catalog-source-lock.json").read_text())
    revision = source_lock["eshopCommit"]
    for filename, metadata in source_lock["files"].items():
        if (
            Path(filename).name != filename
            or hashlib.sha256((ROOT / "research" / filename).read_bytes()).hexdigest()
            != metadata["sha256"]
        ):
            raise ValueError(
                f"Snapshot ausente/alterado: {filename}; não atualizar a auditoria silenciosamente"
            )
    for region, country in [
        ("USA", "US"),
        ("EUR", "GB"),
        ("JPN", "JP"),
        ("KOR", "KR"),
        ("TWN", "TW"),
    ]:
        f = ROOT / f"research/list_{country}.json"
        checksum = hashlib.sha256(f.read_bytes()).hexdigest()
        source = f"https://github.com/hax0kartik/3dsdb/blob/{revision}/jsons/list_{country}.json"
        for item in json.loads(f.read_text()):
            tid = item.get("TitleID", "").upper()
            if re.fullmatch(r"00040000[0-9A-F]{8}", tid):
                facts.append(
                    {
                        "name": item["Name"],
                        "titleId": tid,
                        "region": region,
                        "source": source,
                        "datasetSha256": checksum,
                        "retrieved": DATE,
                        "dataset": "eshop-metadata",
                    }
                )
    f = ROOT / "research/3dsdb.xml"
    checksum = hashlib.sha256(f.read_bytes()).hexdigest()
    for e in ET.parse(f).findall("release"):
        tid = (e.findtext("titleid") or "").upper()
        if re.fullmatch(r"00040000[0-9A-F]{8}", tid):
            facts.append(
                {
                    "name": e.findtext("name"),
                    "titleId": tid,
                    "region": e.findtext("region"),
                    "source": "https://3dsdb.com/xml.php",
                    "datasetSha256": checksum,
                    "retrieved": DATE,
                    "dataset": "physical-release-metadata",
                }
            )
    bygame = {g["id"]: [] for g in rules}
    # Explicit names only. Demos and Virtual Console never enter via franchise substring.
    for fact in facts:
        name = norm(fact["name"])
        if any(
            s in name
            for s in [
                " demo",
                "trial",
                "trailer",
                "treatment version",
                "experience version",
                "special experience",
                "virtual card album",
            ]
        ):
            continue
        scores = [
            (len(norm(alias)), g["id"])
            for g in rules
            for alias in g["aliases"]
            if re.search(r"\b" + re.escape(norm(alias)) + r"\b", name)
        ]
        best = max((score for score, _ in scores), default=0)
        matches = sorted({gid for score, gid in scores if score == best})
        if len(matches) > 1:
            raise ValueError(f"Ambiguous rule {matches}: {fact['name']}")
        if matches:
            bygame[matches[0]].append(fact)
    # Enrich exact matches with other storefronts. Same numeric ID may be sold in many regions.
    assignment = {}
    for gid, rows in bygame.items():
        for row in rows:
            if row["titleId"] in assignment and assignment[row["titleId"]] != gid:
                raise ValueError("Title ID conflict")
            assignment[row["titleId"]] = gid
    for fact in facts:
        gid = assignment.get(fact["titleId"])
        if (
            gid
            and fact not in bygame[gid]
            and not any(s in norm(fact["name"]) for s in [" demo", "trial", "trailer"])
        ):
            bygame[gid].append(fact)
    games = []
    evidence = []
    pilots = {
        "super-mario-3d-land",
        "pokemon-x",
        "zelda-ocarina-of-time-3d",
        "kirby-triple-deluxe",
        "luigis-mansion-dark-moon",
    }
    for rule in rules:
        rows = bygame[rule["id"]]
        titleids = {}
        for row in rows:
            if row["region"] == "WLD":
                continue  # worldwide is not evidence for every individual regional release
            titleids.setdefault(row["region"], set()).add(row["titleId"])
        game = {k: rule[k] for k in ["id", "name", "franchise", "category"]}
        game.update(
            {
                "platform": "Nintendo 3DS",
                "titleIds": {r: sorted(ids) for r, ids in sorted(titleids.items())},
                "guideStatus": "pilot-partial" if rule["id"] in pilots else "missing",
                "guides": {
                    "pt-BR": "pilot-partial" if rule["id"] in pilots else "missing",
                    "en-US": "missing",
                },
                "hardwareStatus": "not-tested",
                "regionalCoverage": "observed-variants-not-proven-exhaustive",
            }
        )
        for lang in ["pt-BR", "en-US"]:
            guidefile = ROOT / "guides" / lang / rule["id"] / "guide.json"
            game["guides"][lang] = (
                json.loads(guidefile.read_text())["coverage"] if guidefile.exists() else "missing"
            )
        game["guideStatus"] = game["guides"]["pt-BR"]
        if "CHN" in game["titleIds"]:
            game["regionNotes"] = {
                "CHN": "Rótulo da fonte comunitária; lançamento chinês/iQue não confirmado. O mesmo ID consta como TWN."
            }
        if rule.get("note"):
            game["note"] = rule["note"]
        games.append(game)
        grouped = {}
        for row in rows:
            key = (row["region"], row["titleId"])
            if key[0] == "WLD":
                continue
            grouped.setdefault(key, [])
            if not any(
                r["source"] == row["source"] and r["name"] == row["name"] for r in grouped[key]
            ):
                grouped[key].append(row)
        for (region, tid), sources in sorted(grouped.items()):
            evidence.append(
                {
                    "gameId": rule["id"],
                    "region": region,
                    "titleId": tid,
                    "verification": "NEEDS_VERIFICATION"
                    if region == "CHN"
                    else "cross-checked"
                    if len({s["dataset"] for s in sources}) > 1
                    else "single-source",
                    "sources": sources,
                }
            )
    for path, value in [
        ("data/games.json", {"schemaVersion": 1, "games": games}),
        (
            "data/title-id-evidence.json",
            {"schemaVersion": 1, "retrieved": DATE, "entries": evidence},
        ),
    ]:
        (ROOT / path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    for franchise in ["mario", "pokemon", "zelda", "kirby"]:
        (ROOT / f"data/franchises/{franchise}.json").write_text(
            json.dumps(
                {"gameIds": [g["id"] for g in games if g["franchise"] == franchise]}, indent=2
            )
            + "\n"
        )
    lines = [
        "# Auditoria dos Title IDs",
        "",
        f"Consulta: {DATE}. Metadados públicos; nenhum conteúdo de ROM foi baixado.",
        "",
        "Verificado aqui significa conferência de metadados, não teste do plugin em hardware. Dois bancos comunitários não substituem confirmação no console. GB é o storefront europeu; TWN pode comercializar um executável compartilhado com USA/JPN. Não supor IDs diferentes por região nem interpretar ausência como inexistência.",
        "",
        "As variantes observadas estão abaixo. A exaustividade regional e títulos ainda sem ID seguem pendentes. Atualizações (0004000E), DLC (0004008C), demos e Virtual Console foram excluídos.",
        "",
        "| Jogo | Região | Title ID | Evidência | Fontes |",
        "|---|---|---|---|---|",
    ]
    names = {g["id"]: g["name"] for g in games}
    for e in evidence:
        refs = "; ".join(
            f"[{s['dataset']}]({s['source']})"
            for s in {s["source"]: s for s in e["sources"]}.values()
        )
        lines.append(
            f"| {names[e['gameId']]} | {e['region']} | `{e['titleId']}` | {e['verification']} | {refs} |"
        )
    lines += ["", "## Pendências de catálogo", ""] + [
        f"- {g['name']}: nenhum ID observado nas fontes baixadas; não empacotado no índice."
        for g in games
        if not g["titleIds"]
    ]
    (ROOT / "TITLE_ID_AUDIT.md").write_text("\n".join(lines) + "\n")
    print(
        f"{len(games)} títulos catalogados; {len(evidence)} variantes regionais; {sum(not g['titleIds'] for g in games)} sem ID"
    )


if __name__ == "__main__":
    main()
