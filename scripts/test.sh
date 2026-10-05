#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python="${UGG_PYTHON:-python3}"
cxx="${CXX:-g++}"
mkdir -p build
"$python" tools/guide-builder/builder.py build > build/validation.json
"$python" -m unittest discover -s tests -v
"$cxx" --version
"$cxx" -std=c++20 -Wall -Wextra -Werror -g -O1 -fsanitize=address,undefined -fno-omit-frame-pointer -Iplugin/include plugin/source/core.cpp tests/core_test.cpp -o build/core-test
ASAN_OPTIONS="detect_leaks=${UGG_LSAN:-1}" build/core-test "$PWD/build/sd/3ds/UniversalGameGuide"
"$cxx" -std=c++20 -Wall -Wextra -Werror -g -O1 -fsanitize=address,undefined -fno-omit-frame-pointer -Itests/native_stubs -Iplugin/include plugin/source/boot.cpp tests/boot_test.cpp -o build/boot-test
for ugg_boot_scenario in normal fs-fail io-fail; do
  ASAN_OPTIONS="detect_leaks=${UGG_LSAN:-1}" build/boot-test "$ugg_boot_scenario"
done
