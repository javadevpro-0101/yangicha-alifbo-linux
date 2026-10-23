"""Compare yangialifbo.core.text.convert_text with the C# TextConverter output."""
import sys
from pathlib import Path

LINUX = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(LINUX))
from yangialifbo.core.detector import AGGRESSIVE, STRICT, LanguageDetector  # noqa: E402
from yangialifbo.core.text import convert_text  # noqa: E402

lines_path, oracle_path = sys.argv[1], sys.argv[2]
det = LanguageDetector.from_data_dir(LINUX / "yangialifbo" / "data", user_dir="/nonexistent-yangialifbo-parity")

lines = open(lines_path, encoding="utf-8").read().split("\n")
if lines and lines[-1] == "":
    lines = lines[:-1]

oracle = {}
for row in open(oracle_path, encoding="utf-8"):
    src, mode, res = row.rstrip("\n").split("\t", 2)
    oracle[(src, mode)] = res

mismatches = []
checked = 0
for line in lines:
    for name, mode in (("strict", STRICT), ("aggressive", AGGRESSIVE)):
        checked += 1
        py = convert_text(line, det, mode=mode, slang=True)
        ref = oracle.get((line, name), "<missing>")
        if py != ref:
            mismatches.append((line, name, ref, py))

print(f"text compared {checked}; mismatches: {len(mismatches)}")
for m in mismatches[:20]:
    print("  line=%r mode=%s C#=%r PY=%r" % m)
sys.exit(1 if mismatches else 0)
