#!/usr/bin/env bash
# Reproducible-ish Bookish OS x86_64 Debian live ISO build; no flashing.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${1:-$ROOT/build/bookish-live}"
mkdir -p "$OUT"
OUT="$(cd "$OUT" && pwd)"
if [[ "$OUT" == "$ROOT" || "$OUT" == / ]]; then
  echo "Refusing unsafe build directory" >&2; exit 2
fi
for command in lb rsync; do
  command -v "$command" >/dev/null || { echo "Missing $command" >&2; exit 2; }
done
mkdir -p "$OUT/config/package-lists" "$OUT/config/includes.chroot/opt/bookish" \
  "$OUT/config/includes.chroot/usr/local/bin" \
  "$OUT/config/includes.chroot/etc/xdg/autostart"
cat > "$OUT/config/package-lists/bookish.list.chroot" <<'EOF'
linux-image-amd64
live-boot
live-config
xfce4
lightdm
xorg
dbus-x11
network-manager
python3
python3-tk
fonts-dejavu
EOF
rsync -a --delete "$ROOT/aevonyr" "$ROOT/bookish" "$ROOT/language-packs" \
  "$OUT/config/includes.chroot/opt/bookish/"
cat > "$OUT/config/includes.chroot/usr/local/bin/bookish-session" <<'EOF'
#!/bin/sh
cd /opt/bookish || exit 1
export PYTHONPATH=/opt/bookish
exec /usr/bin/python3 -m bookish
EOF
chmod +x "$OUT/config/includes.chroot/usr/local/bin/bookish-session"
cat > "$OUT/config/includes.chroot/etc/xdg/autostart/bookish.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Name=Bookish OS
Comment=Bookish library desktop shell
Exec=/usr/local/bin/bookish-session
Terminal=false
X-GNOME-Autostart-enabled=true
EOF
cd "$OUT"
lb config --mode debian --distribution bookworm --architectures amd64 --binary-images iso-hybrid \
  --bootappend-live "boot=live components" --debian-installer none \
  --archive-areas "main" --mirror-bootstrap "https://deb.debian.org/debian/" \
  --mirror-chroot "https://deb.debian.org/debian/" \
  --mirror-binary "https://deb.debian.org/debian/" \
  --mirror-chroot-security "https://security.debian.org/debian-security/" \
  --mirror-binary-security "https://security.debian.org/debian-security/"
lb build
iso="$(find . -maxdepth 1 -name '*.iso' -type f -print -quit)"
[[ -n "$iso" ]] || { echo "Build completed without ISO" >&2; exit 1; }
sha256sum "$iso" > "$iso.sha256"
echo "ISO: $OUT/${iso#./}"
echo "SHA256: $OUT/${iso#./}.sha256"
echo "UNVERIFIED: hardware boot, installer, Realme Pad ARM64"
