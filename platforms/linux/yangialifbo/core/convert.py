"""Word-level conversion decision, mirroring KeyboardHook.TryConvertWord (src/Win32/KeyboardHook.cs).

Returns the replacement word, or None when the word must be left alone.
"""

from . import chat
from . import phonetics as P
from .detector import AGGRESSIVE, STRICT


def try_convert_word(word, detector, mode=STRICT, chat_slang=True):
    if not word or not word.strip() or len(word) < 2:
        return None

    # Tier 1: absolute protection for English and foreign words.
    if detector.is_foreign_or_reject(word):
        return None

    work = chat.normalize(word) if chat_slang else word

    if not P.has_convertible_patterns(work):
        # The chat normalizer may have expanded the word (bilmadm -> bilmadim).
        if work != word and detector.is_uzbek(work):
            return work
        return None

    if mode == AGGRESSIVE:
        return P.convert(work)

    if detector.is_uzbek(work):
        return P.convert(work)

    return None
