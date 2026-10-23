#!/usr/bin/env bash
# Builds yangialifbo_<version>_all.deb from platforms/linux.
# Usage: build_deb.sh            (writes to packaging/deb/dist/)
#        VERSION=0.1.1 OUT=/tmp/x build_deb.sh
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LINUX="$(cd "$HERE/../.." && pwd)"
REPO="$(cd "$LINUX/../.." && pwd)"
VERSION="${VERSION:-0.1.2}"
OUT="${OUT:-$HERE/dist}"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

PKG="$STAGE/yangialifbo_${VERSION}_all"
mkdir -p "$PKG/DEBIAN" \
         "$PKG/usr/lib/yangialifbo" \
         "$PKG/usr/libexec/yangialifbo" \
         "$PKG/usr/share/ibus/component" \
         "$PKG/usr/share/doc/yangialifbo"

# Python package, without caches.
cp -r "$LINUX/yangialifbo" "$PKG/usr/lib/yangialifbo/"
find "$PKG/usr/lib/yangialifbo" -name __pycache__ -type d -prune -exec rm -rf {} +

install -m755 "$HERE/yangialifbo-ibus" "$PKG/usr/libexec/yangialifbo/yangialifbo-ibus"
install -m644 "$LINUX/data/yangialifbo.xml" "$PKG/usr/share/ibus/component/yangialifbo.xml"
install -m644 "$REPO/LICENSE" "$PKG/usr/share/doc/yangialifbo/copyright"

cat > "$PKG/DEBIAN/control" <<CONTROL
Package: yangialifbo
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: all
Depends: ibus, python3, python3-gi, gir1.2-ibus-1.0
Maintainer: Bilolbek Yoldoshxojayev <javadevpro.0101@gmail.com>
Homepage: https://github.com/BilolbekYoldoshxojayev/yangicha-alifbo
Description: Uzbek input method for the new Latin alphabet (IBus)
 Converts Uzbek words typed in the old Latin spelling to the 2024 reformed
 alphabet (sh->ş, ch->ç, o'->ö, g'->ğ) as you type, in any text field
 that IBus handles. Password fields are skipped.
CONTROL

for script in postinst postrm; do
  cat > "$PKG/DEBIAN/$script" <<'MAINTAINER'
#!/bin/sh
set -e
if command -v ibus >/dev/null 2>&1; then
    ibus write-cache --system >/dev/null 2>&1 || true
fi
exit 0
MAINTAINER
  chmod 755 "$PKG/DEBIAN/$script"
done

mkdir -p "$OUT"
dpkg-deb --root-owner-group --build "$PKG" "$OUT" >/dev/null
echo "$OUT/yangialifbo_${VERSION}_all.deb"
