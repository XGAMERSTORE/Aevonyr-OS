#!/usr/bin/env bash
# Build a real Linux live image, not an UEFI-app prototype.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="${AEVONYR_WORK_DIR:-$ROOT/.live-build-work}"
DIST="${AEVONYR_OUTPUT_DIR:-$ROOT/dist}"
if [[ $(id -u) -ne 0 ]]; then echo "Run as root" >&2; exit 1; fi
if ! command -v lb >/dev/null; then echo "Install Debian live-build first" >&2; exit 1; fi
test -f "$ROOT/aevonyr/__main__.py"
if [[ "$WORK" == "$ROOT" || "$WORK" == "/" ]]; then echo "Unsafe build dir" >&2; exit 1; fi
mkdir -p "$WORK" "$DIST"
cd "$WORK"
lb config noauto \
  --distribution trixie \
  --architectures amd64 \
  --binary-images iso-hybrid \
  --archive-areas "main contrib non-free-firmware" \
  --backports true \
  --bootloaders "grub-efi grub-pc" \
  --debian-installer false \
  --iso-application "Aevonyr OS Live" \
  --iso-publisher "Aevonyr Studio" \
  --iso-volume "AEVONYR_LIVE_072" \
  --bootappend-live "boot=live components quiet splash username=user hostname=aevonyr locales=en_US.UTF-8 keyboard-layouts=us"
mkdir -p config/package-lists config/includes.chroot/usr/lib/python3/dist-packages config/hooks/normal
cp "$ROOT/iso/package-lists/desktop.list.chroot" config/package-lists/
cp -a "$ROOT/iso/overlays/." config/includes.chroot/
cp -a "$ROOT/iso/hooks/normal/." config/hooks/normal/
cp -a "$ROOT/aevonyr" config/includes.chroot/usr/lib/python3/dist-packages/
find config/includes.chroot/usr/lib/python3/dist-packages/aevonyr -name __pycache__ -type d -prune -exec rm -rf {} +
find config/includes.chroot/usr/lib/python3/dist-packages/aevonyr -name '*.pyc' -type f -delete
chmod 755 config/includes.chroot/usr/local/bin/*
echo "Building Aevonyr Linux live ISO; Debian downloads required"
lb build 2>&1 | tee "$DIST/build.log"
IMAGE="$(find . -maxdepth 1 -type f -name '*.iso' -print -quit)"
if [[ -z "$IMAGE" ]]; then echo "No ISO produced" >&2; exit 1; fi
cp "$IMAGE" "$DIST/Aevonyr-OS-0.7.2-Linux-Live-amd64.iso"
(cd "$DIST" && sha256sum Aevonyr-OS-0.7.2-Linux-Live-amd64.iso > SHA256SUMS)
ls -lh "$DIST/Aevonyr-OS-0.7.2-Linux-Live-amd64.iso"
