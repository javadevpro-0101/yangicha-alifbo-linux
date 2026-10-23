# YangiAlifbo for Linux (IBus)

Status: **early**. The conversion rules are ported and verified against the
Windows code; the IBus engine has not yet been tested with a live keyboard.

## Layout

- `yangialifbo/engine.py` — IBus engine: buffers letters per word, skips
  password fields (IBus input purpose), converts on delimiters.
- `yangialifbo/core/` — Python port of `src/Core/` (phonetics, chat
  normalizer, language detector, word decision).
- `yangialifbo/data/` — word lists (copied from `src/Core/Dictionaries/`).
- `data/yangialifbo.xml` — IBus component file.
- `tests/parity/` — compares the Python port with the C# code (the oracle).

## Parity test

    platforms/linux/tests/parity/run_parity.sh

Needs the .NET 8 SDK. Runs about 30 000 decisions in both implementations
and fails on any difference.

## Running (development only)

The engine is not installable yet. The component XML runs
`python3 -m yangialifbo.main`, so the package must be on `PYTHONPATH`.
Packaging (.deb / Flatpak) is the next step.

    export PYTHONPATH=$PWD/platforms/linux
    python3 -m yangialifbo.main        # needs the python3-gi and gir1.2-ibus-1.0 packages

## Known gaps

- Keyboard hook behaviour is not verified in a live X11 or Wayland session.
- Terminal and IDE exclusion (the `cmd.exe` / `code.exe` list in Windows) is
  not ported yet.
- User whitelist and blacklist are read at engine start, not hot-reloaded.
- Chat-slang normalization is on; no setting yet.
- Packaging (.deb, Flatpak) is not written yet.
