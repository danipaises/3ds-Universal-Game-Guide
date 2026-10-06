#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
ugg_force_rebuild=0
if [[ "${1:-}" == "--clean" && $# == 1 ]]; then
  ugg_force_rebuild=1
elif [[ $# != 0 ]]; then
  echo "Usage: bash scripts/build-plugin.sh [--clean]" >&2
  exit 2
fi
python3 scripts/fetch_deps.py
python3 scripts/prepare_framework.py
if [[ "$ugg_force_rebuild" == 1 ]]; then
  python3 - <<'PY'
import shutil
from pathlib import Path
root = Path.cwd().resolve()
library = Path('.deps/ctrpluginframework-0.8.0/Library')
targets = [library / part for part in [
    'release', 'debug', 'lib', 'libcwav/build', 'libcwav/lib',
    'libcwav/libncsnd/build', 'libcwav/libncsnd/lib',
]] + [Path('plugin/build'), Path('plugin/build-minimal'), Path('plugin/build-minimal-boot')]
for target in targets:
    if target.is_symlink() or not target.resolve().is_relative_to(root):
        raise ValueError('build cache escapes project')
    if target.exists():
        shutil.rmtree(target)
Path('plugin/default.elf').unlink(missing_ok=True)
Path('plugin/default-minimal.elf').unlink(missing_ok=True)
Path('plugin/default.map').unlink(missing_ok=True)
Path('plugin/default-minimal.map').unlink(missing_ok=True)
Path('plugin/default-minimal-boot.elf').unlink(missing_ok=True)
Path('plugin/default-minimal-boot.map').unlink(missing_ok=True)
PY
fi
# Converter is a host utility. Bundle C++ runtime to support devkitPro image ABI.
cmake -S .deps/yaml-cpp-0.8.0 -B .deps/yaml-build -DCMAKE_POLICY_VERSION_MINIMUM=3.5 -DYAML_CPP_BUILD_TESTS=OFF -DYAML_CPP_BUILD_TOOLS=OFF -DCMAKE_CXX_FLAGS='-include cstdint' -DCMAKE_BUILD_TYPE=Release
cmake --build .deps/yaml-build --parallel 2
g++ -std=c++17 -include cstdint -static-libstdc++ -static-libgcc \
  -I.deps/3gxtool-current/includes -I.deps/yaml-cpp-0.8.0/include \
  -I.deps/yaml-cpp-0.8.0/include/yaml-cpp -I.deps/dynalo/include/dynalo \
  .deps/3gxtool-current/sources/*.cpp .deps/yaml-build/libyaml-cpp.a -ldl \
  -o .deps/3gxtool-current/3gxtool
mkdir -p build
image="$(python3 -c 'import json; print(json.load(open("data/dependencies.lock.json"))["dockerImage"])')"
docker run --rm --network none --user "$(id -u):$(id -g)" -v "$PWD:/work" -w /work "$image" \
  bash -c 'set -e; export PATH="$DEVKITARM/bin:$PATH"; make -C .deps/ctrpluginframework-0.8.0/Library lib/libctrpf.a -j2 G=-g ENABLE_LINK_TIME_OPTIMIZATIONS=0 CTRPF_VERSION_MAJOR=0 CTRPF_VERSION_MINOR=8 CTRPF_VERSION_BUILD=0 COMMIT=a502818c CTRPF_REVISION=0.8.0 COMPILE_DATE=2026-10-04T00:00:00UTC; make -C plugin default.elf default-minimal.elf default-minimal-boot.elf -j2; arm-none-eabi-readelf -S plugin/default.elf > plugin/default.sections.txt; arm-none-eabi-readelf -S plugin/default-minimal.elf > plugin/default-minimal.sections.txt; arm-none-eabi-readelf -S plugin/default-minimal-boot.elf > plugin/default-minimal-boot.sections.txt; arm-none-eabi-size plugin/default.elf plugin/default-minimal.elf plugin/default-minimal-boot.elf; arm-none-eabi-g++ --version > build/arm-compiler-version.txt; dkp-pacman -Q devkitARM libctru > build/arm-package-versions.txt'
.deps/3gxtool-current/3gxtool -s plugin/default.elf plugin/plugin.plgInfo plugin/default.3gx
python3 - <<'PY'
from pathlib import Path
s = Path('plugin/plugin.plgInfo').read_text().replace('Title: 3DS Universal Game Guide', 'Title: UGG MINIMAL Hardware Retest')
Path('build/minimal.plgInfo').parent.mkdir(exist_ok=True)
Path('build/minimal.plgInfo').write_text(s)
Path('build/minimal-boot.plgInfo').write_text(s.replace('UGG MINIMAL Hardware Retest', 'UGG MINIMAL-BOOT Heap Probe'))
PY
.deps/3gxtool-current/3gxtool -s plugin/default-minimal.elf build/minimal.plgInfo plugin/default-minimal.3gx
.deps/3gxtool-current/3gxtool -s plugin/default-minimal-boot.elf build/minimal-boot.plgInfo plugin/default-minimal-boot.3gx
cp plugin/default.3gx plugin/default-full.3gx
cp plugin/default.elf plugin/default-full.elf
cp plugin/default.map plugin/default-full.map
python3 -c 'from pathlib import Path; p=Path("plugin/default.3gx"); assert p.read_bytes()[:8]==b"3GX$0002"; print("3GX v2 produced:",p.stat().st_size,"bytes")'

python3 - <<'PYTOOLCHAIN'
import json
from pathlib import Path
lock = json.loads(Path('data/dependencies.lock.json').read_text())
Path('build/toolchain.json').write_text(json.dumps({
    'dockerImage': lock['dockerImage'],
    'compiler': Path('build/arm-compiler-version.txt').read_text().splitlines()[0],
    'packages': Path('build/arm-package-versions.txt').read_text().splitlines(),
}, indent=2) + '\n')
PYTOOLCHAIN
