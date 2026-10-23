"""Port of src/Core/TextConverter.cs: convert a whole text, word by word.

Used by the selection converter (yangialifbo-convert). Note the rules differ
slightly from the keyboard path (convert.try_convert_word), as in the C# code.
"""

import re

from . import chat
from . import phonetics as P
from .detector import AGGRESSIVE, STRICT

# Same delimiters as KeyboardHook, except '-' which joins compounds.
_TOKENS = re.compile(r"(\s+|[.,!?:;\"()\[\]{}/\\])")


def _convert_token(token, detector, mode, slang):
    if len(token) < 2 or not (token[0].isalpha() or token[0].isdigit()):
        return token

    if detector.is_foreign_or_reject(token):
        return token

    work = chat.normalize(token) if slang else token

    if P.has_convertible_patterns(work):
        if mode == AGGRESSIVE or detector.is_uzbek(work):
            return P.convert(work)
    elif work != token and detector.is_uzbek(work):
        return work

    return token


def convert_text(text, detector, mode=STRICT, slang=True):
    """Return the converted text. Whitespace and punctuation are kept as they are."""
    if not text:
        return text
    parts = []
    for token in _TOKENS.split(text):
        if not token:
            continue
        parts.append(_convert_token(token, detector, mode, slang))
    return "".join(parts)
