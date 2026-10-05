#!/usr/bin/env python3
"""Fetch reference text for human authoring. Never copies reference text into guides."""

import concurrent.futures
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = {
    "mario-world1": "https://www.mariowiki.com/World_1-1_(Super_Mario_3D_Land)",
    "mario-world12": "https://www.mariowiki.com/World_1-2_(Super_Mario_3D_Land)",
    "mario-world13": "https://www.mariowiki.com/World_1-3_(Super_Mario_3D_Land)",
    "mario-world14": "https://www.mariowiki.com/World_1-4_(Super_Mario_3D_Land)",
    "mario-special": "https://www.mariowiki.com/Special_1-Castle",
    "mario-coins": "https://www.mariowiki.com/Star_Medal",
    "mario-boom": "https://www.mariowiki.com/Boom_Boom",
    "mario-pompom": "https://www.mariowiki.com/Pom_Pom",
    "luigi-gloomy": "https://www.mariowiki.com/Gloomy_Manor",
    "luigi-haunted": "https://www.mariowiki.com/Haunted_Towers",
    "luigi-clockworks": "https://www.mariowiki.com/Old_Clockworks",
    "luigi-secretmine": "https://www.mariowiki.com/Secret_Mine",
    "luigi-treacherous": "https://www.mariowiki.com/Treacherous_Mansion",
    "luigi-boo": "https://www.mariowiki.com/Boo#Luigi.27s_Mansion:_Dark_Moon",
    "kirby-fine": "https://wikirby.com/wiki/Fine_Fields",
    "kirby-lollipop": "https://wikirby.com/wiki/Lollipop_Land",
    "kirby-old": "https://wikirby.com/wiki/Old_Odyssey",
    "kirby-wild": "https://wikirby.com/wiki/Wild_World",
    "kirby-endless": "https://wikirby.com/wiki/Endless_Explosions",
    "kirby-royal": "https://wikirby.com/wiki/Royal_Road",
    "kirby-sunstones": "https://wikirby.com/wiki/Sun_Stone",
    "kirby-sectonia": "https://wikirby.com/wiki/Queen_Sectonia",
    "pokemon-gym": "https://bulbapedia.bulbagarden.net/wiki/Kalos_League",
    "pokemon-mega": "https://bulbapedia.bulbagarden.net/wiki/Mega_Evolution",
    "pokemon-charizard": "https://bulbapedia.bulbagarden.net/wiki/Charizard_(Pok%C3%A9mon)",
    "pokemon-breeding": "https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_breeding",
    "pokemon-evolution": "https://bulbapedia.bulbagarden.net/wiki/Evolution",
    "pokemon-type": "https://bulbapedia.bulbagarden.net/wiki/Type/Type_chart",
    "pokemon-hm": "https://bulbapedia.bulbagarden.net/wiki/HM",
    "pokemon-tm": "https://bulbapedia.bulbagarden.net/wiki/List_of_TMs_and_HMs_in_Generation_VI",
    "pokemon-post": "https://bulbapedia.bulbagarden.net/wiki/Kiloude_City",
}
for n in range(1, 18):
    PAGES[f"pokemon-part{n}"] = (
        f"https://bulbapedia.bulbagarden.net/wiki/Walkthrough:Pok%C3%A9mon_X_and_Y/Part_{n}"
    )
for slug in [
    "kokiri-forest",
    "hyrule-castle",
    "death-mountain",
    "inside-jabu-jabus-belly",
    "forest-temple",
    "fire-temple",
    "water-temple",
    "shadow-temple",
    "spirit-temple",
    "ganons-castle",
    "heart-pieces",
    "gold-skulltulas",
]:
    PAGES["zelda-" + slug] = (
        "https://www.zeldadungeon.net/ocarina-of-time-walkthrough/" + slug + "/"
    )


def fetch(item):
    name, url = item
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (UniversalGameGuide source research)"}
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read()
            status = r.status
            final = r.url
        (ROOT / "research/content" / f"{name}.html").write_bytes(body)
        return {
            "name": name,
            "url": url,
            "finalUrl": final,
            "status": status,
            "bytes": len(body),
            "retrieved": "2026-10-04",
        }
    except Exception as e:
        return {"name": name, "url": url, "status": 0, "error": str(e)}


if __name__ == "__main__":
    (ROOT / "research/content").mkdir(parents=True, exist_ok=True)
    results = list(concurrent.futures.ThreadPoolExecutor(max_workers=6).map(fetch, PAGES.items()))
    (ROOT / "research/content-report.json").write_text(json.dumps(results, indent=2) + "\n")
    print("Fontes acessadas:", sum(r["status"] == 200 for r in results), "/", len(results))
    print([(r["name"], r.get("error")) for r in results if r["status"] != 200])
