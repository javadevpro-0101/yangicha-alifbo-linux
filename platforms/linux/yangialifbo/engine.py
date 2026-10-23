# ──────────────────────────────────────────────────────────────────────
# YangiAlifbo — IBus engine (Linux)
#
# Letters of the current word are held as preedit text (shown underlined
# while typing). When a delimiter arrives, the word is converted with the
# same rules as the Windows hook (core/convert.py) and committed once.
# No backspaces are sent, so the result does not depend on how fast the
# application handles synthetic key events.
#
# Privacy: typed text is kept in memory only for the current word and is
# never logged, stored or sent anywhere.
# ──────────────────────────────────────────────────────────────────────

from pathlib import Path

import gi

gi.require_version("IBus", "1.0")
from gi.repository import IBus  # noqa: E402

from .core.convert import try_convert_word  # noqa: E402
from .core.detector import STRICT, LanguageDetector  # noqa: E402

ENGINE_NAME = "yangialifbo"
DATA_DIR = Path(__file__).parent / "data"

# Same delimiter set as src/Win32/KeyboardHook.cs
DELIMITERS = set(" \t\r\n.,!?:;-\"()[]{}/\\<>=+*&|^~@#%")

# Keys that move the caret or break sequential entry.
CARET_KEYSYMS = {
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

# Delimiters that must stay key events (not committed as text).
KEY_EVENT_DELIMITERS = {IBus.KEY_Return, IBus.KEY_KP_Enter, IBus.KEY_Tab, IBus.KEY_ISO_Left_Tab}

CONTROL_MASK = IBus.ModifierType.CONTROL_MASK
MOD1_MASK = IBus.ModifierType.MOD1_MASK  # Alt
SUPER_MASK = IBus.ModifierType.SUPER_MASK
RELEASE_MASK = IBus.ModifierType.RELEASE_MASK

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

    # ── helpers ───────────────────────────────────────────────────────

    def _show_preedit(self):
        text = "".join(self._buffer)
        self.update_preedit_text(IBus.Text.new_from_string(text), len(text), bool(text))

    def _hide_preedit(self):
        self.hide_preedit_text()

    def _commit_raw_buffer(self):
        """Commit the pending letters unchanged (used when the word is interrupted)."""
        if self._buffer:
            text = "".join(self._buffer)
            self._buffer.clear()
            self._hide_preedit()
            self.commit_text(IBus.Text.new_from_string(text))

    def _take_converted(self):
        """Pop the pending word and return its converted form (or raw), or None if empty."""
        if not self._buffer:
            return None
        word = "".join(self._buffer)
        self._buffer.clear()
        converted = convert_word(word)
        self._hide_preedit()
        return converted if converted is not None else word

    # ── IBus callbacks ────────────────────────────────────────────────

    def do_enable(self):
        self._buffer.clear()

    def do_disable(self):
        self._commit_raw_buffer()

    def do_focus_out(self):
        self._commit_raw_buffer()

    def do_reset(self):
        self._buffer.clear()
        self._hide_preedit()

    def do_set_content_type(self, purpose, hints):
        # Password fields must never be converted.
        self._commit_raw_buffer()
        self._password_mode = purpose == IBus.InputPurpose.PASSWORD

    def do_process_key_event(self, keyval, keycode, state):
        if state & RELEASE_MASK:
            return False

        if not self._enabled or self._password_mode:
            self._commit_raw_buffer()
            return False

        if state & (CONTROL_MASK | MOD1_MASK | SUPER_MASK):
            self._commit_raw_buffer()
            return False

        if keyval in CARET_KEYSYMS:
            self._commit_raw_buffer()
            return False

        if keyval == IBus.KEY_BackSpace:
            if not self._buffer:
                return False
            self._buffer.pop()
            self._show_preedit()
            return True

        ch = IBus.keyval_to_unicode(keyval)
        if not ch:
            self._commit_raw_buffer()
            return False

        if ch in DELIMITERS:
            out = self._take_converted()
            if out is None:
                return False
            if keyval in KEY_EVENT_DELIMITERS:
                # Enter / Tab stay real key events: commit the word, then let the key through.
                self.commit_text(IBus.Text.new_from_string(out))
                return False
            # Printable delimiter: commit word and delimiter together, in order.
            self.commit_text(IBus.Text.new_from_string(out + ch))
            return True

        self._buffer.append(ch)
        self._show_preedit()
        return True  # consumed: shown as preedit until the word ends


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
