#!/usr/bin/env python3
"""Cache public textual references for factual authoring; never package this cache."""

import concurrent.futures
import hashlib
import json
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "research/stage2-content"


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.skip += 1
        if tag in {"p", "li", "tr", "h1", "h2", "h3", "h4", "br"} and not self.skip:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.skip = max(0, self.skip - 1)
        if tag in {"p", "li", "tr", "h1", "h2", "h3", "h4"} and not self.skip:
            self.parts.append("\n")

    def handle_data(self, text):
        if not self.skip:
            self.parts.append(text)

    def text(self):
        return "\n".join(" ".join(x.split()) for x in "".join(self.parts).splitlines() if x.strip())


ALIASES = {
    "luigis-mansion": "Luigi's Mansion (Nintendo 3DS)",
    "mario-party-guest": "Mario Party: Star Rush",
    "mario-luigi-superstar-saga": "Mario & Luigi: Superstar Saga + Bowser's Minions",
    "mario-luigi-bowsers-inside-story": "Mario & Luigi: Bowser's Inside Story + Bowser Jr.'s Journey",
    "luigis-mansion-dark-moon": "Luigi's Mansion: Dark Moon",
    "puzzle-dragons-mario": "Puzzle & Dragons: Super Mario Bros. Edition",
    "pokemon-omega-ruby": "Pokémon Omega Ruby and Alpha Sapphire",
    "pokemon-alpha-sapphire": "Pokémon Omega Ruby and Alpha Sapphire",
    "pokemon-sun": "Pokémon Sun and Moon",
    "pokemon-moon": "Pokémon Sun and Moon",
    "pokemon-ultra-sun": "Pokémon Ultra Sun and Ultra Moon",
    "pokemon-ultra-moon": "Pokémon Ultra Sun and Ultra Moon",
    "pokemon-rumble-blast": "Pokémon Rumble Blast",
    "pokemon-battle-trozei": "Pokémon Battle Trozei",
    "pokemon-tretta-lab": "Pokémon Tretta Lab",
    "poke-transporter": "Poké Transporter",
    "3d-classics-kirbys-adventure": "3D Classics: Kirby's Adventure",
    "mario-dk-minis-on-move": "Mario and Donkey Kong: Minis on the Move",
    "mario-dk-tipping-stars": "Mario vs. Donkey Kong: Tipping Stars",
    "pokemon-x": "Pokémon X and Y",
    "pokemon-y": "Pokémon X and Y",
}


def targets():
    result = {}
    for g in json.loads((ROOT / "data/games.json").read_text())["games"]:
        title = ALIASES.get(g["id"], g["name"]).replace("’", "'")
        if g["franchise"] == "mario":
            host = "https://www.mariowiki.com/"
        elif g["franchise"] == "pokemon":
            host = "https://bulbapedia.bulbagarden.net/wiki/"
        elif g["franchise"] == "kirby":
            host = "https://wikirby.com/wiki/"
        else:
            host = "https://www.zeldadungeon.net/wiki/"
        result[g["id"]] = host + urllib.parse.quote(title.replace(" ", "_"), safe=":_")
    return result


def fetch(item):
    key, url = item
    CACHE.mkdir(parents=True, exist_ok=True)
    target = CACHE / (key + ".html")
    try:
        if target.is_file():
            raw = target.read_bytes()
            status = 200
        else:
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0 (UniversalGameGuide factual research)"}
            )
            with urllib.request.urlopen(req, timeout=20) as response:
                raw = response.read(8 * 1024 * 1024 + 1)
                status = response.status
            if len(raw) > 8 * 1024 * 1024:
                raise ValueError("reference too large")
            target.write_bytes(raw)
        parser = Text()
        parser.feed(raw.decode("utf-8"))
        text = parser.text()
        (CACHE / (key + ".txt")).write_text(text)
        return {
            "id": key,
            "url": url,
            "status": status,
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "retrieved": "2026-10-04",
        }
    except Exception as exc:
        return {"id": key, "url": url, "status": 0, "error": str(exc), "retrieved": "2026-10-04"}


if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        report = list(pool.map(fetch, targets().items()))
    CACHE.mkdir(parents=True, exist_ok=True)
    (CACHE / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(
        "Public reference pages:", len(report), "fetched:", sum(r["status"] == 200 for r in report)
    )
    for r in report:
        if r["status"] != 200:
            print("Pending:", r["id"], r.get("error", ""))
