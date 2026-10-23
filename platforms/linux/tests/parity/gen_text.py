"""Generate whole-text lines for the TextConverter parity test (deterministic)."""
import random
import sys
from pathlib import Path

LINUX = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(LINUX))
from yangialifbo.core import tables as T  # noqa: E402

DATA = LINUX / "yangialifbo" / "data"
OUT = Path(sys.argv[1])
random.seed(20261024)

lex = [l.strip() for l in open(DATA / "uzbek_words.txt", encoding="utf-8") if l.strip() and not l.startswith("#")]
rej = [l.strip() for l in open(DATA / "english_reject.txt", encoding="utf-8") if l.strip() and not l.startswith("#")]
pool = (
    [w for w in lex if "sh" in w or "ch" in w or "o'" in w or "g'" in w][:20000]
    + random.sample(lex, 2000)
    + random.sample(rej, 800)
    + ["show", "push", "chat", "Is'hoq", "mus'haf", "5-ci", "kel-chi", "bilmadm", "ucun", "lekn", "o'z-o'zidan"]
)
seps = [" ", " ", " ", ", ", ". ", "! ", "? ", ": ", "; ", " (", ") ", "\"", "/", "-", "  "]

lines = []
for _ in range(1500):
    n = random.randint(1, 9)
    out = []
    for i in range(n):
        out.append(random.choice(pool))
        if i < n - 1:
            out.append(random.choice(seps))
    text = "".join(out)
    if random.random() < 0.3:
        text = text.title()
    if random.random() < 0.2:
        text = text.upper()
    lines.append(text)
lines = [l for l in lines if "\t" not in l and "\n" not in l]
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("text lines:", len(lines))
