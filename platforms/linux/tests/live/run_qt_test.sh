#!/usr/bin/env bash
# Live test for Qt6 apps: types into a QLineEdit through IBus (QT_IM_MODULE=ibus).
# Needs: xvfb, xdotool, ibus, python3-pyqt6 and the Qt6 IBus input plugin.
#   YANGIALIFBO_PYTHON=/usr/bin/python3.12 ./run_qt_test.sh
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DISPLAY_NUM="${DISPLAY_NUM:-98}"
export DISPLAY=":${DISPLAY_NUM}"
PY="${PYTHON_APP:-${YANGIALIFBO_PYTHON:-/usr/bin/python3}}"
WORK="$(mktemp -d)"
export WORK HERE PY
export OUT_FILE="$WORK/qt-typed.txt"
export TYPED="shahar salom o'rtoq chiroyli "
EXPECTED="şahar salom örtoq çiroyli "

XVFB_PID=""
cleanup() { [ -n "$XVFB_PID" ] && kill "$XVFB_PID" 2>/dev/null || true; [ "${KEEP:-0}" = 1 ] || rm -rf "$WORK"; }
trap cleanup EXIT

Xvfb "$DISPLAY" -screen 0 1024x768x24 >/dev/null 2>&1 &
XVFB_PID=$!
sleep 2

cat > "$WORK/session.sh" <<'SESSION'
#!/usr/bin/env bash
set -uo pipefail
export QT_IM_MODULE=ibus QT_QPA_PLATFORM=xcb
setxkbmap us
ibus-daemon -drx >"$WORK/ibusd.log" 2>&1 &
sleep 3
ibus engine yangialifbo
sleep 1

"$PY" -I "$HERE/qt_entry_app.py" "$OUT_FILE" >"$WORK/qt-app.log" 2>&1 &
APP_PID=$!

WID=""
for _ in $(seq 1 30); do
  WID="$(xdotool search --name yangialifbo-qt-test 2>/dev/null | head -1 || true)"
  [ -n "$WID" ] && break
  sleep 1
done
if [ -z "$WID" ]; then
  echo "window not found"; cat "$WORK/qt-app.log"; kill "$APP_PID" 2>/dev/null || true; exit 1
fi
xdotool windowactivate --sync "$WID" 2>/dev/null || xdotool windowfocus "$WID"
sleep 1
xdotool type --delay 120 -- "$TYPED"
sleep 2
kill "$APP_PID" 2>/dev/null || true
wait "$APP_PID" 2>/dev/null || true
SESSION
chmod +x "$WORK/session.sh"

dbus-run-session -- "$WORK/session.sh" || true

if [ ! -s "$OUT_FILE" ]; then
  echo "FAIL: no text captured (logs: $WORK)"; exit 1
fi
GOT="$(cat "$OUT_FILE")"
echo "typed:    ${TYPED}"
echo "captured: ${GOT}"
if [ "$GOT" = "$EXPECTED" ]; then echo "PASS (Qt6)"; else echo "FAIL (Qt6): expected: ${EXPECTED}"; exit 1; fi
