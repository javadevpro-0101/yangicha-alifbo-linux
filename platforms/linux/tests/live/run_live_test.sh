#!/usr/bin/env bash
# Live test: types Latin Uzbek into a real GTK3 entry through IBus and checks
# the result. Two cases:
#   1. normal text field      -> words are converted
#   2. password field         -> nothing is converted (safety rule)
#
# Needs: xvfb, xdotool, ibus, ibus-gtk3, python3 with gi (Gtk 3).
#
#   YANGIALIFBO_PYTHON=/usr/bin/python3.12 ./run_live_test.sh
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DISPLAY_NUM="${DISPLAY_NUM:-99}"
export DISPLAY=":${DISPLAY_NUM}"
export YANGIALIFBO_PYTHON="${YANGIALIFBO_PYTHON:-/usr/bin/python3}"
APP_PY="${PYTHON_APP:-$YANGIALIFBO_PYTHON}"
WORK="$(mktemp -d)"
export WORK HERE APP_PY

XVFB_PID=""
cleanup() {
  [ -n "$XVFB_PID" ] && kill "$XVFB_PID" 2>/dev/null || true
  rm -rf "$WORK"
}
trap cleanup EXIT

Xvfb "$DISPLAY" -screen 0 1024x768x24 >/dev/null 2>&1 &
XVFB_PID=$!
sleep 2

# One IBus + D-Bus session per case, so state does not carry over.
# Written to a file so the apostrophes in the typed text are not parsed by the shell.
cat > "$WORK/session.sh" <<'SESSION'
#!/usr/bin/env bash
set -uo pipefail
export GTK_IM_MODULE=ibus XMODIFIERS=@im=ibus
setxkbmap us
ibus-daemon -drx >"$WORK/ibusd.log" 2>&1 &
sleep 3
ibus engine yangialifbo
sleep 1

cp "$HERE/entry_app.py" "$WORK/yangialifbo_live_entry.py"
LIVE_TIMEOUT=40 "$APP_PY" -I "$WORK/yangialifbo_live_entry.py" "$OUT_FILE" &
APP_PID=$!

WID=""
for _ in $(seq 1 30); do
  WID="$(xdotool search --name yangialifbo-live-test 2>/dev/null | head -1 || true)"
  [ -n "$WID" ] && break
  sleep 1
done
if [ -z "$WID" ]; then
  echo "window not found"
  kill "$APP_PID" 2>/dev/null || true
  exit 1
fi

xdotool windowactivate --sync "$WID" 2>/dev/null || xdotool windowfocus "$WID"
sleep 1
xdotool type --delay 120 -- "$TYPED"
sleep 2
kill "$APP_PID" 2>/dev/null || true
wait "$APP_PID" 2>/dev/null || true
SESSION
chmod +x "$WORK/session.sh"

FAILED=0

run_case() {
  local name="$1" purpose="$2" typed="$3" expected="$4"
  export OUT_FILE="$WORK/$name.txt" TYPED="$typed" ENTRY_PURPOSE="$purpose"
  rm -f "$OUT_FILE"
  dbus-run-session -- "$WORK/session.sh" || true

  if [ ! -s "$OUT_FILE" ]; then
    echo "[$name] FAIL: no text captured (IBus log: $WORK/ibusd.log)"
    FAILED=1
    return
  fi
  local got
  got="$(cat "$OUT_FILE")"
  echo "[$name] typed:    ${typed}"
  echo "[$name] captured: ${got}"
  if [ "$got" = "$expected" ]; then
    echo "[$name] PASS"
  else
    echo "[$name] FAIL: expected: ${expected}"
    FAILED=1
  fi
}

run_case "text-field" "free" \
  "shahar salom o'rtoq chiroyli " \
  "şahar salom örtoq çiroyli "

run_case "password-field" "password" \
  "shahar salom o'rtoq chiroyli " \
  "shahar salom o'rtoq chiroyli "

exit "$FAILED"
