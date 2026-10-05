#!/usr/bin/env python3
"""Render current catalog coverage without equating metadata to hardware support."""

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
games = json.loads((ROOT / "data/games.json").read_text())["games"]
count = Counter()
lines = [
    "# Jogos e regiões catalogados",
    "",
    "Reconhecimento por metadados não confirma compatibilidade física. Não testado em hardware real. Cobertura regional não demonstrada exaustiva. “Piloto parcial” não é walkthrough completo.",
    "",
    "| Jogo | Família / categoria | Regiões observadas | Conteúdo PT-BR |",
    "|---|---|---|---|",
]
for g in games:
    for r, t in g["titleIds"].items():
        count[r] += len(t)
    coverage = {
        "missing": "Ainda sem guia",
        "pilot-partial": "Piloto parcial",
        "starter": "Referência inicial",
        "complete": "Completo (revisão declarada)",
    }[g["guides"]["pt-BR"]]
    regions = (
        ", ".join(r + (" [rótulo incerto]" if r == "CHN" else "") for r in g["titleIds"])
        or "ID pendente"
    )
    lines.append(f"| {g['name']} | {g['franchise']} / {g['category']} | {regions} | {coverage} |")
lines += [
    "",
    "## Totais",
    "",
    f"{len(games)} entradas; {len({t for g in games for tids in g['titleIds'].values() for t in tids})} IDs únicos; {sum(count.values())} associações regionais.",
    "",
]
lines += ["| Região | Associações observadas |", "|---|---|"] + [
    f"| {r} | {c} |" for r, c in sorted(count.items())
]
lines += [
    "",
    "CHN aparece como rótulo comunitário de Ocarina 008F900, que também consta em TWN; não confirma uma edição chinesa/iQue. Não inferir IDs ausentes.",
    "",
    "Pokémon Bank, Poké Transporter, Pokédex 3D/Pro e outros utilitários aparecem em categoria distinta. Photos with Mario e Guest Edition são aplicações complementares. Aventura antecipada japonesa de Detective Pikachu e versões regionais de Puzzle & Dragons exigem conteúdo específico futuro.",
    "",
    "Não incluídos: Virtual Console de GB/GBC/NES, jogos DS, updates, DLCs, demos, série Donkey Kong independente. 3D Classics: Kirby’s Adventure é port nativo aprimorado, incluído separadamente. Jogos Mario vs. Donkey Kong entram por associação direta ao título Mario.",
    "",
    "Falta confirmar ID-base de Pokémon Tretta Lab. A base não é derivada do ID de seu update. Veja TITLE_ID_AUDIT.md.",
]
(ROOT / "SUPPORTED_GAMES.md").write_text("\n".join(lines) + "\n")
print("SUPPORTED_GAMES.md atualizado a partir do catálogo.")
