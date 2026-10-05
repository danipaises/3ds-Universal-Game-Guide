"""Offline provenance checks must reject altered data and paths escaping the project."""

import hashlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SourceTests(unittest.TestCase):
    def test_data_hash_and_symlink_escape(self):
        module = script("fetch_data_sources")
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as outside:
            root = Path(temp)
            (root / "data/pokemon").mkdir(parents=True)
            cache = root / "research/pokeapi"
            cache.mkdir(parents=True)
            raw = b"factual test snapshot\n"
            (root / "data/pokemon/source-lock.json").write_text(
                json.dumps(
                    {
                        "files": {
                            "one.csv": {
                                "url": "https://raw.githubusercontent.com/example",
                                "sha256": hashlib.sha256(raw).hexdigest(),
                            }
                        }
                    }
                )
            )
            file = cache / "one.csv"
            file.write_bytes(raw)
            with (
                patch.object(module, "ROOT", root),
                patch("sys.argv", ["fetch", "pokemon", "--offline"]),
                patch("sys.stdout", io.StringIO()),
            ):
                module.main()
                file.write_bytes(raw + b"changed")
                with self.assertRaises(SystemExit):
                    module.main()
                file.unlink()
                cache.rmdir()
                cache.symlink_to(outside, target_is_directory=True)
                with self.assertRaises(SystemExit):
                    module.main()
            self.assertEqual(list(Path(outside).iterdir()), [])

    def test_dependency_paths_cannot_escape(self):
        module = script("fetch_deps")
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as outside:
            root = Path(temp)
            (root / "data").mkdir()
            lock = root / "data/dependencies.lock.json"
            dep = {
                "name": "bad",
                "archive": "one.tar.gz",
                "destination": ".deps/../../outside",
                "sha256": "0" * 64,
            }
            lock.write_text(json.dumps({"dependencies": [dep]}))
            with patch.object(module, "ROOT", root), patch("sys.argv", ["fetch", "--offline"]):
                with self.assertRaises(ValueError):
                    module.main()
                dep["destination"] = ".deps/library"
                dep["archive"] = "../../outside"
                lock.write_text(json.dumps({"dependencies": [dep]}))
                with self.assertRaises(ValueError):
                    module.main()
                dep["archive"] = "one.tar.gz"
                lock.write_text(json.dumps({"dependencies": [dep]}))
                (root / ".deps").symlink_to(outside, target_is_directory=True)
                with self.assertRaises(ValueError):
                    module.main()
            self.assertEqual(list(Path(outside).iterdir()), [])
