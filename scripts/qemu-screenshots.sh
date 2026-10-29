#!/usr/bin/env bash
# Experimental graphics-only QEMU smoke. Screenshots need manual inspection.
# This does NOT prove successful login or an installed system.
set -Eeuo pipefail
ISO="$(realpath "$1")"
RESULTS="$2"
mkdir -p "$RESULTS"
RESULTS="$(realpath "$RESULTS")"
test -s "$ISO"
command -v qemu-system-x86_64 >/dev/null
firmware=""
for candidate in /usr/share/OVMF/OVMF_CODE_4M.fd /usr/share/OVMF/OVMF_CODE.fd; do
  if [ -r "$candidate" ]; then firmware="$candidate"; break; fi
done
for mode in bios uefi; do
  if [ "$mode" = uefi ] && [ -z "$firmware" ]; then
    echo "UEFI firmware not installed" >&2
    continue
  fi
  socket="$RESULTS/$mode.sock"
  screenshot="$RESULTS/$mode-screen.ppm"
  rm -f "$socket"
  if [ "$mode" = bios ]; then screen=21; else screen=22; fi
  set -- qemu-system-x86_64 -machine q35 -accel tcg -m 2048 -smp 2
  set -- "$@" -boot order=d -drive "file=$ISO,media=cdrom,readonly=on"
  set -- "$@" -vga std -display "vnc=127.0.0.1:$screen"
  set -- "$@" -monitor "unix:$socket,server=on,wait=off"
  set -- "$@" -serial "file:$RESULTS/$mode-serial.log" -no-reboot
  if [ "$mode" = uefi ]; then set -- "$@" -bios "$firmware"; fi
  echo "Trying $mode graphical boot screenshot (experimental)"
  "$@" > "$RESULTS/$mode-qemu.log" 2>&1 &
  pid=$!
  sleep 75
  if kill -0 "$pid" 2>/dev/null && [ -S "$socket" ] && command -v socat >/dev/null; then
    printf "screendump %s\n" "$screenshot" | socat - "UNIX-CONNECT:$socket" || true
  fi
  kill "$pid" 2>/dev/null || true
  wait "$pid" 2>/dev/null || true
  if [ -s "$screenshot" ]; then
    echo "$mode screenshot captured: $screenshot"
  else
    echo "No $mode screenshot; consult logs" >&2
  fi
done
