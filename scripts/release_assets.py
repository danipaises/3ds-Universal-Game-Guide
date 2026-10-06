#!/usr/bin/env python3
"""Record build provenance and prepare immutable GitHub Release downloads."""

import argparse
import hashlib
import io
import json
import re
import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(
    r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)(?:-[0-9A-Za-z]+(?:[.-][0-9A-Za-z]+)*)?"
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def validate_tag(version, tag):
    if not SEMVER.fullmatch(version) or tag != "v" + version:
        raise ValueError("Release tag must exactly match SemVer in VERSION")
    return "-" in version


def build_provenance(root=ROOT):
    try:
        commit = git(root, "rev-parse", "HEAD")
        dirty = bool(git(root, "status", "--porcelain", "--untracked-files=all"))
    except subprocess.CalledProcessError:
        # A SOURCE extraction can be built, but cannot publish a tag without Git.
        commit, dirty = None, True
    lock_path = root / "data/dependencies.lock.json"
    lock = json.loads(lock_path.read_text())
    toolchain = json.loads((root / "build/toolchain.json").read_text())
    if toolchain["dockerImage"] != lock["dockerImage"]:
        raise ValueError("Toolchain image differs from dependency lock")
    for dep in lock["dependencies"]:
        if sha(root / "research" / dep["archive"]) != dep["sha256"]:
            raise ValueError("Dependency archive mismatch: " + dep["name"])
    return {
        "schemaVersion": 2,
        "commit": commit,
        "dirty": dirty,
        "version": (root / "VERSION").read_text().strip(),
        "classification": "CI-REBUILT",
        "currentBinaryHardwareTested": False,
        "status": "NEEDS HARDWARE RETEST",
        "toolchain": toolchain,
        "dependencies": lock,
        "dependencyLockSha256": sha(lock_path),
        "frameworkPatchSha256": sha(root / "docs/CTRPF_FILESYSTEM.patch"),
    }


def validate_identity(identity, version, commit):
    if identity.get("commit") != commit or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("BUILD.json commit differs from tag checkout")
    if identity.get("version") != version or identity.get("dirty") is not False:
        raise ValueError("BUILD.json version mismatch or dirty source")
    if (
        identity.get("classification") != "CI-REBUILT"
        or identity.get("currentBinaryHardwareTested") is not False
    ):
        raise ValueError("Newly built artifacts cannot claim physical validation")
    if not identity.get("toolchain", {}).get("compiler") or not identity.get("toolchain", {}).get(
        "packages"
    ):
        raise ValueError("Compiler/package versions absent")
    if identity["toolchain"]["dockerImage"] != identity["dependencies"]["dockerImage"]:
        raise ValueError("Image mismatch")
    if set(identity.get("variants", {})) != {"minimal-boot", "minimal", "full"}:
        raise ValueError("All three variants required")
    for variant, data in identity["variants"].items():
        if (
            data.get("variant") != variant
            or data.get("commit") != commit
            or data.get("version") != version
        ):
            raise ValueError("Mixed variant provenance")
        for kind in ["plugin", "elf", "map"]:
            if not re.fullmatch(r"[0-9a-f]{64}", data[kind]["sha256"]):
                raise ValueError("Invalid variant hash")


def checked_sums(folder):
    sums = {}
    for line in (folder / "SHA256SUMS.txt").read_text().splitlines():
        value, name = line.split("  ", 1)
        if Path(name).name != name or "\\" in name or not name.endswith(".zip") or name in sums:
            raise ValueError("Invalid or duplicate checksum filename")
        if not re.fullmatch(r"[0-9a-f]{64}", value) or sha(folder / name) != value:
            raise ValueError("Archive checksum mismatch: " + name)
        sums[name] = value
    if len(sums) != 3:
        raise ValueError("Exactly three release ZIPs required")
    return sums


def verify_commit_source(source, root, commit):
    # Never extract remote paths to the workspace.
    raw = subprocess.check_output(["git", "-C", str(root), "archive", commit])
    with tarfile.open(fileobj=io.BytesIO(raw)) as tree:
        names = set()
        for entry in tree.getmembers():
            if entry.isfile():
                names.add(entry.name)
                if source.read(entry.name) != tree.extractfile(entry).read():
                    raise ValueError("SOURCE differs from tag commit: " + entry.name)
    if set(source.namelist()) != names | {"third-party-source.zip", "BUILD.json"}:
        raise ValueError("SOURCE has missing or untracked files")


def prepare(folder, output, tag, commit, root=ROOT):
    version = (root / "VERSION").read_text().strip()
    prerelease = validate_tag(version, tag)
    if git(root, "rev-parse", "HEAD") != commit or git(root, "status", "--porcelain"):
        raise ValueError("Publish checkout must be the clean tag commit")
    sums = checked_sums(folder)
    canonical = [
        f"UniversalGameGuide-PTBR-Hardware-Test-v{version}.zip",
        f"UniversalGameGuide-Debug-Symbols-v{version}.zip",
        f"3DS-Universal-Game-Guide-SOURCE-v{version}.zip",
    ]
    inputs = []
    for name in canonical:
        matches = [n for n in sums if n == name or n == name[:-4] + "-ci-" + commit[:12] + ".zip"]
        if len(matches) != 1:
            raise ValueError("Missing or ambiguous release archive: " + name)
        inputs.append(folder / matches[0])
    with (
        zipfile.ZipFile(inputs[0]) as sd,
        zipfile.ZipFile(inputs[1]) as debug,
        zipfile.ZipFile(inputs[2]) as source,
    ):
        for archive in [sd, debug, source]:
            if archive.testzip() or len(archive.namelist()) != len(set(archive.namelist())):
                raise ValueError("Corrupt or duplicate archive entries")
        encoded = sd.read("diagnostics/BUILD.json")
        if encoded != debug.read("BUILD.json") or encoded != source.read("BUILD.json"):
            raise ValueError("Mixed installer/symbol/source BUILD.json")
        identity = json.loads(encoded)
        validate_identity(identity, version, commit)
        for variant, info in identity["variants"].items():
            for ext, kind in [("3gx", "plugin"), ("elf", "elf"), ("map", "map")]:
                name = f"default-{variant}.{ext}"
                body = debug.read(name)
                if hashlib.sha256(body).hexdigest() != info[kind]["sha256"]:
                    raise ValueError("Mixed symbols: " + name)
                if ext == "3gx" and sd.read("diagnostics/" + name) != body:
                    raise ValueError("Mixed runtime plugin: " + name)
        if sd.read("luma/plugins/default.3gx") != debug.read("default-minimal-boot.3gx"):
            raise ValueError("Installed variant mismatch")
        verify_commit_source(source, root, commit)
        if (
            hashlib.sha256(source.read("data/dependencies.lock.json")).hexdigest()
            != identity["dependencyLockSha256"]
        ):
            raise ValueError("Dependency lock identity mismatch")
        if (
            hashlib.sha256(source.read("docs/CTRPF_FILESYSTEM.patch")).hexdigest()
            != identity["frameworkPatchSha256"]
        ):
            raise ValueError("Framework patch identity mismatch")
    if output.exists():
        raise ValueError("Refusing to overwrite a prepared release directory")
    output.mkdir(parents=True)
    for src, name in zip(inputs, canonical):
        shutil.copyfile(src, output / name)
    (output / "BUILD.json").write_bytes(encoded)
    (output / "SHA256SUMS.txt").write_text(
        "".join(f"{sha(output / n)}  {n}\n" for n in canonical + ["BUILD.json"])
    )
    notes = f"""# 3DS Universal Game Guide {tag}

Build do commit **{commit}**, tag **{tag}**. Classificação: **CI-REBUILT — NEEDS HARDWARE RETEST**. Compilação/testes automatizados não demonstram aprovação física. Consulte TEST_REPORT.md do commit para resultados históricos; eles não certificam novos bytes.

TESTADOR / USUÁRIO: baixe somente **{canonical[0]}**, faça backup e extraia na raiz do SD com o console desligado. Ative Luma3DS Plugin Loader. Instala MINIMAL-BOOT primeiro, sem hotkey/UI; depois siga HARDWARE_RETEST.md para MINIMAL e FULL. START + SELECT + A abre o guia nessas duas variantes.

Não instale Debug-Symbols.zip ou SOURCE.zip no cartão SD. São destinados ao desenvolvimento/diagnóstico. Os três plugins, ELF/MAP, SOURCE e BUILD.json correspondem ao mesmo commit; use SHA256SUMS.txt para conferir os downloads e o BUILD.json para conferir símbolos por variante. Nenhum save comercial é incluído ou alterado.

Pre-release: {"YES" if prerelease else "NO"}. Evidência física das funcionalidades continua necessária antes de chamar a versão de estável. Guias piloto são parciais.
"""
    (output / "NOTES.md").write_text(notes)
    return {
        "version": version,
        "commit": commit,
        "prerelease": prerelease,
        "assets": canonical + ["BUILD.json", "SHA256SUMS.txt"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    validate_tag((ROOT / "VERSION").read_text().strip(), args.tag)
    if git(ROOT, "rev-parse", "HEAD") != args.commit:
        parser.error("Tag checkout does not match commit")
    if args.input and args.output:
        print(json.dumps(prepare(args.input, args.output, args.tag, args.commit), indent=2))
    elif args.input or args.output:
        parser.error("--input and --output must be supplied together")


if __name__ == "__main__":
    main()
