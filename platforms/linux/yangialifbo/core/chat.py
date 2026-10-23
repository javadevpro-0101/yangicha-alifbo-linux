"""Port of src/Core/ChatNormalizer.cs: informal / chat Uzbek -> standard spelling."""

from . import tables as T

_ROOT_TABLES = {
    "bol": T.CN_BOL_SUFFIXES,
    "kor": T.CN_KOR_SUFFIXES,
    "oz": T.CN_OZ_SUFFIXES,
    "kop": T.CN_KOP_SUFFIXES,
    "soz": T.CN_SOZ_SUFFIXES,
    "yol": T.CN_YOL_SUFFIXES,
    "ort": T.CN_ORT_SUFFIXES,
    "ochir": T.CN_OCHIR_SUFFIXES,
    "oyla": T.CN_OYLA_SUFFIXES,
    "jonat": T.CN_JONAT_SUFFIXES,
    "qosh": T.CN_QOSH_SUFFIXES,
    "orin": T.CN_ORIN_SUFFIXES,
    "tol": T.CN_TOL_SUFFIXES,
    "ot": T.CN_OT_SUFFIXES,
}

_WUNI_PREFIXES = (
    "wunaqa", "wunaqangi", "wuni", "wunga", "wunday",
    "wunde", "wuncha", "wunda", "wuning", "wunisi",
)


def _expand_unaccented_roots_fast(norm: str) -> str:
    # Root: sora- -> so'ra- (checked before soz/so'z roots, as in the C# source)
    if norm.startswith("sora") and norm[4:] in T.CN_SORA_SUFFIXES:
        return "so'ra" + norm[4:]

    # Root with a fixed stem length (bol-, kor-, ...), in the same order as the C# file.
    for root, accented in (
        ("bol", "bo'l"),
        ("kor", "ko'r"),
        ("oz", "o'z"),
    ):
        if norm.startswith(root) and norm[len(root):] in _ROOT_TABLES[root]:
            return accented + norm[len(root):]

    if norm == "togri" or norm.startswith("togri"):
        return "to'g'ri" + norm[5:]
    if norm == "zor" or norm.startswith("zor"):
        return "zo'r" + norm[3:]
    if norm in ("hop", "xop"):
        return "xo'p"
    if norm in ("yoq", "yoqmi", "yoqligi", "yoqku"):
        return "yo'q" + norm[3:]

    for root, accented in (
        ("kop", "ko'p"),
        ("soz", "so'z"),
        ("yol", "yo'l"),
        ("ort", "o'rt"),
        ("ochir", "o'chir"),
        ("oyla", "o'yla"),
        ("jonat", "jo'nat"),
        ("qosh", "qo'sh"),
        ("orin", "o'rin"),
        ("tol", "to'l"),
        ("ot", "o't"),
    ):
        if norm.startswith(root) and norm[len(root):] in _ROOT_TABLES[root]:
            return accented + norm[len(root):]

    if norm.startswith("orgat"):
        return "o'rgat" + norm[5:]
    if norm.startswith("organ"):
        return "o'rgan" + norm[5:]

    return norm


def match_casing(original: str, transformed: str) -> str:
    if not transformed:
        return transformed

    all_upper = True
    for c in original:
        if c.isalpha() and not c.isupper():
            all_upper = False
            break

    if all_upper:
        return transformed.upper()
    if original[:1].isupper():
        return transformed[0].upper() + transformed[1:]
    return transformed.lower()


def normalize(word: str) -> str:
    if not word or word.strip() == "" or len(word) < 2:
        return word

    lower = word.lower()
    norm = lower

    # 0. Hyphenated numbers: 5-ci -> 5-chi, 1-orin -> 1-o'rin
    hyphen = norm.find("-")
    if hyphen > 0 and all(c.isdigit() for c in norm[:hyphen]):
        prefix = norm[: hyphen + 1]
        suffix = norm[hyphen + 1:]
        if suffix in ("ci", "c"):
            norm = prefix + "chi"
        else:
            norm_suffix = normalize(suffix)
            if norm_suffix != suffix:
                norm = prefix + norm_suffix

    # 1. Russian keyboard 'w' substitutions
    if norm == "wu":
        norm = "shu"
    elif norm.startswith(_WUNI_PREFIXES):
        norm = "sh" + norm[1:]
    elif norm.startswith("owa") or norm.startswith("uwa"):
        norm = "o'sha" + norm[3:]
    elif norm == "awqam":
        norm = "oqshom"
    else:
        if "yaxw" in norm:
            norm = norm.replace("yaxw", "yaxsh")
        if "tuw" in norm:
            norm = norm.replace("tuw", "tush")
        if "bowq" in norm:
            norm = norm.replace("bowq", "boshq")
        if "bowlan" in norm:
            norm = norm.replace("bowlan", "boshlan")
        if "yow" in norm:
            norm = norm.replace("yow", "yosh")
        if norm.endswith("iwi") and len(norm) >= 5:
            norm = norm[:-3] + "ishi"
        if norm in ("iwim", "iwing", "iwi"):
            norm = norm.replace("w", "sh")
        if norm == "quwiladi":
            norm = "qo'shiladi"
        if "tawavor" in norm:
            norm = norm.replace("tawavor", "tashavor")

    # 2. 'c' for 'ch' in high-frequency chat abbreviations
    if norm == "ucun":
        norm = "uchun"
    elif norm == "qacon":
        norm = "qachon"
    elif norm == "hec":
        norm = "hech"
    elif norm == "qanca":
        norm = "qancha"
    elif norm == "necu":
        norm = "nechun"

    # 3. Dialectal & spoken stems
    if norm.startswith("osha"):
        norm = "o'sha" + norm[4:]
    elif norm.startswith("bopti"):
        norm = "bo'pti" + norm[5:]
    elif norm in ("bomasam", "bomasa", "bomasin"):
        norm = "bo'lmasam"
    elif norm == "bosa":
        norm = "bo'lsa"
    elif norm.startswith("bovot"):
        norm = "bo'vott" + norm[6:]
    elif norm == "bovotti":
        norm = "bo'votti"
    elif norm == "lekn":
        norm = "lekin"
    elif norm in ("blan", "bln"):
        norm = "bilan"
    elif norm == "nma":
        norm = "nima"
    elif norm == "nmaga":
        norm = "nimaga"
    elif norm in ("nmadur", "nmadir"):
        norm = "nimadir"
    elif norm == "qalesz":
        norm = "qaleysiz"
    elif norm.startswith("qattansz"):
        norm = "qattansiz"
    elif norm == "yaxwmsz":
        norm = "yaxshimisiz"
    # "qanaqangisi" and "aytvor" branches in the C# source are no-ops.

    # 4. Suffix contractions
    if norm.endswith("amz") and len(norm) >= 5:
        norm = norm[:-3] + "amiz"
    elif norm.endswith("asz") and len(norm) >= 5:
        norm = norm[:-3] + "asiz"
    elif norm.endswith("misz") and len(norm) >= 6:
        norm = norm[:-4] + "misiz"
    elif norm.endswith("dm") and len(norm) >= 3 and norm != "adm":
        norm = norm[:-2] + "dim"
    elif norm.endswith("dk") and len(norm) >= 4 and norm != "idk":
        norm = norm[:-2] + "dik"

    # 5. Unaccented 'o' expansion
    norm = _expand_unaccented_roots_fast(norm)

    if norm == lower:
        return word
    return match_casing(word, norm)
