# Bookish OS — unified distribution plan

**Canonical project:** `XGAMERSTORE/Aevonyr-OS` (repository name is historical; Bookish OS is the product name).

Bookish OS is **one Linux-based distribution**, with shared identity, shell, applications, configuration and release process. It has separate hardware targets:

| Target | Architecture | Status |
| --- | --- | --- |
| Desktop / laptop | x86_64 | Existing Python/Tk shell prototype; not yet an independently bootable, validated installer |
| Realme Pad RMP2102 LTE | ARM64 / MT6768 | Research only; no verified Linux boot or complete device support |
| Realme Pad RMP2103 Wi-Fi | ARM64 / MT6768 | Research only; no verified Linux boot or complete device support |

## Repository consolidation

- This repository is the **single product home** for Bookish OS. Existing `aevonyr/` Python package stays in place temporarily for compatibility; product-facing naming should progressively become Bookish OS.
- `XGAMERSTORE/RealmePad-Windows-ARM` is a **read-only research source during migration**, not a second OS. Preserve original commit history and source attribution; do not delete or claim its experimental EFI as functional.
- Import **only reviewed, read-only hardware evidence and tooling** under `platforms/realme-pad/` with explicit provenance. Do not copy unverified bootloader binaries, proprietary firmware, Windows images or flash scripts into releases.
- Windows ARM boot is no longer the tablet release goal. Wine/Waydroid, where legally and technically available, are optional compatibility layers, not the operating-system base.

## Release gates

1. Desktop: reproducible Linux image, signed/checksummed artifact, VM install and graphical smoke tests.
2. Shared UX: responsive desktop/tablet shell, touch/keyboard layouts, Bookish branding, accessible settings and book library.
3. Tablet: independently verified exact-model device tree, RAM/reserved-memory map, bootchain handoff, kernel drivers, recovery plan, then **non-destructive** boot experiments with explicit owner consent.
4. Never mark a tablet image installable or bootable until actual RMP2102/RMP2103 hardware tests pass.

## Safety

No flashing, bootloader unlock, partition writes, or assumptions that Redmi 9 U-Boot supports Realme Pad. A passing CI job proves only the tested software behavior, **not** a bootable OS.
