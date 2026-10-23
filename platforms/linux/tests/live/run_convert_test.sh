#!/usr/bin/env bash
# Live test for yangialifbo-convert: types plain text into a Qt field (no IBus),
# selects it, runs the converter, and checks the replaced text.
# Needs: xvfb, xdotool, xclip, python3 with PyQt6.
#   PYTHON_APP=/usr/bin/python3.12 ./run_convert_test.sh
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LINUX="$(cd "$HERE/../.." && pwd)"
DISPLAY_NUM="${DISPLAY_NUM:-97}"
export DISPLAY=":${DISPLAY_NUM}"
PY="${PYTHON_APP:-/usr/bin/python3}"
WORK="$(mktemp -d)"
OUT_FILE="$WORK/field.txt"
TYPED="shahar salom o'rtoq chiroyli"
EXPECTED="şahar salom örtoq çiroyli"

XVFB_PID=""
cleanup() { [ -n "$XVFB_PID" ] && kill "$XVFB_PID" 2>/dev/null || true; rm -rf "$WORK"; }
trap cleanup EXIT

Xvfb "$DISPLAY" -screen 0 1024x768x24 >/dev/null 2>&1 &
XVFB_PID=$!
sleep 2

export QT_QPA_PLATFORM=xcb
env -u QT_IM_MODULE "$PY" -I "$HERE/qt_entry_app.py" "$OUT_FILE" >"$WORK/app.log" 2>&1 &
APP_PID=$!

WID=""
for _ in $(seq 1 30); do
  WID="$(xdotool search --name yangialifbo-qt-test 2>/dev/null | head -1 || true)"
  [ -n "$WID" ] && break
  sleep 1
done
[ -n "$WID" ] || { echo "FAIL: window not found"; cat "$WORK/app.log"; exit 1; }

xdotool windowactivate --sync "$WID" 2>/dev/null || xdotool windowfocus "$WID"
sleep 1
xdotool type --delay 60 -- "$TYPED"
sleep 1
xdotool key ctrl+a
sleep 1

# Run the converter with the package from this checkout.
PYTHONPATH="$LINUX" "$PY" -m yangialifbo.convert_selection
sleep 2

kill "$APP_PID" 2>/dev/null || true
wait "$APP_PID" 2>/dev/null || true

GOT="$(cat "$OUT_FILE" 2>/dev/null || true)"
echo "typed:    ${TYPED}"
echo "field:    ${GOT}"
if [ "$GOT" = "$EXPECTED" ]; then echo "PASS (convert selection)"; else echo "FAIL: expected: ${EXPECTED}"; exit 1; fi
