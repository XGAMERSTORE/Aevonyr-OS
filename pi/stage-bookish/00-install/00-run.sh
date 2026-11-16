#!/bin/bash -e
install -d "${ROOTFS_DIR}/opt/bookish" "${ROOTFS_DIR}/usr/local/bin" \
    "${ROOTFS_DIR}/usr/share/applications" "${ROOTFS_DIR}/etc/xdg/autostart"
cp -a files/aevonyr files/bookish files/language-packs "${ROOTFS_DIR}/opt/bookish/"
install -m 0755 files/bookish-session "${ROOTFS_DIR}/usr/local/bin/bookish-session"
install -m 0644 files/bookish.desktop "${ROOTFS_DIR}/usr/share/applications/bookish.desktop"
install -m 0644 files/bookish.desktop "${ROOTFS_DIR}/etc/xdg/autostart/bookish.desktop"
install -m 0644 files/build-info.txt "${ROOTFS_DIR}/opt/bookish/build-info.txt"
on_chroot <<'CHROOT'
set -eu
test "$(dpkg --print-architecture)" = arm64
cd /opt/bookish
python3 -m compileall -q aevonyr bookish
python3 -m bookish --languages
python3 -c 'import tkinter; import aevonyr.ui'
CHROOT
