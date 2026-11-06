#!/usr/bin/env bash
# ============================================================================
# tests/package_list_format_test.sh — validasi FORMAT package-list
#
# KENAPA TES INI ADA
# live-build membaca package-list dengan:
#     Expand_packagelist ... | grep -v '^#'
# Artinya HANYA baris yang diawali '#' yang dibuang. Komentar di belakang nama
# paket:
#     firefox-esr    # peramban
# akan terbaca sebagai nama paket "firefox-esr    # peramban", apt gagal
# menemukannya, dan SELURUH build berhenti — setelah puluhan menit bootstrap.
#
# Bug ini nyata: sempat ditulis pada perubahan Phase 5 dan tertangkap hanya
# karena sumber live-build dibaca lebih dulu. Tes ini mencegah pengulangan.
#
# Yang diperiksa (statis, tanpa build):
#   1. Tidak ada komentar inline di package-list maupun profile.
#   2. Setiap baris non-komentar adalah nama paket Debian yang valid.
#   3. Tidak ada duplikat dalam satu berkas.
#   4. Tidak ada baris kosong berisi spasi saja yang menyelip.
#   5. Setiap profile yang dirujuk config/profiles.conf benar-benar ada.
#
# Jalankan: ./tests/package_list_format_test.sh
# ============================================================================

set -uo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

pass=0; fail=0
ok() { printf '  ok   %s\n' "$1"; pass=$((pass+1)); }
no() { printf '  FAIL %s\n' "$1"; fail=$((fail+1)); }

echo "== format package-list dan profile =="

LISTS=()
while IFS= read -r f; do LISTS+=("$f"); done < <(
	find "${ROOT}/image/config/package-lists" \
	     "${ROOT}/image/config/includes.chroot/usr/share/oracle/profiles" \
	     -type f \( -name '*.list.chroot' -o -name '*.list' \) 2>/dev/null | sort
)

[ "${#LISTS[@]}" -gt 0 ] && ok "menemukan ${#LISTS[@]} berkas package-list" \
	|| no "tidak ada package-list yang ditemukan"

for f in "${LISTS[@]}"; do
	rel="${f#"${ROOT}/"}"

	# 1. Komentar inline: karakter non-'#' diikuti spasi lalu '#'
	inline="$(grep -nE '^[^#[:space:]][^#]*[[:space:]]#' "$f" 2>/dev/null || true)"
	if [ -n "$inline" ]; then
		no "${rel}: komentar inline (akan terbaca sebagai bagian nama paket)"
		printf '%s\n' "$inline" | head -3 | sed 's/^/         /'
	else
		ok "${rel}: tidak ada komentar inline"
	fi

	# 2. Nama paket valid. Debian: huruf kecil, angka, + . - dan ':' untuk arch.
	bad=""
	while IFS= read -r pkg; do
		[ -n "$pkg" ] || continue
		case "$pkg" in
			[a-z0-9]*) ;;
			*) bad="${bad}${pkg}"$'\n'; continue ;;
		esac
		printf '%s' "$pkg" | grep -qE '^[a-z0-9][a-z0-9+.:-]*$' \
			|| bad="${bad}${pkg}"$'\n'
	done < <(grep -vhE '^[[:space:]]*(#|$)' "$f" 2>/dev/null)

	if [ -n "$bad" ]; then
		no "${rel}: nama paket tidak valid"
		printf '%s' "$bad" | head -3 | sed 's/^/         /'
	else
		ok "${rel}: semua nama paket valid"
	fi

	# 3. Duplikat
	dup="$(grep -vhE '^[[:space:]]*(#|$)' "$f" 2>/dev/null | sort | uniq -d)"
	if [ -n "$dup" ]; then
		no "${rel}: paket duplikat"
		printf '%s\n' "$dup" | head -3 | sed 's/^/         /'
	else
		ok "${rel}: tidak ada duplikat"
	fi

	# 4. Baris berisi spasi saja
	if grep -qnE '^[[:space:]]+$' "$f" 2>/dev/null; then
		no "${rel}: ada baris berisi spasi saja"
	else
		ok "${rel}: tidak ada baris spasi kosong"
	fi
done

# 5. Profile yang dirujuk harus ada berkasnya.
CONF="${ROOT}/config/profiles.conf"
PROFILE_DIR="${ROOT}/image/config/includes.chroot/usr/share/oracle/profiles"
if [ -f "$CONF" ]; then
	missing=""
	while IFS= read -r name; do
		[ -n "$name" ] || continue
		[ -f "${PROFILE_DIR}/${name}.list" ] || missing="${missing}${name}"$'\n'
	done < <(grep -vhE '^[[:space:]]*(#|$)' "$CONF" 2>/dev/null)

	if [ -n "$missing" ]; then
		no "profiles.conf merujuk profile yang tidak ada"
		printf '%s' "$missing" | sed 's/^/         /'
	else
		ok "semua profile di config/profiles.conf punya berkas"
	fi
else
	ok "config/profiles.conf tidak ada (image minimal)"
fi

printf '\nhasil: %d lulus, %d gagal\n' "$pass" "$fail"
echo "CATATAN: tes statis; tidak memverifikasi paket ada di arsip Debian."
if [ "$fail" -gt 0 ]; then exit 1; fi
