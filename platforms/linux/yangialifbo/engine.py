# ──────────────────────────────────────────────────────────────────────
# YangiAlifbo — IBus engine (Linux)
#
# Typed letters are buffered per word. When a delimiter arrives, the word
# is checked with the same rules as the Windows hook (core/convert.py).
# If it converts, the typed word is erased and the new one is committed.
#
# Privacy: typed text is kept in memory only for the current word and is
# never logged, stored or sent anywhere.
# ──────────────────────────────────────────────────────────────────────

from pathlib import Path

import gi

gi.require_version("IBus", "1.0")
from gi.repository import IBus  # noqa: E402

ENGINE_NAME = "yangialifbo"

# Same delimiter set as src/Win32/KeyboardHook.cs
DELIMITERS = set(" \t\r\n.,!?:;-\"()[]{}/\\<>=+*&|^~@#%")

# Keys that move the caret or break sequential entry: forget the buffer.
BUFFER_CLEAR_KEYSYMS = {
    IBus.KEY_Left,
    IBus.KEY_Right,
    IBus.KEY_Up,
    IBus.KEY_Down,
    IBus.KEY_Home,
    IBus.KEY_End,
    IBus.KEY_Page_Up,
    IBus.KEY_Page_Down,
    IBus.KEY_Escape,
}

# Modifiers that mean a shortcut, not text entry.
CONTROL_MASK = IBus.ModifierType.CONTROL_MASK
MOD1_MASK = IBus.ModifierType.MOD1_MASK  # Alt
SUPER_MASK = IBus.ModifierType.SUPER_MASK


from .core.convert import try_convert_word  # noqa: E402
from .core.detector import STRICT, LanguageDetector  # noqa: E402

DATA_DIR = Path(__file__).parent / "data"

_detector = None


def _get_detector():
    global _detector
    if _detector is None:
        _detector = LanguageDetector.from_data_dir(DATA_DIR)
    return _detector


def convert_word(word: str):
    """Return the converted word, or None if it must be left unchanged."""
    return try_convert_word(word, _get_detector(), mode=STRICT, chat_slang=True)


class YangiAlifboEngine(IBus.Engine):
    __gtype_name__ = "YangiAlifboEngine"

    def __init__(self):
        super().__init__()
        self._buffer = []
        self._enabled = True
        self._password_mode = False

    # ── IBus callbacks ────────────────────────────────────────────────

    def do_enable(self):
        self._buffer.clear()

    def do_disable(self):
        self._buffer.clear()

    def do_focus_out(self):
        self._buffer.clear()

    def do_reset(self):
        self._buffer.clear()

    def do_set_content_type(self, purpose, hints):
        # IBus tells us what kind of field has focus. Password fields
        # must never be converted.
        self._password_mode = purpose == IBus.InputPurpose.PASSWORD
        self._buffer.clear()

    def do_process_key_event(self, keyval, keycode, state):
        # Ignore key releases.
        if state & IBus.ModifierType.RELEASE_MASK:
            return False

        if not self._enabled or self._password_mode:
            self._buffer.clear()
            return False

        if state & (CONTROL_MASK | MOD1_MASK | SUPER_MASK):
            self._buffer.clear()
            return False

        if keyval in BUFFER_CLEAR_KEYSYMS:
            self._buffer.clear()
            return False

        if keyval == IBus.KEY_BackSpace:
            if self._buffer:
                self._buffer.pop()
            return False

        ch = IBus.keyval_to_unicode(keyval)
        if not ch:
            self._buffer.clear()
            return False

        if ch in DELIMITERS:
            self._finish_word(ch)
            return False

        self._buffer.append(ch)
        return False

    # ── Word replacement ──────────────────────────────────────────────

    def _finish_word(self, delimiter: str):
        word = "".join(self._buffer)
        self._buffer.clear()
        if not word:
            return

        converted = convert_word(word)
        if converted is None or converted == word:
            return

        # Erase the typed word, then write the converted one.
        # The delimiter itself is passed through by the caller.
        for _ in word:
            self.forward_key_event(IBus.KEY_BackSpace, 0, 0)
        self.commit_text(IBus.Text.new_from_string(converted))


def create_engine_desc() -> IBus.EngineDesc:
    return IBus.EngineDesc.new(
        ENGINE_NAME,
        "YangiAlifbo",
        "O‘zbek lotin alifbosini yangi alifbo (ş ç ö ğ) ga o‘giradi",
        "uz",
        "MIT",
        "Bilolbek Yoldoshxojayev",
        "yangialifbo",
        "us",
    )
