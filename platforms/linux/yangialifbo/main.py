# ──────────────────────────────────────────────────────────────────────
# YangiAlifbo — IBus component entry point.
# ibus-daemon starts this via the component XML (platforms/linux/data).
# ──────────────────────────────────────────────────────────────────────

import sys

import gi

gi.require_version("IBus", "1.0")
from gi.repository import GLib, IBus  # noqa: E402

from .engine import YangiAlifboEngine  # noqa: E402

COMPONENT_NAME = "org.freedesktop.IBus.YangiAlifbo"


def main():
    IBus.init()
    bus = IBus.Bus()
    if not bus.is_connected():
        print("YangiAlifbo: IBus daemon'ga ulanib bo‘lmadi", file=sys.stderr)
        return 1

    factory = IBus.Factory.new(bus.get_connection())
    factory.add_engine("yangialifbo", YangiAlifboEngine.__gtype__)
    bus.request_name(COMPONENT_NAME, 0)

    GLib.MainLoop().run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
