#!/usr/bin/env python3
"""Draw original, non-geographic route diagrams; never loads third-party artwork."""

import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SPECS = [
    (
        "super-mario-3d-land",
        "world-1-1",
        "1-1 / pontos de referência",
        [
            ("Início", "Super Leaf nos blocos"),
            ("Rio", "Medalha 1 / corda"),
            ("Checkpoint", "Árvore / Note Blocks"),
            ("Cano", "Medalha 2 / sala"),
            ("Ponte final", "Medalha 3 / corda"),
            ("Ilha", "Mastro / saída"),
        ],
    ),
    (
        "luigis-mansion-dark-moon",
        "mansions",
        "Dark Moon / sequência",
        [
            ("Gloomy Manor", "Primeira mansão"),
            ("Haunted Towers", "Segunda mansão"),
            ("Old Clockworks", "Terceira mansão"),
            ("Secret Mine", "Quarta mansão"),
            ("Treacherous Mansion", "Quinta mansão"),
            ("Coleção", "13 gemas por mansão"),
        ],
    ),
    (
        "kirby-triple-deluxe",
        "floralia",
        "Floralia / regiões",
        [
            ("Fine Fields", "13 Sun Stones"),
            ("Lollipop Land", "14 Sun Stones"),
            ("Old Odyssey", "18 Sun Stones"),
            ("Wild World", "19 Sun Stones"),
            ("Endless Explosions", "20 Sun Stones"),
            ("Royal Road", "16 Sun Stones"),
        ],
    ),
    (
        "zelda-ocarina-of-time-3d",
        "first-objectives",
        "Objetivos / aventura normal",
        [
            ("Kokiri Forest", "Sword + Shield"),
            ("Deku Tree", "Slingshot / Emerald"),
            ("Dodongo’s Cavern", "Bomb Bag / Ruby"),
            ("Jabu-Jabu", "Boomerang / Sapphire"),
            ("Temple of Time", "Master Sword"),
            ("Adulto / cemitério", "Hookshot"),
        ],
    ),
    (
        "pokemon-x",
        "kalos-route",
        "Kalos / início da jornada",
        [
            ("Vaniville", "Route 1 / Aquacorde"),
            ("Route 2", "Santalune Forest"),
            ("Santalune", "Primeiro ginásio"),
            ("Lumiose sul", "Route 4 / Route 5"),
            ("Camphrier", "Parfum Palace / Route 7"),
            ("Ambrette / Cyllage", "Glittering Cave / ginásio"),
        ],
    ),
]


SPECS.extend(
    [
        (
            "super-mario-3d-land",
            "world-1-castle",
            "World 1-Castle / coleta",
            [
                ("Plataforma rotatória", "Medalha 1 / centro"),
                ("Lava Bubble", "Espere a abertura"),
                ("Checkpoint", "Recomeço do trecho"),
                ("Fire Bar", "Medalha 2 / perto"),
                ("Segundo Thwomp", "Medalha 3 / atrás"),
                ("Wall jump", "Passagem estreita"),
            ],
        ),
        (
            "kirby-triple-deluxe",
            "fine-fields-1",
            "Fine Fields 1 / Hypernova",
            [
                ("Miracle Fruit", "Obter Hypernova"),
                ("Árvore grande", "Sun Stone 1"),
                ("Reentrância", "Mova bloco de apoio"),
                ("Bloco com pedra", "Puxe / Sun Stone 2"),
                ("Pêndulo", "Puxe até dourado"),
                ("Parede destruída", "Rare Keychain"),
            ],
        ),
        (
            "zelda-ocarina-of-time-3d",
            "water-temple",
            "Water Temple / níveis",
            [
                ("Fundo / Ruto", "Suba ao símbolo"),
                ("Água baixa", "Tochas / portas baixas"),
                ("Pilar central", "Água média"),
                ("Bloco flutuante", "Chave sob a base"),
                ("Dark Link", "Longshot / alcance"),
                ("Morpha", "Puxe o núcleo"),
            ],
        ),
    ]
)


# Fonts are not distributed: rendered glyphs in original diagrams only.
def font(size):
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
    ]:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


registry = []
maps = []
for gid, ident, title, nodes in SPECS:
    im = Image.new("RGB", (640, 384), (13, 22, 34))
    d = ImageDraw.Draw(im)
    d.text((16, 8), title, font=font(23), fill=(90, 219, 160))
    d.text((16, 42), "Esquema próprio / sem escala geográfica", font=font(15), fill=(168, 185, 202))
    positions = [(16, 82), (226, 82), (436, 82), (16, 228), (226, 228), (436, 228)]
    for i, ((name, note), (x, y)) in enumerate(zip(nodes, positions)):
        d.rounded_rectangle(
            (x, y, x + 188, y + 106), radius=8, fill=(25, 39, 56), outline=(90, 219, 160), width=2
        )
        d.text((x + 8, y + 8), str(i + 1), font=font(20), fill=(90, 219, 160))
        words = name.split()
        lines = [""]
        for w in words:
            if d.textlength(lines[-1] + " " + w, font=font(15)) > 168:
                lines.append(w)
            else:
                lines[-1] = (lines[-1] + " " + w).strip()
        for n, line in enumerate(lines):
            d.text((x + 8, y + 36 + n * 19), line, font=font(15), fill=(237, 243, 250))
        words = note.split()
        lines = [""]
        for w in words:
            if d.textlength(lines[-1] + " " + w, font=font(12)) > 168:
                lines.append(w)
            else:
                lines[-1] = (lines[-1] + " " + w).strip()
        for n, line in enumerate(lines):
            d.text((x + 8, y + 76 + n * 14), line, font=font(12), fill=(168, 185, 202))
    d.text(
        (16, 357),
        "Leia 1 → 6; o desenho indica objetivos, não corredores.",
        font=font(15),
        fill=(168, 185, 202),
    )
    rel = f"assets/maps/{gid}-{ident}.png"
    path = ROOT / rel
    im.save(path, optimize=True)
    registry.append(
        {
            "path": rel,
            "author": "Contribuidores do 3DS Universal Game Guide",
            "source": "Desenho original gerado por scripts/make_maps.py; fatos referenciados no guia correspondente",
            "license": "CC-BY-4.0",
            "url": f"guides/pt-BR/{gid}/SOURCES.md",
            "accessed": "2026-10-04",
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    )
    maps.append(
        {"gameId": gid, "id": ident, "asset": rel, "width": 640, "height": 384, "levels": 2}
    )
# X and Y share the same factual route drawing, with distinct game IDs.
companion = dict(next(m for m in maps if m["gameId"] == "pokemon-x"))
companion["gameId"] = "pokemon-y"
maps.append(companion)
(ROOT / "ASSET_LICENSES.json").write_text(
    json.dumps({"schemaVersion": 1, "assets": registry}, ensure_ascii=False, indent=2) + "\n"
)
(ROOT / "assets/maps.json").write_text(
    json.dumps({"schemaVersion": 1, "maps": maps}, indent=2) + "\n"
)
print("Esquemas originais e registro de licenças gerados.")
