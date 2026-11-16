#!/usr/bin/env bash
# Build a regular image file only; never flash a host disk.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${1:-$ROOT/build/pi4}"
if [[ $(uname -m) != aarch64 ]]; then
    echo 'Use a native ARM64 Linux builder (GitHub ubuntu-24.04-arm).' >&2
    exit 2
fi
if [[ $EUID != 0 ]]; then
    echo 'pi-gen requires root for chroot, mounts and loop devices.' >&2
    exit 2
fi
# A fresh build directory prevents stale root filesystems entering an image.
if [[ -e "$OUT" ]]; then
    echo "Build directory already exists: $OUT; choose a fresh directory." >&2
    exit 2
fi
if [[ "$OUT" =~ [[:space:]] ]]; then
    echo 'pi-gen requires a path without whitespace.' >&2
    exit 2
fi
PIN="$(cat "$ROOT/pi/pi-gen-revision")"
[[ "$PIN" =~ ^[0-9a-f]{40}$ ]]
mkdir -p "$OUT"
OUT="$(realpath "$OUT")"
git clone --no-checkout https://github.com/RPi-Distro/pi-gen.git "$OUT/pi-gen"
git -C "$OUT/pi-gen" checkout --detach "$PIN"
cp "$ROOT/pi/config" "$OUT/pi-gen/config"
cp -a "$ROOT/pi/stage-bookish" "$OUT/pi-gen/stage-bookish"
FILES="$OUT/pi-gen/stage-bookish/00-install/files"
cp -a "$ROOT/aevonyr" "$ROOT/bookish" "$ROOT/language-packs" "$FILES/"
find "$FILES" -type d -name __pycache__ -prune -exec rm -rf {} +
printf 'Bookish commit: %s\npi-gen commit: %s\nTarget: Raspberry Pi 4, ARM64, 8 GB\nHardware validation: pending\n' \
    "$(git -C "$ROOT" rev-parse HEAD)" "$PIN" > "$FILES/build-info.txt"
touch "$OUT/pi-gen/stage2/SKIP_IMAGES"
cd "$OUT/pi-gen"
./build.sh
shopt -s nullglob
images=(deploy/*bookish-pi4-arm64*.img.xz)
[[ ${#images[@]} -eq 1 ]] || { echo 'Expected exactly one Pi image' >&2; exit 1; }
xz -t "${images[0]}"
cp "$FILES/build-info.txt" deploy/build-info.txt
cp "$ROOT/docs/RASPBERRY_PI4_ARM64.md" deploy/README.md
cd deploy
sha256sum ./*.img.xz > SHA256SUMS
sha256sum -c SHA256SUMS
