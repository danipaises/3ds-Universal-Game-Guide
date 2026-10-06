#!/usr/bin/env python3
"""Guide Builder: bounded offline packs, validation, maps and deterministic SD ZIPs."""

from __future__ import annotations
import argparse
import concurrent.futures
import hashlib
import importlib.util
import json
import math
import re
import shutil
import struct
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAX_PAGES = 1024
MAX_TEXT = 8192
MAX_SOURCE_TEXT = 64 * 1024
MAX_JSON = 16 * 1024 * 1024
MAX_GUIDE = 4 * 1024 * 1024
PAGE = struct.Struct("<48s96sIIII48s")
TITLE = struct.Struct("<Q64s96s")
ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
TID = re.compile(r"00040000[0-9A-F]{8}\Z")
LANGUAGES = {"pt-BR", "en-US"}
PILOTS = {
    "super-mario-3d-land",
    "pokemon-x",
    "pokemon-y",
    "zelda-ocarina-of-time-3d",
    "kirby-triple-deluxe",
    "luigis-mansion-dark-moon",
}


def version(root=ROOT):
    value = (root / "VERSION").read_text().strip()
    require(re.fullmatch(r"\d+\.\d+\.\d+-(?:alpha|beta|rc)(?:\.\d+)?", value), "versão inválida")
    return value


class Invalid(ValueError):
    pass


def require(condition: bool, why: str) -> None:
    if not condition:
        raise Invalid(why)


def read_json(path: Path):
    def unique(pairs):
        obj = {}
        for k, v in pairs:
            require(k not in obj, f"{path}: chave duplicada {k}")
            obj[k] = v
        return obj

    try:
        require(path.stat().st_size <= MAX_JSON, f"{path}: JSON acima de 16 MiB")
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise Invalid(f"{path}: {exc}") from exc


def inside(root: Path, relative: str, exists=True) -> Path:
    require(
        isinstance(relative, str) and relative and not Path(relative).is_absolute(),
        "caminho relativo obrigatório",
    )
    require(".." not in Path(relative).parts and "\\" not in relative, "path traversal")
    p = root / relative
    require(not p.is_symlink(), f"symlink recusado: {p}")
    require(p.resolve().is_relative_to(root.resolve()), "caminho fora da raiz")
    if exists:
        require(p.is_file(), f"arquivo ausente: {p}")
    return p


def markdown_files(root: Path):
    return sorted(
        list(root.glob("*.md"))
        + list(root.glob("docs/**/*.md"))
        + list(root.glob("guides/**/*.md"))
        + list(root.glob("data/**/*.md"))
    )


def inline_targets(text: str):
    """Read inline destinations, including balanced parentheses in wiki URLs."""
    for match in re.finditer(r"\]\(", text):
        start = match.end()
        depth = 1
        end = start
        while end < len(text) and text[end] != "\n" and depth:
            if text[end] == "\\":
                end += 2
                continue
            if text[end] == "(":
                depth += 1
            elif text[end] == ")":
                depth -= 1
            if depth:
                end += 1
        if depth == 0:
            raw = text[start:end].strip()
            if raw.startswith("<") and ">" in raw:
                yield raw[1 : raw.index(">")]
            else:
                yield re.split(r"\s+[\"']", raw, maxsplit=1)[0]


def local_links(root: Path):
    """Check inline Markdown file targets; heading anchors need editorial review."""
    report = []
    for file in markdown_files(root):
        require(file.resolve().is_relative_to(root.resolve()), "Markdown fora da raiz")
        for target in inline_targets(file.read_text(encoding="utf-8")):
            link = urllib.parse.urlsplit(target)
            if link.scheme or link.netloc or not link.path:
                continue
            path = Path(urllib.parse.unquote(link.path))
            destination = file.parent / path
            safe = (
                not path.is_absolute()
                and "\\" not in str(path)
                and destination.resolve().is_relative_to(root.resolve())
                and not destination.is_symlink()
            )
            report.append(
                {
                    "file": file.relative_to(root).as_posix(),
                    "target": target,
                    "verdict": "reachable" if safe and destination.is_file() else "broken",
                }
            )
    return report


def require_local_links(root: Path):
    report = local_links(root)
    missing = [f"{r['file']} -> {r['target']}" for r in report if r["verdict"] == "broken"]
    require(not missing, "links locais ausentes ou fora da raiz: " + "; ".join(missing))
    return report


def slug(value):
    return isinstance(value, str) and len(value) <= 47 and ID.fullmatch(value)


def field(text: str, size: int) -> bytes:
    require(isinstance(text, str), "campo textual obrigatório")
    require(not any(0xD800 <= ord(c) <= 0xDFFF for c in text), "Unicode surrogate inválido")
    data = text.encode("utf-8")
    require(len(data) < size and "\0" not in text, f"campo maior que {size - 1}: {text}")
    require(not any(ord(c) < 32 or ord(c) == 127 for c in text), f"controle em campo: {text}")
    return data.ljust(size, b"\0")


def plain(markdown: str) -> str:
    require(not any(0xD800 <= ord(c) <= 0xDFFF for c in markdown), "Unicode inválido")
    require(
        not any((ord(c) < 32 and c not in "\n\t\r") or ord(c) == 127 for c in markdown),
        "caractere de controle no texto",
    )
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", markdown)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.M)
    text = text.replace("**", "").replace("`", "").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"^[*-]\s+", "- ", text, flags=re.M)
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
    require(0 < len(text.encode("utf-8")) <= MAX_TEXT, "página vazia ou acima de 8192 bytes")
    return text


def fold(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", text.lower()) if not unicodedata.combining(c)
    )


def read_text_source(path: Path):
    try:
        require(path.stat().st_size <= MAX_SOURCE_TEXT, "source textual acima de 64 KiB")
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise Invalid(f"{path}: texto UTF-8 inválido/inacessível") from exc


def guide_data(root: Path, lang: str, gid: str):
    base = root / "guides" / lang / gid
    if not (base / "guide.json").exists():
        return None
    obj = read_json(base / "guide.json")
    require(
        obj.get("schemaVersion") == 1 and obj.get("gameId") == gid and obj.get("language") == lang,
        f"{gid}: cabeçalho inválido",
    )
    require(
        obj.get("coverage") in {"pilot-partial", "starter", "complete"},
        f"{gid}: cobertura explícita obrigatória",
    )
    require(obj.get("license") == "CC-BY-4.0", f"{gid}: licença de texto não definida")
    require(
        isinstance(obj.get("pages"), list) and 0 < len(obj["pages"]) <= MAX_PAGES,
        f"{gid}: índice inválido",
    )
    require((base / "SOURCES.md").is_file(), f"{gid}: SOURCES.md ausente")
    sources = read_json(base / "sources.json")
    require(isinstance(sources, list) and len(sources) > 0, f"{gid}: fontes ausentes")
    ids = set()
    for p in obj["pages"]:
        require(slug(p.get("id")) and p["id"] not in ids, f"{gid}: ID de página inválido/duplicado")
        ids.add(p["id"])
        field(p.get("title", ""), 96)
        require(type(p.get("spoiler", False)) is bool, "spoiler deve ser bool")
        require(not p.get("map") or slug(p["map"]), "ID de mapa inválido")
        text = read_text_source(inside(base, p["file"]))
        plain(text)
        require(
            isinstance(p.get("sources"), list)
            and p["sources"]
            and all(type(i) is int and 0 <= i < len(sources) for i in p["sources"]),
            f"{gid}/{p['id']}: referências inválidas",
        )
        for target in inline_targets(text):
            if not urllib.parse.urlparse(target).scheme and not target.startswith("#"):
                inside(base, target.split("#")[0])
    sections = {p.get("section") for p in obj["pages"] if p.get("section")}
    if obj.get("requiredSections") is not None:
        require(
            isinstance(obj["requiredSections"], list)
            and all(slug(x) for x in obj["requiredSections"]),
            "seções inválidas",
        )
        require(set(obj["requiredSections"]) <= sections, f"{gid}: seção obrigatória ausente")
    if obj["coverage"] == "complete":
        require(
            obj.get("reviewed") is True and obj.get("requiredSections"),
            "guia completo exige revisão e seções verificáveis",
        )
    for src in sources:
        require(
            src.get("url", "").startswith("https://") and src.get("title") and src.get("retrieved"),
            f"{gid}: metadados de fonte inválidos",
        )
    return obj


def validate(root: Path = ROOT, lang="pt-BR") -> dict:
    require_local_links(root)
    require(lang in LANGUAGES, "idioma inválido")
    for p in root.glob("data/**/*.json"):
        read_json(p)
    for p in root.glob("guides/**/*.json"):
        read_json(p)
    catalog = read_json(root / "data/games.json")
    require(catalog.get("schemaVersion") == 1, "versão de catálogo inválida")
    evidence = read_json(root / "data/title-id-evidence.json")["entries"]
    ev = {(e["gameId"], e["region"], e["titleId"]) for e in evidence if e.get("sources")}
    regions = read_json(root / "data/regions.json")
    ids = {}
    seen = set()
    guides = pages = 0
    missing = []
    for g in catalog["games"]:
        gid = g.get("id")
        require(slug(gid) and gid not in seen, f"Game ID inválido/duplicado: {gid}")
        seen.add(gid)
        field(g["name"], 96)
        require(g["franchise"] in {"mario", "pokemon", "zelda", "kirby"}, "franquia inválida")
        require(g["platform"] == "Nintendo 3DS", "plataforma inválida")
        for r, tids in g["titleIds"].items():
            require(
                r in regions and isinstance(tids, list) and len(tids) == len(set(tids)),
                "região/IDs inválidos",
            )
            for tid in tids:
                require(TID.fullmatch(tid), f"Title ID inválido (não derivar de update): {tid}")
                require(tid not in ids or ids[tid] == gid, f"Title ID conflitante: {tid}")
                require((gid, r, tid) in ev, f"Title ID sem evidência: {gid}/{r}/{tid}")
                ids[tid] = gid
        gd = guide_data(root, lang, gid)
        if gd:
            require(g["titleIds"], f"{gid}: guia sem Title ID confirmado")
            guides += 1
            pages += len(gd["pages"])
            require(
                g["guides"].get(lang, "missing") == gd["coverage"],
                f"{gid}: cobertura inconsistente",
            )
        else:
            require(
                g["guides"].get(lang, "missing") == "missing", f"{gid}: guia declarado mas ausente"
            )
            missing.append(gid)
    for index in root.glob("guides/*/*/guide.json"):
        require(index.parent.name in seen, f"{index}: guia sem jogo no catálogo")
        require(index.parent.parent.name in LANGUAGES, f"{index}: idioma inválido")
        obj = read_json(index)
        require(
            obj.get("gameId") == index.parent.name
            and obj.get("language") == index.parent.parent.name,
            f"{index}: associação de guia inválida",
        )
    for f in root.glob("data/franchises/*.json"):
        refs = read_json(f)["gameIds"]
        require(len(refs) == len(set(refs)), "franquia duplicada")
        require(
            set(refs) == {g["id"] for g in catalog["games"] if g["franchise"] == f.stem},
            f"{f}: índice de franquia desatualizado",
        )
    require(guides > 0, f"{lang}: nenhum guia instalado para este idioma")
    asset_registry = read_json(root / "ASSET_LICENSES.json")
    paths = set()
    for asset in asset_registry["assets"]:
        p = inside(root, asset["path"])
        require(p.stat().st_size <= 4 * 1024 * 1024, "asset maior que 4 MiB")
        require(asset["path"] not in paths, "asset duplicado no registro")
        paths.add(asset["path"])
        require(
            asset.get("author")
            and asset.get("source")
            and asset.get("url")
            and asset.get("accessed"),
            "asset sem atribuição",
        )
        require(
            asset.get("license") in {"CC-BY-4.0", "CC0-1.0", "MIT", "public-domain"},
            "licença de asset não permitida automaticamente",
        )
        require(
            hashlib.sha256(p.read_bytes()).hexdigest() == asset.get("sha256"),
            "checksum do asset não confere",
        )
        if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}:
            from PIL import Image, UnidentifiedImageError

            try:
                with Image.open(p) as image:
                    require(
                        0 < image.width <= 2048 and 0 < image.height <= 2048,
                        "imagem fora do limite de 2048 pixels",
                    )
                    image.verify()
            except (OSError, UnidentifiedImageError, Image.DecompressionBombError) as exc:
                raise Invalid(f"asset raster inválido: {p}") from exc
    for p in root.glob("assets/**/*"):
        if p.is_file() and p.suffix.lower() in {
            ".png",
            ".jpg",
            ".jpeg",
            ".ppm",
            ".svg",
            ".webp",
            ".bmp",
        }:
            require(p.relative_to(root).as_posix() in paths, f"asset sem licença: {p}")
    maps = read_json(root / "assets/maps.json")["maps"]
    keys = set()
    for m in maps:
        require(m["gameId"] in seen and slug(m["id"]), "mapa inválido")
        require((m["gameId"], m["id"]) not in keys, "mapa duplicado")
        keys.add((m["gameId"], m["id"]))
        require(m["asset"] in paths, "mapa sem asset licenciado")
        require(
            type(m.get("levels")) is int and 1 <= m["levels"] <= 3, "níveis de zoom fora do limite"
        )
        require(
            320 <= m["width"] <= 2048 and 192 <= m["height"] <= 2048, "dimensões fora do limite"
        )
    for g in catalog["games"]:
        gd = guide_data(root, lang, g["id"])
        if gd:
            for p in gd["pages"]:
                if p.get("map"):
                    require((g["id"], p["map"]) in keys, "mapa referenciado ausente")
    return {
        "games": len(seen),
        "uniqueTitleIds": len(ids),
        "regionalVariants": sum(len(v) for g in catalog["games"] for v in g["titleIds"].values()),
        "guides": guides,
        "pages": pages,
        "missingGuides": missing,
        "maps": len(maps),
    }


def compile_guide(root: Path, lang: str, gid: str, out: Path, hardware=False):
    obj = guide_data(root, lang, gid)
    if not obj:
        return
    if hardware:
        obj = dict(obj)
        candidates = [p for p in obj["pages"] if not p["id"].startswith("dex-")]
        # Keep the opening page and map probes while excluding the full Pokédex.
        preferred = candidates[:1] + [p for p in candidates if p.get("map")] + candidates
        editorial = list({p["id"]: p for p in preferred}.values())[:12]
        probes = [p for p in obj["pages"] if p["id"] in {"dex-006", "dex-025", "dex-716"}]
        obj["pages"] = editorial + probes
    base = root / "guides" / lang / gid
    texts = [plain(read_text_source(inside(base, p["file"]))).encode("utf-8") for p in obj["pages"]]
    offset = 12 + PAGE.size * len(texts)
    records = []
    search = set()
    for i, (p, text) in enumerate(zip(obj["pages"], texts)):
        records.append(
            PAGE.pack(
                field(p["id"], 48),
                field(p["title"], 96),
                int(p.get("spoiler", False)),
                offset,
                len(text),
                zlib.crc32(text),
                field(p.get("map", ""), 48),
            )
        )
        offset += len(text)
        content = fold(
            p["title"] + " " + text.decode("utf-8") + " " + " ".join(p.get("keywords", []))
        )
        for word in (
            re.findall(r"[a-z0-9]+", content)
            + [fold(k) for k in p.get("keywords", [])]
            + [fold(p["title"])]
        ):
            if 2 <= len(word.encode("utf-8")) < 64:
                search.add((word, i))
    require(offset <= MAX_GUIDE, "guia ultrapassa 4 MiB")
    index = b"".join(records)
    pack = b"UGG1" + struct.pack("<II", len(records), zlib.crc32(index)) + index + b"".join(texts)
    folder = out / "guides" / lang
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{gid}.ugg").write_bytes(pack)
    migration_file = root / "data/migrations/alpha-0.1.0-pt-BR.json"
    if not hardware and migration_file.is_file() and lang == "pt-BR":
        old = read_json(migration_file).get(gid)
        if old:
            positions = {p["id"]: i for i, p in enumerate(obj["pages"])}
            mapping = b"".join(
                struct.pack("<I", positions.get(pid, 0xFFFFFFFF)) for pid in old["pageIds"]
            )
            (folder / f"{gid}.ugr").write_bytes(
                b"UGR1"
                + struct.pack(
                    "<IIII",
                    old["fingerprint"],
                    zlib.crc32(index),
                    len(old["pageIds"]),
                    zlib.crc32(mapping),
                )
                + mapping
            )
    require(len(search) <= 131072, "índice de busca grande demais")
    (folder / f"{gid}.ugs").write_bytes(
        b"UGS2"
        + struct.pack("<II", len(search), zlib.crc32(index))
        + b"".join(field(word, 64) + struct.pack("<I", i) for word, i in sorted(search))
    )


def compile_maps(root: Path, out: Path, selected=None):
    maps = read_json(root / "assets/maps.json")["maps"]
    if not maps:
        return
    try:
        from PIL import Image
    except ImportError as exc:
        raise Invalid(
            "Pillow necessário para converter mapas; pip install -r requirements-dev.txt"
        ) from exc
    Image.MAX_IMAGE_PIXELS = 16_000_000
    for m in maps:
        if selected is not None and m["gameId"] not in selected:
            continue
        with Image.open(inside(root, m["asset"])) as image:
            image = image.convert("RGB")
            require(image.size == (m["width"], m["height"]), "mapa com dimensões inconsistentes")
            folder = out / "maps" / m["gameId"]
            folder.mkdir(parents=True, exist_ok=True)
            dims = []
            for z in range(m["levels"]):
                divisor = 2 ** (m["levels"] - z - 1)
                w = math.ceil(image.width / divisor)
                h = math.ceil(image.height / divisor)
                resized = image.resize((w, h), Image.Resampling.LANCZOS)
                cols = math.ceil(w / 320)
                rows = math.ceil(h / 192)
                require(cols <= 64 and rows <= 64, "mapa com tiles demais")
                dims.append(struct.pack("<II", cols, rows))
                for y in range(rows):
                    for x in range(cols):
                        tile = resized.crop(
                            (x * 320, y * 192, min(w, (x + 1) * 320), min(h, (y + 1) * 192))
                        )
                        pixels = bytearray()
                        for r, g, b in tile.get_flattened_data():
                            pixels += struct.pack(
                                "<H", ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
                            )
                        header = b"UGI1" + struct.pack(
                            "<III", tile.width, tile.height, zlib.crc32(pixels)
                        )
                        (folder / f"{m['id']}-{z}-{x}-{y}.ugi").write_bytes(header + pixels)
            data = b"".join(dims)
            (folder / f"{m['id']}.ugm").write_bytes(
                b"UGM1" + struct.pack("<II", len(dims), zlib.crc32(data)) + data
            )


def hardware_status(root: Path):
    report = root / "data/hardware-tests.json"
    if report.is_file():
        data = read_json(report)
        return data["currentVersion"] + ": " + data["currentStatus"]
    return "NEEDS HARDWARE RETEST"


def compile_data(root: Path = ROOT, lang="pt-BR", stage: Path | None = None, hardware=False):
    stats = validate(root, lang)
    stage = stage or root / "build/sd"
    out = stage / "3ds/UniversalGameGuide"
    require(
        stage.resolve().is_relative_to((root / "build").resolve())
        and (root / "build").resolve().is_relative_to(root.resolve()),
        "staging fora de build/ do projeto",
    )
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    games = read_json(root / "data/games.json")["games"]
    byid = {}
    selected = PILOTS if hardware else None
    for g in games:
        if selected is not None and g["id"] not in selected:
            continue
        for tids in g["titleIds"].values():
            for tid in tids:
                byid[tid] = g
        compile_guide(root, lang, g["id"], out, hardware)
    records = [
        TITLE.pack(int(tid, 16), field(g["id"], 64), field(g["name"], 96))
        for tid, g in sorted(byid.items())
    ]
    (out / "titles.bin").write_bytes(b"UGT1" + struct.pack("<I", len(records)) + b"".join(records))
    compile_maps(root, out, selected)
    if hardware:
        stats = dict(stats)
        stats["catalogGames"] = stats["games"]
        stats["games"] = len(PILOTS)
        stats["uniqueTitleIds"] = len(byid)
        stats["regionalVariants"] = sum(
            len(v) for g in games if g["id"] in PILOTS for v in g["titleIds"].values()
        )
        stats["guides"] = len(list((out / "guides" / lang).glob("*.ugg")))
        stats["pages"] = sum(
            struct.unpack_from("<I", p.read_bytes(), 4)[0]
            for p in (out / "guides" / lang).glob("*.ugg")
        )
        stats["missingGuides"] = []
        stats["maps"] = sum(
            m["gameId"] in PILOTS for m in read_json(root / "assets/maps.json")["maps"]
        )
    (out / "state").mkdir(exist_ok=True)
    (out / "runtime").mkdir(exist_ok=True)
    (out / "logs").mkdir(exist_ok=True)
    (out / "VERSION").write_text(
        version(root)
        + "\nprofile="
        + ("hardware-test" if hardware else "release")
        + "\n"
        + hardware_status(root)
        + "\n"
    )
    (out / "state/README.txt").write_text(
        "Progresso local. Faça backup desta pasta. Nenhum save do jogo é lido ou alterado.\n"
    )
    manifest = {
        "formatVersion": 1,
        "language": lang,
        "version": version(root),
        "profile": "hardware-test" if hardware else "release",
        "hardwareTested": False,
        "hardwareStatus": "NEEDS HARDWARE RETEST",
        "previousHardwareResult": hardware_status(root),
        "guideCoverage": "partial",
        "statistics": stats,
        "files": {
            p.relative_to(out).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(out.rglob("*"))
            if p.is_file()
        },
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    return stats, stage


def verify_pack(path: Path):
    data = path.read_bytes()
    require(data[:4] == b"UGG1" and len(data) >= 12, "magic de guia inválido")
    n, crc = struct.unpack_from("<II", data, 4)
    require(0 < n <= MAX_PAGES, "contagem inválida")
    index = data[12 : 12 + n * PAGE.size]
    require(len(index) == n * PAGE.size and zlib.crc32(index) == crc, "índice corrompido")
    end = 12 + len(index)
    for i in range(n):
        _, _, flags, offset, size, checksum, _ = PAGE.unpack_from(index, i * PAGE.size)
        require(
            flags <= 1 and offset == end and 0 < size <= MAX_TEXT and offset + size <= len(data),
            "offset inválido",
        )
        text = data[offset : offset + size]
        require(zlib.crc32(text) == checksum, "texto corrompido")
        text.decode("utf-8")
        end = offset + size
    require(end == len(data), "bytes extras no guia")


def write_zip(tree: Path, archive: Path):
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for p in sorted(tree.rglob("*")):
            if p.is_file():
                info = zipfile.ZipInfo(p.relative_to(tree).as_posix(), (2026, 10, 4, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                zf.writestr(info, p.read_bytes())
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix(".zip.sha256").write_text(f"{checksum}  {archive.name}\n")
    return checksum


def coverage(root: Path = ROOT, lang="pt-BR"):
    games = read_json(root / "data/games.json")["games"]
    lines = [
        "# Cobertura " + version(root),
        "",
        hardware_status(root)
        + ". Percentuais medem presença de guia, não completude do walkthrough. "
        "Revisado é revisão editorial declarada, nunca teste físico.",
        "",
    ]
    total = {"complete": 0, "partial": 0, "missing": 0}
    for franchise in ["mario", "pokemon", "zelda", "kirby"]:
        group = [g for g in games if g["franchise"] == franchise]
        available = sum((root / "guides" / lang / g["id"] / "guide.json").is_file() for g in group)
        percent = round(100 * available / len(group))
        filled = round(percent / 10)
        lines.append(
            f"{franchise.title()}: {'█' * filled}{'░' * (10 - filled)} {percent}% com guia ({available}/{len(group)})"
        )
    lines += [
        "",
        "| Jogo | IDs únicos | Guia | Páginas | Mapas | Busca | Revisado |",
        "|---|---:|---|---:|---:|---|---|",
    ]
    missing = []
    gaps = [
        "# Lacunas de conteúdo — " + version(root),
        "",
        "Gerado pelo Guide Builder. Nenhum guia parcial é contado como completo. "
        + hardware_status(root)
        + ". Os itens abaixo são conteúdo ainda faltante ou não revisado.",
        "",
    ]
    for g in games:
        path = root / "guides" / lang / g["id"] / "guide.json"
        obj = read_json(path) if path.is_file() else None
        key = "missing" if not obj else "complete" if obj["coverage"] == "complete" else "partial"
        total[key] += 1
        if not obj:
            missing.append(g["name"])
        count = len(obj["pages"]) if obj else 0
        gaps += ["## " + g["name"], ""]
        if obj:
            gaps += [
                f"Estado: {obj['coverage']}; {count} páginas; revisão editorial: "
                + ("sim." if obj.get("reviewed") else "pendente."),
                "",
            ]
            gaps += ["- " + item for item in obj.get("remaining", [])]
        else:
            gaps += [
                "- Guia ausente. Title ID pendente de confirmação; não criar ID a partir de update/DLC."
            ]
        gaps += [""]
        maps = len({p.get("map") for p in obj["pages"] if p.get("map")}) if obj else 0
        ids = len({tid for tids in g["titleIds"].values() for tid in tids})
        label = (
            "Sem guia"
            if not obj
            else "Completo"
            if key == "complete"
            else "Parcial / " + obj["coverage"]
        )
        lines.append(
            f"| {g['name']} | {ids} | {label} | {count} | {maps} | {'Sim' if obj else 'Não'} | {'Sim' if obj and obj.get('reviewed') else 'Não'} |"
        )
    lines += [
        "",
        f"Completos: {total['complete']}; parciais: {total['partial']}; sem guia: {total['missing']}.",
        "",
        "Faltantes: " + (", ".join(missing) or "nenhum"),
        "",
        "Veja os campos remaining em guide.json para as lacunas exatas de cada guia parcial.",
    ]
    (root / "COVERAGE.md").write_text("\n".join(lines) + "\n")
    (root / "CONTENT_GAPS.md").write_text("\n".join(gaps) + "\n")
    return total


def source_package(root: Path):
    source = root / "build/source-release"
    require(source.resolve().is_relative_to(root.resolve()), "source staging inválido")
    if source.exists():
        shutil.rmtree(source)
    source.mkdir(parents=True)
    for folder in [
        "plugin",
        "tools",
        "scripts",
        "data",
        "guides",
        "assets",
        "docs",
        "tests",
        ".github",
    ]:
        for p in sorted((root / folder).rglob("*")):
            if (
                p.is_file()
                and not {"build", "build-minimal", "build-minimal-boot"}.intersection(p.parts)
                and "__pycache__" not in p.parts
                and p.suffix not in {".elf", ".3gx", ".pyc", ".map", ".o", ".d", ".a", ".dmp"}
                and not p.name.endswith(".sections.txt")
            ):
                require(
                    p.resolve().is_relative_to(root.resolve()) and not p.is_symlink(),
                    "fonte externa recusada",
                )
                t = source / p.relative_to(root)
                t.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, t)
    for p in sorted(root.glob("*")):
        if p.is_file() and (
            p.suffix in {".md", ".json", ".txt", ".toml"}
            or p.name in {"LICENSE", "VERSION", "builder.py"}
        ):
            require(
                not p.is_symlink() and p.resolve().is_relative_to(root.resolve()),
                "fonte raiz externa recusada",
            )
            shutil.copy2(p, source / p.name)
    for name in [".gitignore", ".gitattributes", ".clang-format"]:
        require(not (root / name).is_symlink(), "configuração de fonte symlink recusada")
        shutil.copy2(root / name, source / name)
    third = root / "build/third-party-source.zip"
    require(third.is_file(), "executar scripts/bundle_sources.py")
    shutil.copy2(third, source / third.name)
    dist = root / "dist"
    require(dist.resolve().is_relative_to(root.resolve()), "dist externo recusado")
    dist.mkdir(exist_ok=True)
    archive = dist / f"3DS-Universal-Game-Guide-SOURCE-v{version(root)}.zip"
    return archive, write_zip(source, archive)


def package(
    root: Path = ROOT, lang="pt-BR", plugin: Path | None = None, hardware=False, archive_name=None
):
    plugin = plugin or root / "plugin/default.3gx"
    require(plugin.is_file(), ".3gx ausente")
    binary = plugin.read_bytes()
    require(binary[:8] == b"3GX$0002" and 160 <= len(binary) <= 2 * 1024 * 1024, ".3gx inválido")
    stage = root / "build" / ("hardware-test" if hardware else f"package-{lang}")
    require(stage.resolve().is_relative_to(root.resolve()), "staging externo recusado")
    if stage.exists():
        shutil.rmtree(stage)
    stats, stage = compile_data(root, lang, stage, hardware)
    target = stage / "luma/plugins"
    target.mkdir(parents=True)
    shutil.copy2(plugin, target / "default.3gx")
    out = stage / "3ds/UniversalGameGuide"
    # Legal notices are runtime redistribution requirements, not development files.
    notices = (root / "LICENSE").read_text() + "\n" + (root / "THIRD_PARTY_NOTICES.md").read_text()
    for p in sorted((root / "docs/licenses").glob("*")):
        notices += "\n\n" + p.name + "\n" + p.read_text()
    (out / "LICENSES.txt").write_text(notices)
    registry = read_json(root / "ASSET_LICENSES.json")
    maps = read_json(root / "assets/maps.json")["maps"]
    used = {m["asset"] for m in maps if not hardware or m["gameId"] in PILOTS}
    registry["assets"] = [a for a in registry["assets"] if a["path"] in used]
    (out / "ASSET_LICENSES.json").write_text(
        json.dumps(registry, ensure_ascii=False, indent=2) + "\n"
    )
    if hardware:
        shutil.copy2(root / "HARDWARE_TEST.md", stage / "HARDWARE_TEST.md")
    else:
        shutil.copy2(root / "INSTALL_PTBR.md", stage / "INSTALL_PTBR.md")
    if (root / "HARDWARE_RETEST.md").is_file():
        shutil.copy2(root / "HARDWARE_RETEST.md", stage / "HARDWARE_RETEST.md")
    for pack in stage.rglob("*.ugg"):
        verify_pack(pack)
    checks = {
        p.relative_to(stage).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(stage.rglob("*"))
        if p.is_file()
    }
    (out / "SHA256SUMS.txt").write_text("".join(f"{sha}  {path}\n" for path, sha in checks.items()))
    dist = root / "dist"
    require(dist.resolve().is_relative_to(root.resolve()), "dist externo recusado")
    dist.mkdir(exist_ok=True)
    default_name = (
        f"UniversalGameGuide-{'PTBR' if lang == 'pt-BR' else 'EN'}-Hardware-Test.zip"
        if hardware
        else f"UniversalGameGuide-{'PTBR' if lang == 'pt-BR' else 'EN'}-v{version(root)}.zip"
    )
    name = archive_name or default_name
    require(Path(name).name == name and name.endswith(".zip"), "nome de ZIP inválido")
    archive = dist / name
    checksum = write_zip(stage, archive)
    return {
        "archive": str(archive),
        "sha256": checksum,
        "profile": "hardware-test" if hardware else "release",
        **stats,
    }


def release(root=ROOT, lang="pt-BR", plugin=None):
    validate(root, lang)
    totals = coverage(root, lang)
    normal = package(root, lang, plugin)
    hardware = package(root, lang, plugin, True)
    source, sha = source_package(root)
    sums = [
        (normal["sha256"], Path(normal["archive"]).name),
        (hardware["sha256"], Path(hardware["archive"]).name),
        (sha, source.name),
    ]
    (root / "dist/SHA256SUMS.txt").write_text("".join(f"{h}  {n}\n" for h, n in sums))
    return {
        "version": version(root),
        "release": normal,
        "hardware": hardware,
        "source": str(source),
        "sourceSha256": sha,
        "coverage": totals,
    }


def check_links(root: Path = ROOT):
    local = local_links(root)
    target = root / "build/local-link-report.json"
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(local, ensure_ascii=False, indent=2) + "\n")
    require_local_links(root)
    urls = set()
    for file in root.glob("guides/**/sources.json"):
        urls.update(src["url"] for src in read_json(file))
    for file in markdown_files(root):
        urls.update(
            target for target in inline_targets(file.read_text()) if target.startswith("https://")
        )

    def fetch(url):
        status = 0
        error = ""
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0 (UniversalGameGuide source-check)"}
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                status = response.status
        except urllib.error.HTTPError as exc:
            status = exc.code
            error = str(exc)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            error = str(exc)
        verdict = (
            "reachable"
            if 200 <= status < 400
            else "broken"
            if status in {404, 410}
            else "blocked"
            if status in {401, 403, 429}
            else "network-pending"
        )
        return {"url": url, "status": status, "verdict": verdict, "error": error}

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        report = list(pool.map(fetch, sorted(urls)))
    target = root / "build/link-report.json"
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=[
            "validate",
            "build",
            "package",
            "release",
            "hardware-test",
            "hardware-retest",
            "coverage",
            "check-links",
            "verify",
        ],
    )
    parser.add_argument("--language", "--lang", default="pt-BR", choices=sorted(LANGUAGES))
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--plugin", type=Path)
    parser.add_argument("--file", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "validate":
            result = validate(args.root, args.language)
            coverage(args.root, args.language)
        elif args.command == "build":
            result = compile_data(args.root, args.language)[0]
        elif args.command == "release":
            result = release(args.root, args.language, args.plugin)
        elif args.command == "hardware-test":
            result = package(args.root, args.language, args.plugin, True)
        elif args.command == "hardware-retest":
            spec = importlib.util.spec_from_file_location(
                "hardware_release", args.root / "scripts/hardware_release.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            result = module.build_retest(args.root, args.language)
        elif args.command == "coverage":
            result = coverage(args.root, args.language)
        elif args.command == "package":
            result = package(args.root, args.language, args.plugin)
        elif args.command == "check-links":
            result = check_links(args.root)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return int(any(r["verdict"] == "broken" for r in result))
        else:
            require(args.file is not None, "--file necessário")
            verify_pack(args.file)
            result = {"verified": str(args.file)}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (Invalid, UnicodeError, KeyError, TypeError) as exc:
        parser.exit(1, f"ERRO: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
