"""Port of src/Core/LanguageDetector.cs.

3-tier Uzbek / foreign discrimination:
  Tier 1: English / tech reject list
  Tier 2: Uzbek lexicon exact match (1995 and 2024 spellings)
  Tier 3: Uzbek morphological affix stripping
Plus user whitelist / blacklist files.

Privacy: nothing typed is written anywhere. Only the user's own word lists
are read and (when they edit them through the app) written.
"""

import os
from pathlib import Path

from . import phonetics as P
from . import tables as T

STRICT = "strict"
AGGRESSIVE = "aggressive"


def user_config_dir() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(Path.home(), ".config")
    return Path(base) / "yangialifbo"


def normalize_for_lookup(word: str) -> str:
    return P.normalize_apostrophes(word).lower()


def _load_word_list(path: Path) -> set:
    words = set()
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            t = line.strip()
            if t and not t.startswith("#"):
                words.add(t.lower())
    return words


def _load_user_file(path: Path) -> set:
    if not path.exists():
        return set()
    words = set()
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                t = line.strip()
                if t and not t.startswith("#") and not t.startswith(";"):
                    words.add(normalize_for_lookup(t))
    except OSError:
        return set()
    return words


def _is_all_digits(s: str) -> bool:
    return bool(s) and all(c.isdigit() for c in s)


class LanguageDetector:
    def __init__(self, english_reject, uzbek_lexicon, whitelist=None, blacklist=None, user_dir=None):
        self._english_reject = set(x.lower() for x in english_reject)
        self._uzbek_lexicon = set(x.lower() for x in uzbek_lexicon)
        self._user_dir = Path(user_dir) if user_dir else user_config_dir()
        self._whitelist = set(whitelist or ())
        self._blacklist = set(blacklist or ())
        self._cache = {}

    @classmethod
    def from_data_dir(cls, data_dir, user_dir=None):
        data_dir = Path(data_dir)
        det = cls(
            _load_word_list(data_dir / "english_reject.txt"),
            _load_word_list(data_dir / "uzbek_words.txt"),
            user_dir=user_dir,
        )
        det.reload_user_lists()
        return det

    # ── Public API ────────────────────────────────────────────────────

    @property
    def whitelist_path(self) -> Path:
        return self._user_dir / "user_whitelist.txt"

    @property
    def blacklist_path(self) -> Path:
        return self._user_dir / "user_blacklist.txt"

    def reload_user_lists(self):
        self._whitelist = _load_user_file(self.whitelist_path)
        self._blacklist = _load_user_file(self.blacklist_path)
        self._cache.clear()

    def should_convert(self, word: str, mode=STRICT) -> bool:
        if not word or not word.strip() or len(word) < 2:
            return False
        if not P.has_convertible_patterns(word):
            return False

        normalized = normalize_for_lookup(word)
        if normalized in self._blacklist:
            return False
        if normalized in self._whitelist:
            return True
        if mode == AGGRESSIVE:
            return True
        return self.is_uzbek(word)

    def is_uzbek(self, word: str, mode=STRICT) -> bool:
        if not word or not word.strip() or len(word) < 2:
            return False

        normalized = normalize_for_lookup(word)
        if mode == STRICT and normalized in self._cache:
            return self._cache[normalized]

        result = self._compute_is_uzbek(normalized, mode)

        if mode == STRICT and len(self._cache) < 10000:
            self._cache[normalized] = result
        return result

    def is_foreign_or_reject(self, word: str) -> bool:
        if not word or not word.strip():
            return False

        normalized = normalize_for_lookup(word)
        if normalized in self._blacklist:
            return True
        if normalized in self._whitelist:
            return False

        hyphen = normalized.find("-")
        if hyphen > 0:
            part1 = normalized[:hyphen]
            part2 = normalized[hyphen + 1:]
            if _is_all_digits(part1):
                if part2 in T.ORDINAL_SUFFIXES:
                    return False
                return part2 in self._english_reject

            if part2 == "chi":
                return part1 in self._english_reject

            if part1 in self._english_reject or part2 in self._english_reject:
                return True

        return normalized in self._english_reject

    # ── Core decision (mirrors ComputeIsUzbek) ────────────────────────

    def _compute_is_uzbek(self, normalized: str, mode) -> bool:
        if normalized in self._blacklist:
            return False
        if normalized in self._whitelist:
            return True
        if mode == AGGRESSIVE:
            return True

        if normalized in self._english_reject:
            return False

        hyphen = normalized.find("-")
        if hyphen > 0:
            if _is_all_digits(normalized[:hyphen]):
                suffix = normalized[hyphen + 1:]
                if suffix in T.ORDINAL_SUFFIXES:
                    return True
                if self._compute_is_uzbek(suffix, mode):
                    return True
            else:
                if normalized.endswith("-chi"):
                    stem = normalized[:-4]
                    if len(stem) >= 2 and self._compute_is_uzbek(stem, mode):
                        return True

                part1 = normalized[:hyphen]
                part2 = normalized[hyphen + 1:]
                if part1 not in self._english_reject and part2 not in self._english_reject:
                    if self._compute_is_uzbek(part1, mode) or self._compute_is_uzbek(part2, mode):
                        return True

        if normalized in self._uzbek_lexicon:
            return True

        converted = P.convert(normalized)
        if converted != normalized and converted in self._uzbek_lexicon:
            return True

        if self._try_morphological_match(normalized):
            return True
        if converted != normalized and self._try_morphological_match(converted):
            return True

        return False

    # ── Tier 3: morphology ────────────────────────────────────────────

    def _try_morphological_match(self, word: str) -> bool:
        for suffix in T.UZBEK_SUFFIXES:
            if len(word) > len(suffix) + 1 and word.endswith(suffix):
                stem = word[: -len(suffix)]
                if self._check_stem(stem):
                    return True

                for suffix2 in T.CHAINABLE_INNER_SUFFIXES:
                    if len(stem) > len(suffix2) + 1 and stem.endswith(suffix2):
                        stem2 = stem[: -len(suffix2)]
                        if self._check_stem(stem2):
                            return True

                        for suffix3 in T.CHAINABLE_INNER_SUFFIXES:
                            if len(stem2) > len(suffix3) + 1 and stem2.endswith(suffix3):
                                stem3 = stem2[: -len(suffix3)]
                                if self._check_stem(stem3):
                                    return True
        return False

    def _lex_or_converted(self, form: str) -> bool:
        """True if form, or its 2024 conversion, is in the lexicon."""
        if form in self._uzbek_lexicon:
            return True
        conv = P.convert(form)
        return conv != form and conv in self._uzbek_lexicon

    def _check_stem(self, stem: str) -> bool:
        if len(stem) < 2:
            return False

        # 1. Direct match, either spelling.
        if self._lex_or_converted(stem):
            return True

        # 2. Verb infinitive (stem + "moq").
        verb = stem + "moq"
        if self._lex_or_converted(verb):
            return True

        # 3. Consonant alternation: g' -> q  (o'rtog' -> o'rtoq)
        if stem.endswith("'") and len(stem) > 2:
            if stem.endswith("g'"):
                q_stem = stem[:-2] + "q"
                if self._lex_or_converted(q_stem):
                    return True
        elif (stem.endswith("ğ") or stem.endswith("Ğ")) and len(stem) > 2:
            q_stem = stem[:-1] + "q"
            if self._lex_or_converted(q_stem):
                return True

        # 4. Consonant alternation: g -> k  (yurag -> yurak)
        if stem.endswith("g") and len(stem) > 2:
            k_stem = stem[:-1] + "k"
            if self._lex_or_converted(k_stem):
                return True

        # 5. Voice derivations
        if stem.endswith("n") and len(stem) > 2:
            if self._base_matches(stem[:-1]):
                return True

        if stem.endswith("il") and len(stem) > 3:
            if self._base_matches(stem[:-2]):
                return True

        if stem.endswith("t") and len(stem) > 2:
            if self._base_matches(stem[:-1]):
                return True

        if len(stem) > 4 and (stem.endswith("tir") or stem.endswith("dir")):
            if self._base_matches(stem[:-3]):
                return True

        return False

    def _base_matches(self, base: str) -> bool:
        if base in self._uzbek_lexicon or (base + "moq") in self._uzbek_lexicon:
            return True
        conv = P.convert(base)
        return conv in self._uzbek_lexicon or (conv + "moq") in self._uzbek_lexicon
