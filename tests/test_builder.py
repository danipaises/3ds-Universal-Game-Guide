"""PC checks exercise data contracts and malicious/corrupted inputs."""

import hashlib
import importlib.util
import json
import shutil
import struct
import tempfile
import unittest
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("builder", ROOT / "tools/guide-builder/builder.py")
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


class BuilderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def project(self):
        for folder in ["data", "guides", "assets"]:
            shutil.copytree(ROOT / folder, self.root / folder)
        shutil.copy2(ROOT / "ASSET_LICENSES.json", self.root / "ASSET_LICENSES.json")
        return self.root

    def edit(self, path, fn):
        p = self.root / path
        o = json.loads(p.read_text())
        fn(o)
        p.write_text(json.dumps(o, ensure_ascii=False))

    def test_real_catalog(self):
        stats = b.validate(ROOT)
        self.assertEqual(stats["games"], 68)
        self.assertEqual(stats["guides"], 67)
        self.assertEqual(stats["uniqueTitleIds"], 211)
        self.assertEqual(stats["missingGuides"], ["pokemon-tretta-lab"])
        self.assertGreaterEqual(stats["pages"], 2000)

    def test_duplicate_json_key(self):
        p = self.root / "bad.json"
        p.write_text('{"id":1,"id":2}')
        self.assertRaises(b.Invalid, b.read_json, p)

    def test_path_traversal_and_symlink(self):
        self.assertRaises(b.Invalid, b.inside, self.root, "../etc/passwd")
        self.assertRaises(b.Invalid, b.inside, self.root, "/etc/passwd")
        p = self.root / "escape"
        p.symlink_to("/etc/passwd")
        self.assertRaises(b.Invalid, b.inside, self.root, "escape")

    def test_title_id_wrong_category(self):
        root = self.project()
        self.edit(
            "data/games.json", lambda o: o["games"][0]["titleIds"].update(USA=["0004000E00054000"])
        )
        self.assertRaises(b.Invalid, b.validate, root)

    def test_local_markdown_links(self):
        docs = self.root / "docs"
        docs.mkdir()
        (self.root / "file with spaces.md").write_text("# Heading\n")
        (docs / "ok.md").write_text(
            "[root](../file%20with%20spaces.md#heading) [self](#heading) "
            '[remote](https://example.org/) [title](<../file with spaces.md> "note")'
        )
        self.assertEqual(len(b.require_local_links(self.root)), 2)
        (docs / "bad.md").write_text("[missing](absent.md) [escape](../../outside.md)")
        self.assertRaises(b.Invalid, b.require_local_links, self.root)
        (docs / "bad.md").unlink()
        (docs / "linked.md").symlink_to("/etc/passwd")
        (docs / "ok.md").write_text("[symlink](linked.md)")
        self.assertRaises(b.Invalid, b.require_local_links, self.root)

    def test_conflicting_title_id(self):
        root = self.project()
        self.edit(
            "data/games.json",
            lambda o: o["games"][1]["titleIds"].update(USA=o["games"][0]["titleIds"]["USA"]),
        )
        self.assertRaises(b.Invalid, b.validate, root)

    def test_id_without_evidence(self):
        root = self.project()
        self.edit("data/title-id-evidence.json", lambda o: o.update(entries=[]))
        self.assertRaises(b.Invalid, b.validate, root)

    def test_missing_index(self):
        root = self.project()
        (root / "guides/pt-BR/super-mario-3d-land/guide.json").unlink()
        self.assertRaises(b.Invalid, b.validate, root)

    def test_oversize_and_controls(self):
        self.assertRaises(b.Invalid, b.plain, "á" * 4097)
        self.assertRaises(b.Invalid, b.plain, "hello\0")
        self.assertRaises(b.Invalid, b.plain, "hello\x7f")
        self.assertRaises(b.Invalid, b.field, "hello\x7f", 96)
        self.assertEqual(b.plain("linha 1\rlinha 2"), "linha 1\nlinha 2\n")
        self.assertRaises(b.Invalid, b.field, "á" * 48, 96)

    def test_asset_without_license(self):
        root = self.project()
        (root / "assets/uncredited.png").write_bytes(b"png")
        self.assertRaises(b.Invalid, b.validate, root)

    def test_asset_tamper(self):
        root = self.project()
        p = next((root / "assets/maps").glob("*.png"))
        p.write_bytes(b"changed")
        self.assertRaises(b.Invalid, b.validate, root)

    def test_map_missing(self):
        root = self.project()
        self.edit("assets/maps.json", lambda o: o.update(maps=[]))
        self.assertRaises(b.Invalid, b.validate, root)

    def test_pack_crc_and_offsets(self):
        stage = self.root / "sd"
        b.compile_guide(ROOT, "pt-BR", "super-mario-3d-land", stage)
        pack = stage / "guides/pt-BR/super-mario-3d-land.ugg"
        b.verify_pack(pack)
        data = pack.read_bytes()
        mut = bytearray(data)
        mut[-1] ^= 1
        pack.write_bytes(mut)
        self.assertRaises(b.Invalid, b.verify_pack, pack)
        pack.write_bytes(data + b"extra")
        self.assertRaises(b.Invalid, b.verify_pack, pack)

    def test_deterministic_generation_and_search_binding(self):
        a = self.root / "a"
        c = self.root / "b"
        b.compile_guide(ROOT, "pt-BR", "pokemon-x", a)
        b.compile_guide(ROOT, "pt-BR", "pokemon-x", c)
        for suffix in ["ugg", "ugs"]:
            self.assertEqual(
                (a / f"guides/pt-BR/pokemon-x.{suffix}").read_bytes(),
                (c / f"guides/pt-BR/pokemon-x.{suffix}").read_bytes(),
            )
        guide = (a / "guides/pt-BR/pokemon-x.ugg").read_bytes()
        search = (a / "guides/pt-BR/pokemon-x.ugs").read_bytes()
        self.assertEqual(search[:4], b"UGS2")
        self.assertEqual(guide[8:12], search[8:12])
        self.assertGreater(struct.unpack_from("<I", search, 4)[0], 32768)

    def test_pokemon_historical_values(self):
        rows = b.read_json(ROOT / "data/pokemon/gen6.json")["records"]
        p = {r["number"]: r for r in rows}
        self.assertEqual(len(rows), 721)
        self.assertEqual(p[51]["stats"][1], 80)
        self.assertEqual(p[94]["abilities"][0]["name"], "Levitate")
        self.assertEqual(p[6]["damageMultipliers"]["Rock"], 4)
        self.assertEqual(p[35]["types"], ["Fairy"])
        self.assertTrue(any("220" in e for e in p[133]["evolutions"]))
        self.assertTrue(any("cabeça para baixo" in e for e in p[686]["evolutions"]))
        self.assertTrue(
            any(e["area"] == "Kalos Route 2" and e["version"] == "X" for e in p[659]["encounters"])
        )

    def test_missing_required_section(self):
        root = self.project()
        self.edit(
            "guides/pt-BR/pokemon-x/guide.json",
            lambda o: o.update(requiredSections=["never-authored"]),
        )
        self.assertRaises(b.Invalid, b.validate, root)

    def test_complete_requires_review(self):
        root = self.project()
        self.edit(
            "guides/pt-BR/pokemon-x/guide.json",
            lambda o: o.update(coverage="complete", reviewed=False),
        )
        self.assertRaises(b.Invalid, b.guide_data, root, "pt-BR", "pokemon-x")

    def test_bad_text_encoding_and_huge_source(self):
        path = self.root / "page.md"
        path.write_bytes(b"bad \xff")
        self.assertRaises(b.Invalid, b.read_text_source, path)
        path.write_bytes(b"a" * (b.MAX_SOURCE_TEXT + 1))
        self.assertRaises(b.Invalid, b.read_text_source, path)
        self.assertRaises(b.Invalid, b.field, "\ud800", 96)
        self.assertRaises(b.Invalid, b.plain, "\ud800")
        path.write_bytes(b"\xff")
        self.assertRaises(b.Invalid, b.read_json, path)

    def test_invalid_raster_even_with_matching_hash(self):
        root = self.project()
        registry = b.read_json(root / "ASSET_LICENSES.json")
        asset = registry["assets"][0]
        path = root / asset["path"]
        path.write_bytes(b"not an image")
        asset["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        (root / "ASSET_LICENSES.json").write_text(json.dumps(registry))
        self.assertRaises(b.Invalid, b.validate, root)

    def test_oversized_raster(self):
        from PIL import Image

        root = self.project()
        registry = b.read_json(root / "ASSET_LICENSES.json")
        asset = registry["assets"][0]
        path = root / asset["path"]
        Image.new("RGB", (2049, 2)).save(path)
        asset["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        (root / "ASSET_LICENSES.json").write_text(json.dumps(registry))
        self.assertRaises(b.Invalid, b.validate, root)

    def test_language_header_mismatch(self):
        root = self.project()
        self.edit("guides/pt-BR/pokemon-x/guide.json", lambda o: o.update(language="en-US"))
        self.assertRaises(b.Invalid, b.validate, root)

    def test_missing_language_cannot_produce_empty_release(self):
        self.assertRaises(b.Invalid, b.validate, ROOT, "en-US")

    def test_legacy_migration_is_bound_to_guide(self):
        stage = self.root / "sd"
        b.compile_guide(ROOT, "pt-BR", "pokemon-x", stage)
        pack = (stage / "guides/pt-BR/pokemon-x.ugg").read_bytes()
        migration = (stage / "guides/pt-BR/pokemon-x.ugr").read_bytes()
        magic, old, new, count, crc = struct.unpack_from("<4sIIII", migration)
        baseline = b.read_json(ROOT / "data/migrations/alpha-0.1.0-pt-BR.json")["pokemon-x"]
        self.assertEqual(magic, b"UGR1")
        self.assertEqual(old, baseline["fingerprint"])
        self.assertEqual(new, struct.unpack_from("<I", pack, 8)[0])
        self.assertEqual(count, len(baseline["pageIds"]))
        self.assertEqual(len(migration), 20 + 4 * count)
        self.assertEqual(zlib.crc32(migration[20:]), crc)

    def test_hardware_subset_contains_probe_and_limits(self):
        stage = self.root / "sd"
        b.compile_guide(ROOT, "pt-BR", "pokemon-x", stage, hardware=True)
        pack = (stage / "guides/pt-BR/pokemon-x.ugg").read_bytes()
        count = struct.unpack_from("<I", pack, 4)[0]
        self.assertLessEqual(count, 15)
        ids = [
            b.PAGE.unpack_from(pack, 12 + i * b.PAGE.size)[0].split(b"\0", 1)[0]
            for i in range(count)
        ]
        self.assertIn(b"dex-006", ids)
        self.assertNotIn(b"dex-721", ids)
        b.verify_pack(stage / "guides/pt-BR/pokemon-x.ugg")

    def test_package_runtime_only_and_preserves_user_state(self):
        root = self.project()
        for name in [
            "VERSION",
            "LICENSE",
            "THIRD_PARTY_NOTICES.md",
            "HARDWARE_TEST.md",
            "HARDWARE_RETEST.md",
            "INSTALL_PTBR.md",
        ]:
            shutil.copy2(ROOT / name, root / name)
        shutil.copytree(ROOT / "docs/licenses", root / "docs/licenses")
        plugin = root / "fixture.3gx"
        plugin.write_bytes(b"3GX$0002" + b"\0" * 152)
        result = b.package(root, "pt-BR", plugin, hardware=True)
        with zipfile.ZipFile(result["archive"]) as archive:
            names = archive.namelist()
            self.assertIn("luma/plugins/default.3gx", names)
            self.assertIn("HARDWARE_TEST.md", names)
            self.assertFalse(any(n.endswith((".py", ".cpp", ".hpp", ".elf")) for n in names))
            self.assertFalse(any("/source/" in n or "/tests/" in n for n in names))
            self.assertFalse(
                any(
                    n.endswith("config.bin") or "/state/" in n and n.endswith(".bin") for n in names
                )
            )
            self.assertEqual(sum(n.endswith(".ugg") for n in names), 6)
            self.assertIn(b"hardware-test", archive.read("3ds/UniversalGameGuide/VERSION"))

    def test_markdown_urls_keep_balanced_parentheses(self):
        text = (
            "[Stage](https://example.org/World_4-1_(Super_Mario_3D_Land)) "
            '[File](<a folder/guide.md>) [Title](guide.md "optional title")'
        )
        self.assertEqual(
            list(b.inline_targets(text)),
            [
                "https://example.org/World_4-1_(Super_Mario_3D_Land)",
                "a folder/guide.md",
                "guide.md",
            ],
        )

    def test_coverage_records_exact_content_gaps(self):
        root = self.project()
        shutil.copy2(ROOT / "VERSION", root / "VERSION")
        counts = b.coverage(root)
        self.assertEqual(counts, {"complete": 0, "partial": 67, "missing": 1})
        report = (root / "CONTENT_GAPS.md").read_text()
        mario = b.read_json(root / "guides/pt-BR/super-mario-3d-land/guide.json")
        self.assertIn(mario["remaining"][0], report)
        self.assertIn("Pokémon Tretta Lab", report)

    def test_hardware_retains_maps_as_probes(self):
        stage = self.root / "sd"
        for gid in b.PILOTS:
            b.compile_guide(ROOT, "pt-BR", gid, stage, hardware=True)
            data = (stage / f"guides/pt-BR/{gid}.ugg").read_bytes()
            count = struct.unpack_from("<I", data, 4)[0]
            maps = {
                b.PAGE.unpack_from(data, 12 + i * b.PAGE.size)[-1].split(b"\0", 1)[0].decode()
                for i in range(count)
            }
            full = b.read_json(ROOT / f"guides/pt-BR/{gid}/guide.json")
            expected = {p["map"] for p in full["pages"] if p.get("map")}
            self.assertTrue(expected <= maps)

    def test_source_rejects_root_symlinks(self):
        root = self.project()
        outside = self.root / "outside.md"
        outside.write_text("not part of source")
        (root / "README.md").symlink_to(outside)
        self.assertRaises(b.Invalid, b.source_package, root)


if __name__ == "__main__":
    unittest.main()
