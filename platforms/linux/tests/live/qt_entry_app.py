"""Minimal Qt6 text field for the live IBus test (Qt counterpart of entry_app.py).

Writes the text to OUT_FILE on every change. Not part of the installed package.
"""

import os
import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QLineEdit, QMainWindow

OUT_FILE = sys.argv[1]
TIMEOUT = int(os.environ.get("LIVE_TIMEOUT", "40"))


def save(text):
    with open(OUT_FILE, "w", encoding="utf-8") as fh:
        fh.write(text)


app = QApplication(sys.argv)
win = QMainWindow()
win.setWindowTitle("yangialifbo-qt-test")
edit = QLineEdit()
win.setCentralWidget(edit)
edit.textChanged.connect(save)
win.resize(400, 40)
win.show()
edit.setFocus()
QTimer.singleShot(TIMEOUT * 1000, app.quit)
sys.exit(app.exec())
