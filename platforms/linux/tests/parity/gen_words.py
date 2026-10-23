"""Generate the word list used for parity tests (deterministic, seed 20261023)."""
import random
import sys
from pathlib import Path

LINUX = Path(__file__).resolve().parents[2]          # platforms/linux
sys.path.insert(0, str(LINUX))
from yangialifbo.core import tables as T              # noqa: E402

DATA = LINUX / "yangialifbo" / "data"
OUT = Path(sys.argv[1])

random.seed(20261023)
lex = [l.strip() for l in open(DATA / "uzbek_words.txt", encoding="utf-8") if l.strip() and not l.startswith("#")]
rej = [l.strip() for l in open(DATA / "english_reject.txt", encoding="utf-8") if l.strip() and not l.startswith("#")]
suf = list(T.UZBEK_SUFFIXES)
apos = ["'", "‘", "’", "ʻ", "ʼ", "`", "´", "‛", "′"]
words = set()
words.update(random.sample(lex, 4000))
words.update(random.sample(rej, 2000))
for w in random.sample(lex, 3000):
    words.add(w + random.choice(suf))
    if random.random() < 0.5:
        words.add(w + random.choice(suf) + random.choice(suf))
for w in random.sample([x for x in lex if "o'" in x or "g'" in x or "sh" in x or "ch" in x] or lex, 800):
    for a in random.sample(apos, 3):
        words.add(w.replace("'", a))
    words.add(w.title())
    words.add(w.upper())
words.update(["5-ci", "5-chi", "1-orin", "10-gacha", "12-inchi", "kel-chi", "ayt-chi", "o'z-o'zidan", "ko'r-chi",
              "2-chi", "3-lik", "7-talab", "pc-chi", "shahar-chi", "1-o'rin", "20-ci", "5-c", "100-tacha"])
words.update([
    "wu", "wunaqa", "wunday", "wuncha", "owa", "uwa", "awqam", "ucun", "qacon", "hec", "qanca", "necu",
    "osha", "bopti", "bomasam", "bosa", "bovotti", "bovottim", "lekn", "blan", "bln", "nma", "nmaga", "nmadur",
    "nmadir", "qalesz", "qattansz", "yaxwmsz", "bilmadm", "kirasz", "tuwri", "bowlan", "yow", "iwi", "iwim",
    "iwing", "quwiladi", "tawavor", "yaxw", "tuw", "bowq", "amz", "asz", "misz", "dm", "dk", "adm", "idk",
    "bolamiz", "bolasz", "bolmadm", "kormadm", "ozim", "orgatyapman", "organdim", "ortog", "otgan",
    "tolamiz", "jonatdim", "qoshdim", "orindim", "oylagan", "ochirdim", "sorandim", "sozladim", "yolga",
    "kopdi", "togrisi", "zorman", "hop", "xop", "yoq", "yoqmi", "yoqligi", "yoqku", "sora", "soram", "soz",
    "Kop", "KOP", "Bol", "BOL", "Osha", "OSHA", "Ucun", "UCUN", "Lekn", "Tuwri", "Quwiladi"])
words.update(["Is'hoq", "mus'haf", "as'hob", "mas'ul", "Is’hoq", "mus`haf", "o'rtoq", "g'alaba", "Ko'p",
              "KO'P", "shahar", "Shahar", "SHAHAR", "show", "shu", "chat", "push", "chiroy", "choy", "to'g'ri",
              "g'", "o'", "a", "shu-shu", "kitob.", "salom!", "qo'llanma", "xo'jayin", "bo'lsa", "bo'lmasam"])
alpha = "abcdefghiklmnoprstuvxyzg'"
for _ in range(1500):
    n = random.randint(2, 9)
    w = "".join(random.choice(alpha) for _ in range(n))
    if random.random() < 0.5:
        i = random.randint(0, n - 1)
        w = w[:i] + random.choice(["sh", "ch", "o'", "g'"]) + w[i + 1:]
    words.add(w)
words = sorted(w for w in words if "\t" not in w and "\n" not in w)
OUT.write_text("\n".join(words) + "\n", encoding="utf-8")
print("words:", len(words))
