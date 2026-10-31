#!/usr/bin/env bash
# ============================================================================
# tests/desktop_config_test.sh — uji statis konfigurasi XFCE + LightDM
#
# Ini hanya memeriksa source package-list dan file konfigurasi live image.
# Tidak membangun ISO, memasang paket, menjalankan LightDM, atau membuktikan
# bahwa X.Org dan XFCE benar-benar bekerja di runtime.
# ============================================================================

set -uo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
PKG="${ROOT}/image/config/package-lists/oracle-desktop.list.chroot"
LM="${ROOT}/image/config/includes.chroot/etc/lightdm/lightdm.conf.d/50-oracle-live.conf"
GR="${ROOT}/image/config/includes.chroot/etc/lightdm/lightdm-gtk-greeter.conf"

pass=0; fail=0
ok() { printf '  ok   %s\n' "$1"; pass=$((pass+1)); }
no() { printf '  FAIL %s\n' "$1"; fail=$((fail+1)); }

[ -f "$PKG" ] && ok "package-list desktop ada" || no "package-list desktop hilang"
for p in xfce4 lightdm lightdm-gtk-greeter xserver-xorg-core \
         xserver-xorg-input-all xserver-xorg-video-all dbus-x11 polkitd pkexec; do
	grep -qx "$p" "$PKG" 2>/dev/null \
		&& ok "package desktop: $p" \
		|| no "package desktop hilang: $p"
done

[ -f "$LM" ] && ok "konfigurasi LightDM live ada" || no "konfigurasi LightDM live hilang"
for rule in 'greeter-session=lightdm-gtk-greeter' 'user-session=xfce' \
            'autologin-user=user' 'autologin-user-timeout=0'; do
	grep -Fqx "$rule" "$LM" 2>/dev/null \
		&& ok "LightDM rule: $rule" \
		|| no "LightDM rule hilang: $rule"
done

[ -f "$GR" ] && ok "konfigurasi GTK greeter ada" || no "konfigurasi GTK greeter hilang"
grep -Fq '[greeter]' "$GR" 2>/dev/null \
	&& ok "GTK greeter memiliki section greeter" \
	|| no "GTK greeter section hilang"

# Jangan membuat symlink display-manager.service secara manual dari source.
if find "${ROOT}/image/config" -type l -path '*display-manager.service' -print -quit 2>/dev/null | grep -q .; then
	no "source membuat symlink display-manager.service manual"
else
	ok "tidak ada symlink display-manager.service manual"
fi

printf '\nhasil: %d lulus, %d gagal\n' "$pass" "$fail"
echo "CATATAN: tes statis; tidak membuktikan paket atau desktop berjalan."
[ "$fail" -eq 0 ]
