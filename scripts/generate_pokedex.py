#!/usr/bin/env python3
"""Generate Gen-VI factual pages from a pinned, BSD-3-Clause PokéAPI snapshot.
No flavor text, sprites, ROM data or scraped walkthrough prose is imported.
"""

import csv
import hashlib
import shutil
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "research/pokeapi"
COMMIT = "bc92d3b6029ef1abe9e7ad424c400b338f3c11fe"
TYPE_PT = {
    "Normal": "Normal",
    "Fire": "Fogo",
    "Water": "Água",
    "Electric": "Elétrico",
    "Grass": "Grama",
    "Ice": "Gelo",
    "Fighting": "Lutador",
    "Poison": "Venenoso",
    "Ground": "Terrestre",
    "Flying": "Voador",
    "Psychic": "Psíquico",
    "Bug": "Inseto",
    "Rock": "Pedra",
    "Ghost": "Fantasma",
    "Dragon": "Dragão",
    "Dark": "Sombrio",
    "Steel": "Aço",
    "Fairy": "Fada",
}
METHOD_PT = {
    "Walk": "Caminhando",
    "Surf": "Usando Surf",
    "Old Rod": "Pesca / Old Rod",
    "Good Rod": "Pesca / Good Rod",
    "Super Rod": "Pesca / Super Rod",
    "Rock Smash": "Usando Rock Smash",
    "Horde": "Horda",
    "Gift": "Presente",
    "Static": "Encontro fixo",
    "Yellow Flowers": "Flores amarelas",
    "Purple Flowers": "Flores roxas",
    "Red Flowers": "Flores vermelhas",
    "Rough Terrain": "Terreno acidentado",
    "Berry Trees": "Árvores de Berries",
    "Ceiling Ambush": "Emboscada do teto",
    "Ground Ambush": "Emboscada do chão",
    "Rustling Bush Ambush": "Emboscada no arbusto",
    "Sky Ambush": "Emboscada aérea",
    "Trash Can Ambush": "Emboscada na lixeira",
}

# Never silently relabel edited CSVs as a verified public commit.
source_lock = json.loads((ROOT / "data/pokemon/source-lock.json").read_text())
assert source_lock["commit"] == COMMIT
for filename, metadata in source_lock["files"].items():
    assert Path(filename).name == filename
    assert hashlib.sha256((RAW / filename).read_bytes()).hexdigest() == metadata["sha256"], filename


def rows(name):
    return list(csv.DictReader((RAW / (name + ".csv")).open(encoding="utf-8", newline="")))


def number(row, key, default=0):
    return int(row.get(key) or default)


def label(value):
    return value.replace("-", " ").title()


def names(name):
    return {number(r, "id"): label(r["identifier"]) for r in rows(name)}


sp = {number(r, "id"): r for r in rows("pokemon_species") if number(r, "generation_id") <= 6}
english = {
    number(r, "pokemon_species_id"): r["name"]
    for r in rows("pokemon_species_names")
    if r["local_language_id"] == "9"
}
pok = {
    number(r, "species_id"): number(r, "id")
    for r in rows("pokemon")
    if r["is_default"] == "1" and number(r, "species_id") in sp
}
versions = {number(r, "id"): r for r in rows("versions")}
xy = {k for k, v in versions.items() if v["identifier"] in {"x", "y"}}
assert xy == {23, 24} and all(number(versions[v], "version_group_id") == 15 for v in xy)
types = names("types")
abilities = names("abilities")
items = names("items")
moves = names("moves")
locations = {number(r, "id"): r for r in rows("locations")}
areas = {number(r, "id"): r for r in rows("location_areas")}
slots = {number(r, "id"): r for r in rows("encounter_slots")}
methods = names("encounter_methods")


# Historical tables describe values up to and including generation_id.
def historical(table, past, keyfields):
    result = {tuple(number(r, k) for k in keyfields): r for r in rows(table)}
    candidates = defaultdict(list)
    for r in rows(past):
        if number(r, "generation_id") >= 6:
            candidates[tuple(number(r, k) for k in keyfields)].append(r)
    for key, entries in candidates.items():
        result[key] = min(entries, key=lambda r: number(r, "generation_id"))
    return result


ty = historical("pokemon_types", "pokemon_types_past", ["pokemon_id", "slot"])
ab = historical("pokemon_abilities", "pokemon_abilities_past", ["pokemon_id", "slot"])
st = historical("pokemon_stats", "pokemon_stats_past", ["pokemon_id", "stat_id"])
efficacy = {
    (number(r, "damage_type_id"), number(r, "target_type_id")): number(r, "damage_factor") / 100
    for r in rows("type_efficacy")
    if number(r, "damage_type_id") <= 18 and number(r, "target_type_id") <= 18
}
encounters = defaultdict(dict)
for e in rows("encounters"):
    v = number(e, "version_id")
    pid = number(e, "pokemon_id")
    if v not in xy:
        continue
    area = areas[number(e, "location_area_id")]
    loc = locations[number(area, "location_id")]
    slot = slots[number(e, "encounter_slot_id")]
    area_name = label(loc["identifier"]) + (
        (" / " + label(area["identifier"])) if area["identifier"] else ""
    )
    key = (v, area_name, methods[number(slot, "encounter_method_id")])
    mn = number(e, "min_level")
    mx = number(e, "max_level")
    if key in encounters[pid]:
        a, b = encounters[pid][key]
        mn = min(a, mn)
        mx = max(b, mx)
    encounters[pid][key] = (mn, mx)
learn = defaultdict(list)
for r in rows("pokemon_moves"):
    if number(r, "version_group_id") == 15 and number(r, "pokemon_move_method_id") == 1:
        learn[number(r, "pokemon_id")].append((number(r, "level"), moves[number(r, "move_id")]))
dex = defaultdict(list)
for r in rows("pokemon_dex_numbers"):
    if number(r, "pokedex_id") in {12, 13, 14}:
        dex[number(r, "species_id")].append(
            (
                {12: "Central", 13: "Coastal", 14: "Mountain"}[number(r, "pokedex_id")],
                number(r, "pokedex_number"),
            )
        )
evol = defaultdict(list)
for r in rows("pokemon_evolution"):
    target = number(r, "evolved_species_id")
    vg = number(r, "version_group_id")
    if target not in sp or vg > 15:
        continue
    if r["location_id"] and (number(locations.get(number(r, "location_id"), {}), "region_id") != 6):
        continue
    src = number(sp[target], "evolves_from_species_id")
    if src:
        evol[src].append(r)


def evolution(r):
    target = number(r, "evolved_species_id")
    trigger = number(r, "evolution_trigger_id")
    out = []
    if trigger == 1:
        out.append("subir de nível")
    elif trigger == 2:
        out.append("trocar com outro jogador")
    elif trigger == 3:
        out.append("usar " + items[number(r, "trigger_item_id")])
    elif trigger == 4:
        out.append("criar espaço na equipe e ter uma Poké Ball ao evoluir Nincada")
    else:
        return english[target] + ": condição especial ainda não modelada"
    if r["minimum_level"]:
        out.append("nível mínimo " + r["minimum_level"])
    if r["held_item_id"]:
        out.append("segurando " + items[number(r, "held_item_id")])
    if r["minimum_happiness"]:
        out.append("amizade mínima 220 (geração VI)")
    if r["minimum_affection"]:
        out.append("affection mínima " + r["minimum_affection"] + " em Pokémon-Amie")
    if r["minimum_beauty"]:
        out.append("Beauty mínima " + r["minimum_beauty"])
    if r["time_of_day"]:
        out.append(
            {"day": "durante o dia", "night": "durante a noite", "dusk": "ao anoitecer"}.get(
                r["time_of_day"], r["time_of_day"]
            )
        )
    if r["gender_id"]:
        out.append({"1": "fêmea", "2": "macho", "3": "sem gênero"}[r["gender_id"]])
    if r["location_id"]:
        out.append("em " + label(locations[number(r, "location_id")]["identifier"]))
    if r["known_move_id"]:
        out.append("conhecendo " + moves[number(r, "known_move_id")])
    if r["known_move_type_id"]:
        out.append("conhecendo golpe " + types[number(r, "known_move_type_id")])
    if r["relative_physical_stats"]:
        out.append(
            {
                "1": "Attack maior que Defense",
                "-1": "Attack menor que Defense",
                "0": "Attack igual a Defense",
            }[r["relative_physical_stats"]]
        )
    if r["party_species_id"]:
        out.append("com " + english[number(r, "party_species_id")] + " na equipe")
    if r["party_type_id"]:
        out.append("com Pokémon " + types[number(r, "party_type_id")] + " na equipe")
    if r["trade_species_id"]:
        out.append("em troca por " + english[number(r, "trade_species_id")])
    if r["needs_overworld_rain"] == "1":
        out.append("com chuva natural no mapa")
    if r["turn_upside_down"] == "1":
        out.append("com o console de cabeça para baixo")
    if r["condition_expression"]:
        out.append("ramo determinado por valor interno; não pode ser escolhido apenas pelo nível")
    return english[target] + ": " + ", ".join(out)


records = []
for sid, species in sorted(sp.items()):
    pid = pok[sid]
    ts = [number(ty[pid, i], "type_id") for i in [1, 2] if (pid, i) in ty]
    stats = [number(st[pid, i], "base_stat") for i in range(1, 7)]
    ability_list = [
        {
            "name": abilities[number(ab[pid, i], "ability_id")],
            "hidden": ab[pid, i]["is_hidden"] == "1",
        }
        for i in [1, 2, 3]
        if (pid, i) in ab and ab[pid, i]["ability_id"]
    ]
    mult = {types[t]: __import__("math").prod(efficacy[t, d] for d in ts) for t in range(1, 19)}
    # Evolution conditions referring to other generations' locations are excluded.
    ev = sorted(set(evolution(r) for r in evol[sid]))
    if sid == 349:
        ev = [e for e in ev if "Beauty" not in e]  # Beauty evolution isn't available in X/Y.
    records.append(
        {
            "number": sid,
            "name": english[sid],
            "types": [types[t] for t in ts],
            "stats": stats,
            "abilities": ability_list,
            "damageMultipliers": mult,
            "evolvesFrom": english.get(number(species, "evolves_from_species_id")),
            "evolutions": ev,
            "kalosDex": dex[sid],
            "encounters": [
                {
                    "version": versions[v]["identifier"].upper(),
                    "area": area,
                    "method": method,
                    "minLevel": mn,
                    "maxLevel": mx,
                }
                for (v, area, method), (mn, mx) in sorted(encounters[pid].items())
            ],
            "levelMoves": [{"level": lv, "name": name} for lv, name in sorted(set(learn[pid]))],
        }
    )
assert len(records) == 721
out = ROOT / "data/pokemon"
out.mkdir(exist_ok=True)
(out / "gen6.json").write_text(
    json.dumps(
        {
            "schemaVersion": 1,
            "generation": 6,
            "games": ["X", "Y"],
            "forms": "default-only",
            "license": "BSD-3-Clause",
            "sourceCommit": COMMIT,
            "records": records,
        },
        ensure_ascii=False,
        indent=2,
    )
    + "\n"
)
(ROOT / "docs/licenses").mkdir(exist_ok=True)
(ROOT / "docs/licenses/POKEAPI-BSD-3-Clause.txt").write_bytes((RAW / "LICENSE.md").read_bytes())
base = ROOT / "guides/pt-BR/pokemon-x"
guide = json.loads((base / "guide.json").read_text())
sources = json.loads((base / "sources.json").read_text())
source = {
    "title": "PokéAPI, tabelas factuais BSD-3-Clause (snapshot fixado)",
    "url": f"https://github.com/PokeAPI/pokeapi/tree/{COMMIT}/data/v2/csv",
    "retrieved": "2026-10-04",
    "use": "Dados numéricos e nomes; sem flavor text, sprites ou arte. Aviso BSD em docs/licenses.",
}
if source not in sources:
    sources.append(source)
friend = {
    "title": "Friendship — diferenças entre gerações",
    "url": "https://bulbapedia.bulbagarden.net/wiki/Friendship#Evolutions_based_on_friendship",
    "retrieved": "2026-10-04",
    "use": "Limiar histórico de evolução: 220 na geração VI; não usar o valor moderno 160.",
}
if friend not in sources:
    sources.append(friend)
existing = [p for p in guide["pages"] if not p["id"].startswith("dex-")]
guide["pages"] = existing
for r in records:
    ident = f"dex-{r['number']:03d}"
    title = f"{r['number']:03d} / {r['name']}"
    lines = [
        f"# {title}",
        "",
        "Pokédex factual / X e Y / forma normal / geração VI.",
        "",
        "Tipos: " + " / ".join(TYPE_PT[t] for t in r["types"]),
        "Atributos base (HP / Ataque / Defesa / Atq. especial / Def. especial / Velocidade): "
        + " / ".join(map(str, r["stats"])),
        "Habilidades: "
        + ", ".join(a["name"] + (" [oculta]" if a["hidden"] else "") for a in r["abilities"]),
        "",
    ]
    if r["kalosDex"]:
        regions_pt = {"Central": "Central", "Coastal": "Costeira", "Mountain": "Montanhosa"}
        lines.append(
            "Kalos: " + ", ".join(f"{regions_pt[area]} #{n:03d}" for area, n in r["kalosDex"])
        )
    for label_, predicate in [
        ("Fraquezas", lambda x: x > 1),
        ("Resistências", lambda x: 0 < x < 1),
        ("Imunidades", lambda x: x == 0),
    ]:
        lines.append(
            label_
            + ": "
            + (
                ", ".join(
                    f"{TYPE_PT[t]} x{v:g}".replace(".", ",")
                    for t, v in r["damageMultipliers"].items()
                    if predicate(v)
                )
                or "nenhuma pela tabela de tipos"
            )
        )
    lines += [
        "",
        "Multiplicadores ignoram habilidades, itens e campo. A habilidade pode anular uma fraqueza. Habilidades ocultas não são obtidas automaticamente em encontros comuns.",
        "",
    ]
    if r["evolvesFrom"]:
        lines.append("Forma anterior: " + r["evolvesFrom"])
    lines.append(
        "Evolução: "
        + (
            "Não possui evolução normal na geração VI."
            if not r["evolutions"]
            else "\n" + "\n".join("- " + e for e in r["evolutions"])
        )
    )
    lines += ["", "Locais e métodos documentados:"]
    if not r["encounters"]:
        lines += [
            "Não há registro de obtenção em X/Y nesta tabela. Verifique evolução, presentes, troca, eventos e Friend Safari; esta ausência não significa impossibilidade de obtenção."
        ]
    for e in r["encounters"]:
        lines.append(
            f"- {e['version']}: {e['area']} / {METHOD_PT[e['method']]} / nível {e['minLevel']}–{e['maxLevel']}"
        )
    lines += [
        "",
        "Movimentos por nível em X/Y (nível 1 pode incluir golpes de início/reaprendizagem):",
    ]
    lines += ["- " + str(m["level"]) + ": " + m["name"] for m in r["levelMoves"]] or [
        "Não listado."
    ]
    lines += [
        "",
        "TMs, HMs, Move Tutors, Egg Moves e formas Mega não estão completos nesta página. Algumas evoluções com condições especiais precisam de revisão editorial.",
        "Dados PokéAPI / BSD-3-Clause; estrutura e notas próprias / CC BY 4.0.",
    ]
    text = "\n".join(lines) + "\n"
    if len(text.encode()) > 8192:
        raise SystemExit(f"{title} acima do limite: dividir a página antes do build")
    (base / (ident + ".md")).write_text(text)
    keywords = [r["name"], "Pokédex", "evolução", "fraquezas"] + [
        e["area"].replace("Kalos ", "") for e in r["encounters"]
    ]
    guide["pages"].append(
        {
            "id": ident,
            "title": title,
            "file": ident + ".md",
            "spoiler": r["number"] >= 716,
            "sources": [sources.index(source), sources.index(friend)],
            "keywords": sorted(set(keywords)),
            "generatedBy": "scripts/generate_pokedex.py",
        }
    )
(base / "guide.json").write_text(json.dumps(guide, ensure_ascii=False, indent=2) + "\n")
(base / "sources.json").write_text(json.dumps(sources, ensure_ascii=False, indent=2) + "\n")
(base / "SOURCES.md").write_text(
    "# Fontes e autoria\n\nNotas e organização próprias: CC BY 4.0. Dados factuais PokéAPI: BSD-3-Clause; preservar o aviso em docs/licenses/POKEAPI-BSD-3-Clause.txt. Nenhum flavor text ou sprite foi importado.\n\n"
    + "".join(f"- [{i}: {s['title']}]({s['url']})\n" for i, s in enumerate(sources))
    + "\nO gerador aplica tabelas históricas de stats, tipos e habilidades para geração VI e corrige amizade para 220. Exclui locais de evolução de regiões anteriores. A disponibilidade de presentes, eventos, trocas e Friend Safari ainda não é completa. Condições especiais precisam de revisão editorial.\n"
)
print(
    f"{len(records)} espécies factuais geradas; {sum(len(r['encounters']) for r in records)} registros de área/método/versão."
)

# Refresh only generated Pokédex pages in Y; retain its editorial pages.
other = ROOT / "guides/pt-BR/pokemon-y"
if (other / "guide.json").exists():
    companion = json.loads((other / "guide.json").read_text())
    companion_sources = json.loads((other / "sources.json").read_text())
    for src in [source, friend]:
        if src not in companion_sources:
            companion_sources.append(src)
    companion["pages"] = [p for p in companion["pages"] if not p["id"].startswith("dex-")]
    for page in guide["pages"]:
        if page["id"].startswith("dex-"):
            item = dict(page)
            item["sources"] = [companion_sources.index(source), companion_sources.index(friend)]
            companion["pages"].append(item)
            shutil.copy2(base / page["file"], other / page["file"])
    (other / "guide.json").write_text(json.dumps(companion, ensure_ascii=False, indent=2) + "\n")
    (other / "sources.json").write_text(
        json.dumps(companion_sources, ensure_ascii=False, indent=2) + "\n"
    )
