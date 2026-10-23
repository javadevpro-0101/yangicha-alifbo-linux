"""Minimal GTK3 text field for the live IBus test.

Writes what the user typed to OUT_FILE on every change, so the file is
current even if the process is killed. Used by run_live_test.sh; not part of the installed package.
"""

import os
import sys

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk  # noqa: E402

OUT_FILE = sys.argv[1]
TIMEOUT = int(os.environ.get("LIVE_TIMEOUT", "25"))


def save(entry):
    # Written on every change so the test can read it even if we kill us.
    with open(OUT_FILE, "w", encoding="utf-8") as fh:
        fh.write(entry.get_text())
    return False


def finish(entry):
    save(entry)
    Gtk.main_quit()
    return False


win = Gtk.Window(title="yangialifbo-live-test")
entry = Gtk.Entry()
win.add(entry)
win.connect("destroy", lambda *_: finish(entry))
win.set_default_size(400, 40)
win.show_all()
if os.environ.get("ENTRY_PURPOSE") == "password":
    entry.set_input_purpose(Gtk.InputPurpose.PASSWORD)
entry.connect("changed", save)
entry.grab_focus()
GLib.timeout_add_seconds(TIMEOUT, finish, entry)
Gtk.main()
