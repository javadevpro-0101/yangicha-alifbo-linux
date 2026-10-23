"""yangialifbo-convert: convert the selected text in any application.

Works in apps where the IBus engine does not (for example Telegram Desktop).
Bind this command to a shortcut in your desktop settings (for example
Ctrl+Alt+U). Flow:

  1. Read the selected text (X11 PRIMARY selection).
  2. Convert it with the same rules as the keyboard engine.
  3. Put the result on the clipboard, paste it over the selection (Ctrl+V),
     and restore the previous clipboard contents.

Needs X11, xclip and xdotool. Optional: notify-send for messages.
Privacy: the text is only handled in memory on this machine.
"""

import shutil
import subprocess
import sys
import time
from pathlib import Path

from .core.detector import STRICT, LanguageDetector
from .core.text import convert_text

DATA_DIR = Path(__file__).parent / "data"
PASTE_DELAY = 0.15
RESTORE_DELAY = 0.6


def _run(args, input_bytes=None):
    return subprocess.run(
        args,
        input=input_bytes,
        stdout=subprocess.PIPE if input_bytes is None else subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=5,
        check=False,
    )


def read_selection(name):
    """Return text of the X selection `name` (primary/clipboard), or '' if empty."""
    res = _run(["xclip", "-o", "-selection", name])
    if res.returncode != 0:
        return ""
    return res.stdout.decode("utf-8", errors="replace")


def write_clipboard(text):
    # xclip forks to serve the selection; DEVNULL keeps subprocess from waiting on it.
    subprocess.run(
        ["xclip", "-selection", "clipboard"],
        input=text.encode("utf-8"),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=5,
        check=False,
    )


def notify(message):
    if shutil.which("notify-send"):
        _run(["notify-send", "YangiAlifbo", message])
    else:
        print(message, file=sys.stderr)


def main():
    for tool in ("xclip", "xdotool"):
        if shutil.which(tool) is None:
            notify(f"{tool} o'rnatilmagan. sudo apt install {tool}")
            return 1

    selected = read_selection("primary")
    if not selected.strip():
        notify("Avval matnni belgilang, keyin tugmani bosing.")
        return 0

    detector = LanguageDetector.from_data_dir(DATA_DIR)
    converted = convert_text(selected, detector, mode=STRICT, slang=True)
    if converted == selected:
        notify("O‘zgartiriladigan so‘z topilmadi.")
        return 0

    previous = read_selection("clipboard")
    write_clipboard(converted)
    time.sleep(PASTE_DELAY)
    _run(["xdotool", "key", "--clearmodifiers", "ctrl+v"])
    time.sleep(RESTORE_DELAY)
    if previous:
        write_clipboard(previous)
    return 0


if __name__ == "__main__":
    sys.exit(main())
