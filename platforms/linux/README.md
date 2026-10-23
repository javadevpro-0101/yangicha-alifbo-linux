# YangiAlifbo for Linux (IBus)

Status: **early but working**. Conversion rules match the Windows code
(parity test). The IBus engine has been tested with real keystrokes in a
virtual X display: normal text fields convert, password fields do not.

## Layout

- `yangialifbo/engine.py` — IBus engine: buffers letters per word, skips
  password fields (IBus input purpose), converts on delimiters.
- `yangialifbo/core/` — Python port of `src/Core/` (phonetics, chat
  normalizer, language detector, word decision).
- `yangialifbo/data/` — word lists (copied from `src/Core/Dictionaries/`).
- `data/yangialifbo.xml` — IBus component file.
- `packaging/deb/` — builds `yangialifbo_<version>_all.deb` (`build_deb.sh`).
- `tests/live/` — live IBus test: types into a real GTK3 field through IBus.
- `tests/parity/` — compares the Python port with the C# code (the oracle).

## Parity test

    platforms/linux/tests/parity/run_parity.sh

Needs the .NET 8 SDK. Runs about 30 000 decisions in both implementations
and fails on any difference.

## Build and install (.deb)

    platforms/linux/packaging/deb/build_deb.sh
    sudo apt install ./platforms/linux/packaging/deb/dist/yangialifbo_*_all.deb
    ibus restart

Then add the input source: Settings → Keyboard → Input Sources → + →
Uzbek → YangiAlifbo. Switch to it with the usual IBus shortcut.

The package depends on `ibus`, `python3`, `python3-gi` and `gir1.2-ibus-1.0`.
On systems where `/usr/bin/python3` has no matching `python3-gi`, set
`YANGIALIFBO_PYTHON` to a Python that has it (the launcher reads it).

## Live test

    YANGIALIFBO_PYTHON=/usr/bin/python3.12 platforms/linux/tests/live/run_live_test.sh

Needs `xvfb`, `xdotool`, `ibus`, `ibus-gtk3`. Runs its own X display and D-Bus
session and checks two cases (normal field converts; password field does not).

## Known gaps

- Tested on X11 only (Xvfb). Wayland is not tested.
- Words are shown as preedit (underlined) while typing and committed converted
  when the word ends. Apps that do not show preedit may show the raw text until
  the word ends.
- Terminal and IDE exclusion (the `cmd.exe` / `code.exe` list in Windows) is
  not ported yet.
- User whitelist and blacklist are read at engine start, not hot-reloaded.
- Chat-slang normalization is on; no setting yet.
- Flatpak is not written yet.
- Tested on Ubuntu 24.04 (sandbox). Kali is Debian-based; the package
  dependencies have the same names there, but it has not been tested on Kali.
