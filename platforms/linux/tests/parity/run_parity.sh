#!/usr/bin/env bash
# Runs the C# Core (src/Core) as an oracle and compares the Python engine with it.
# Requires: .NET 8 SDK (dotnet), Python 3 with the same package set as the engine.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../../../.." && pwd)"
PY="${PYTHON:-python3}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

mkdir -p "$WORK/core" "$WORK/data"
cp "$REPO"/src/Core/UzbekPhonetics.cs "$REPO"/src/Core/LanguageDetector.cs "$REPO"/src/Core/ChatNormalizer.cs "$WORK/core/"
cp "$REPO"/platforms/linux/yangialifbo/data/*.txt "$WORK/data/"
cp "$HERE/harness.csproj" "$HERE/Program.cs" "$WORK/"

"$PY" "$HERE/gen_words.py" "$WORK/words.txt"
(cd "$WORK" && dotnet run -c Release --project harness.csproj -- "$WORK/words.txt" "$WORK/oracle.tsv")
"$PY" "$HERE/compare.py" "$WORK/words.txt" "$WORK/oracle.tsv"
