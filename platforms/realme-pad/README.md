# Realme Pad ARM64 research (Bookish OS)

This directory tracks **research only** for RMP2102 (LTE) and RMP2103 (Wi-Fi), separately. It does not contain a bootable image, working UEFI, Windows ARM port, installable firmware, or approved flash instructions.

## Provenance and scope

- Historical research: [RealmePad-Windows-ARM](https://github.com/XGAMERSTORE/RealmePad-Windows-ARM), especially [compatibility evidence](https://github.com/XGAMERSTORE/RealmePad-Windows-ARM/blob/main/docs/COMPATIBILITY.md). Keep that repository read-only during migration.
- Product policy: [Bookish OS unified distribution plan](../../docs/BOOKISH_UNIFIED_OS.md). Bookish OS is Linux-based; Windows ARM is **not** the tablet release target.
- Public [RMP6768 BoardConfig](https://github.com/Realme-Pad-Dev/android_device_realme_RMP6768/blob/lineage-20.0/BoardConfig.mk) identifies Android image packaging properties; these are **not** measured RAM reservations or proof of a bootloader entry point.
- Public [RMP6768 kernel build config](https://github.com/Realme-Pad-Dev/android_kernel_realme_RMP6768/blob/arrow-13.1/build.config.RMP6768) names downstream DTB candidates. Their exact model mapping and the FDT actually supplied by firmware remain unverified.
- [Redmi 9 MT6768 research](https://github.com/hataketsu/mt6768-mainline-notes) documents device-specific LK/U-Boot and reserved-memory pitfalls; **none** of its offsets, payload format, recovery steps or boot success transfer to Realme Pad.

## Evidence matrix (no hardware proof yet)

| Required gate | RMP2102 LTE | RMP2103 Wi-Fi |
| --- | --- | --- |
| Redacted, read-only device/board identity inventory | Missing | Missing |
| Exact variant boot-chain and signature-policy evidence | Missing | Missing |
| LK-provided FDT and reserved-memory validation | Missing | Missing |
| Independently verified exact-model recovery path | Missing | Missing |
| Repeatable, recoverable non-destructive custom-code handoff | Not demonstrated | Not demonstrated |
| Linux/UEFI boot on physical tablet | Not demonstrated | Not demonstrated |

**Nearest blocker:** Without a verified, recoverable LK handoff and exact-model reserved-memory/signature constraints, building an EFI or U-Boot payload cannot establish a safe tablet boot path. Recovery must be established *before* any device-side experiment.

## Safe next steps

1. Collect **read-only** ADB property and partition-*name* inventories separately for each variant, using the historical project's inventory tooling; redact serial numbers, IMEI, identifiers and other personal data before publishing.
2. Review matching public kernel DTS sources for `/memory`, `/reserved-memory`, `chosen` and boot-console details. Record source URLs, revisions, evidence quality and unresolved variant mapping. Do not assume a DTS is the LK-supplied FDT.
3. Keep host-only static checks and mocks separate from emulator evidence and real-hardware evidence. Passing CI or compiling a diagnostic EFI **does not** establish UEFI, Linux or Windows boot on RMP2102/RMP2103.
4. Require independently verified exact-model recovery and owner consent before planning any future non-destructive hardware test.

**Prohibited at this stage:** flashing, partition writes, bootloader unlocking, disabling verified boot, repacking boot images for device use, or treating another MT6768 device's memory map as applicable here.
