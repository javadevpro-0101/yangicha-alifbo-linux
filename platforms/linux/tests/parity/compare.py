"""Compare the Python engine's decisions with the C# oracle output."""
import sys
from pathlib import Path

LINUX = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(LINUX))
from yangialifbo.core.convert import try_convert_word           # noqa: E402
from yangialifbo.core.detector import AGGRESSIVE, STRICT, LanguageDetector  # noqa: E402

words_path, oracle_path = sys.argv[1], sys.argv[2]
det = LanguageDetector.from_data_dir(LINUX / "yangialifbo" / "data", user_dir="/nonexistent-yangialifbo-parity")

words = open(words_path, encoding="utf-8").read().split("\n")
if words and words[-1] == "":
    words = words[:-1]

oracle = {}
for line in open(oracle_path, encoding="utf-8"):
    w, mode, res = line.rstrip("\n").split("\t", 2)
    oracle[(w, mode)] = res

mismatches = []
checked = 0
for w in words:
    for name, mode in (("strict", STRICT), ("aggressive", AGGRESSIVE)):
        checked += 1
        py = try_convert_word(w, det, mode=mode, chat_slang=True) or ""
        ref = oracle.get((w, name), "<missing>")
        if py != ref:
            mismatches.append((w, name, ref, py))

print(f"compared {checked} decisions; mismatches: {len(mismatches)}")
for m in mismatches[:40]:
    print("  word=%r mode=%s C#=%r PY=%r" % m)
sys.exit(1 if mismatches else 0)
