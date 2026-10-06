"""Publishing must reject wrong tags, mixed symbols and uncommitted source."""

import hashlib
import importlib.util
import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("release_assets", ROOT / "scripts/release_assets.py")
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


class ReleaseTests(unittest.TestCase):
    def test_exact_tag_and_prerelease_detection(self):
        for version in ["0.2.3-alpha", "0.3.0-beta.1", "0.3.0-rc.2"]:
            self.assertTrue(r.validate_tag(version, "v" + version))
        self.assertFalse(r.validate_tag("0.3.0", "v0.3.0"))
        for version, tag in [
            ("0.2.3-alpha", "v0.2.2-alpha"),
            ("01.2.3", "v01.2.3"),
            ("0.2", "v0.2"),
            ("0.2.3\n", "v0.2.3\n"),
        ]:
            with self.subTest(version=version):
                self.assertRaises(ValueError, r.validate_tag, version, tag)

    def fixture(self, root):
        for name, raw in {
            "VERSION": b"0.2.3-alpha\n",
            "docs/CTRPF_FILESYSTEM.patch": b"patch\n",
            "data/dependencies.lock.json": b'{"dockerImage":"image@sha256:test","dependencies":[]}\n',
            ".gitignore": b"build/\n",
        }.items():
            p = root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(raw)
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        subprocess.run(["git", "-C", str(root), "add", "."], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "-c",
                "user.name=Fixture",
                "-c",
                "user.email=fixture@localhost",
                "commit",
                "-qm",
                "fixture",
            ],
            check=True,
        )
        commit = r.git(root, "rev-parse", "HEAD")
        (root / "build").mkdir()
        (root / "build/toolchain.json").write_text(
            json.dumps(
                {
                    "dockerImage": "image@sha256:test",
                    "compiler": "fixture compiler",
                    "packages": ["fixture package"],
                }
            )
        )
        identity = r.build_provenance(root)
        identity["variants"] = {}
        symbols, runtime = {}, {}
        for variant in ["minimal-boot", "minimal", "full"]:
            entry = {"variant": variant, "version": "0.2.3-alpha", "commit": commit}
            for ext, kind in [("3gx", "plugin"), ("elf", "elf"), ("map", "map")]:
                name = f"default-{variant}.{ext}"
                raw = name.encode()
                entry[kind] = {"sha256": digest(raw)}
                symbols[name] = raw
                if ext == "3gx":
                    runtime["diagnostics/" + name] = raw
            identity["variants"][variant] = entry
        encoded = json.dumps(identity).encode()
        runtime["luma/plugins/default.3gx"] = symbols["default-minimal-boot.3gx"]
        runtime["diagnostics/BUILD.json"] = symbols["BUILD.json"] = encoded
        source = {n: (root / n).read_bytes() for n in r.git(root, "ls-files").splitlines()}
        source.update({"third-party-source.zip": b"fixture", "BUILD.json": encoded})
        folder = root / "build/dist"
        folder.mkdir()
        files = {}
        for prefix, entries in [
            ("UniversalGameGuide-PTBR-Hardware-Test", runtime),
            ("UniversalGameGuide-Debug-Symbols", symbols),
            ("3DS-Universal-Game-Guide-SOURCE", source),
        ]:
            path = folder / f"{prefix}-v0.2.3-alpha-ci-{commit[:12]}.zip"
            with zipfile.ZipFile(path, "w") as archive:
                for name, raw in entries.items():
                    archive.writestr(name, raw)
            files[prefix] = path
        self.sums(folder)
        return folder, files, commit, identity

    def sums(self, folder):
        (folder / "SHA256SUMS.txt").write_text(
            "".join(f"{r.sha(p)}  {p.name}\n" for p in sorted(folder.glob("*.zip")))
        )

    def replace_entry(self, path, name, raw):
        with zipfile.ZipFile(path) as archive:
            entries = {n: archive.read(n) for n in archive.namelist()}
        entries[name] = raw
        with zipfile.ZipFile(path, "w") as archive:
            for n, data in entries.items():
                archive.writestr(n, data)

    def test_prepare_preserves_zip_bytes_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            folder, files, commit, _ = self.fixture(root)
            out = root / "build/prepared"
            result = r.prepare(folder, out, "v0.2.3-alpha", commit, root)
            self.assertTrue(result["prerelease"])
            for prefix, p in files.items():
                self.assertEqual(p.read_bytes(), (out / f"{prefix}-v0.2.3-alpha.zip").read_bytes())
            for line in (out / "SHA256SUMS.txt").read_text().splitlines():
                value, name = line.split("  ", 1)
                self.assertEqual(r.sha(out / name), value)
            self.assertRaises(ValueError, r.prepare, folder, out, "v0.2.3-alpha", commit, root)

    def test_mixed_full_symbols_rejected_even_after_rehashing_zip(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            folder, files, commit, _ = self.fixture(root)
            self.replace_entry(
                files["UniversalGameGuide-Debug-Symbols"], "default-full.elf", b"wrong build"
            )
            self.sums(folder)
            with self.assertRaisesRegex(ValueError, "Mixed symbols"):
                r.prepare(folder, root / "build/prepared", "v0.2.3-alpha", commit, root)

    def test_source_must_match_every_tagged_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            folder, files, commit, _ = self.fixture(root)
            self.replace_entry(files["3DS-Universal-Game-Guide-SOURCE"], "VERSION", b"old version")
            self.sums(folder)
            with self.assertRaisesRegex(ValueError, "SOURCE differs"):
                r.prepare(folder, root / "build/prepared", "v0.2.3-alpha", commit, root)
            (root / "VERSION").write_text("0.2.3-alpha\n#dirty\n")
            self.assertRaises(
                ValueError, r.prepare, folder, root / "build/prepared", "v0.2.3-alpha", commit, root
            )

    def test_build_metadata_cannot_claim_hardware_pass_or_wrong_commit(self):
        with tempfile.TemporaryDirectory() as temp:
            _, _, commit, identity = self.fixture(Path(temp))
            r.validate_identity(identity, "0.2.3-alpha", commit)
            for key, value in [
                ("commit", "0" * 40),
                ("dirty", True),
                ("classification", "HARDWARE-TESTED"),
                ("currentBinaryHardwareTested", True),
            ]:
                modified = dict(identity, **{key: value})
                self.assertRaises(ValueError, r.validate_identity, modified, "0.2.3-alpha", commit)

    def test_bad_checksum_and_path_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            p = folder / "SHA256SUMS.txt"
            for name in ["../outside.zip", "/outside.zip", "path\\file.zip"]:
                p.write_text("0" * 64 + "  " + name + "\n")
                self.assertRaises(ValueError, r.checked_sums, folder)
