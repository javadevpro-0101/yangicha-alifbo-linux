"""Port of src/Core/UzbekPhonetics.cs.

1995 Uzbek Latin -> 2024 reformed Latin:  sh->ş  ch->ç  o'->ö  g'->ğ
"""

# All 9 characters recognized as apostrophe / tutuq belgisi variants.
APOSTROPHE_VARIANTS = frozenset([
    "'",       # U+0027
    "‘",  # U+2018
    "’",  # U+2019
    "ʻ",  # U+02BB  modifier letter turned comma (1995 Uzbek)
    "ʼ",  # U+02BC  modifier letter apostrophe (tutuq belgisi)
    "`",       # U+0060
    "´",  # U+00B4
    "‛",  # U+201B
    "′",  # U+2032
])

_APOSTROPHE_TABLE = {ord(c): "'" for c in APOSTROPHE_VARIANTS}


def normalize_apostrophes(text: str) -> str:
    if not text:
        return text
    return text.translate(_APOSTROPHE_TABLE)


def _protected_positions(chars):
    """Mark s'h and c'h positions so they are never converted."""
    protected = set()
    for i in range(len(chars) - 2):
        lo = chars[i].lower()
        mid = chars[i + 1]
        nxt = chars[i + 2].lower()
        if (lo == "s" or lo == "c") and mid == "'" and nxt == "h":
            protected.update((i, i + 1, i + 2))
    return protected


def has_convertible_patterns(word: str) -> bool:
    if not word or len(word) < 2:
        return False

    normalized = normalize_apostrophes(word)
    protected = _protected_positions(normalized)

    for i in range(len(normalized) - 1):
        if i in protected or (i + 1) in protected:
            continue
        lo = normalized[i].lower()
        nxt = normalized[i + 1]
        loNext = nxt.lower()

        if (lo == "s" or lo == "c") and loNext == "h":
            return True
        if (lo == "o" or lo == "g") and nxt == "'":
            return True
    return False


has_convertible_sequences = has_convertible_patterns


def convert(word: str) -> str:
    """Convert 1995 Uzbek Latin spelling to the 2024 reformed alphabet, preserving case."""
    if not word:
        return word

    chars = list(normalize_apostrophes(word))
    protected = _protected_positions(chars)
    upper = [c.isupper() for c in chars]

    result = []
    idx = 0
    n = len(chars)
    while idx < n:
        if idx in protected:
            result.append(chars[idx])
            idx += 1
            continue

        if idx + 1 < n and (idx + 1) not in protected:
            lo = chars[idx].lower()
            nxt = chars[idx + 1]
            loNext = nxt.lower()
            is_upper = upper[idx]

            if lo == "s" and loNext == "h":
                result.append("Ş" if is_upper else "ş")
                idx += 2
                continue
            if lo == "c" and loNext == "h":
                result.append("Ç" if is_upper else "ç")
                idx += 2
                continue
            if lo == "o" and nxt == "'":
                result.append("Ö" if is_upper else "ö")
                idx += 2
                continue
            if lo == "g" and nxt == "'":
                result.append("Ğ" if is_upper else "ğ")
                idx += 2
                continue

        result.append(chars[idx])
        idx += 1

    return "".join(result)
