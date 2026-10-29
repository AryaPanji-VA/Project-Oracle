#!/bin/sh
# ============================================================================
# scripts/gen-profile-list.sh — hasilkan package-list build-time dari profile
#
# Single source of truth: file profile di
#   image/config/includes.chroot/usr/share/oracle/profiles/<nama>.list
# Dipakai DUA kali:
#   - build-time : skrip ini merakit package-list untuk live-build
#   - runtime    : CLI `oracle profile install` membaca file yang sama
#
# Tidak ada daftar paket kedua. Kalau perlu menambah paket, ubah file profile.
#
# Kontrak keluaran:
#   - Ada profile dipilih  -> tulis file package-list (satu paket per baris,
#     duplikat dibuang, urutan dipertahankan).
#   - Tidak ada profile    -> TIDAK membuat file, exit 0 (image minimal).
#     File kosong membuat live-build menganggap ada paket yang hilang.
#   - Nama profile tidak valid / tidak ada / paket tidak valid -> exit 1,
#     tidak meninggalkan file setengah jadi.
#
# Variabel lingkungan (wajib, sengaja tidak ada default supaya tidak salah
# menulis ke lokasi yang tidak dimaksud):
#   PROFILES_CONF  file berisi nama profile yang dipilih
#   PROFILE_DIR    direktori berisi <nama>.list
#   OUT            path file package-list hasil (kosong = cetak ke stdout)
#
# Berlaku POSIX sh: dipakai di host maupun di dalam container Debian.
# ============================================================================

set -eu

PROFILES_CONF="${PROFILES_CONF:-}"
PROFILE_DIR="${PROFILE_DIR:-}"
OUT="${OUT:-}"

die() { printf 'oracle-profile: %s\n' "$*" >&2; exit 1; }
info() { printf '[oracle] %s\n' "$*" >&2; }

[ -n "$PROFILES_CONF" ] || die "PROFILES_CONF wajib diisi"
[ -n "$PROFILE_DIR" ]   || die "PROFILE_DIR wajib diisi"
[ -f "$PROFILES_CONF" ] || die "PROFILES_CONF tidak ada: $PROFILES_CONF"
[ -d "$PROFILE_DIR" ]   || die "PROFILE_DIR tidak ada: $PROFILE_DIR"

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

RAW="$WORK/packages.raw"
: > "$RAW"

# Buang komentar dan spasi di ujung baris — TAPI jangan buang spasi di tengah.
# Menghapus spasi di tengah membuat nama tidak valid ('net working') berubah
# menjadi nama valid ('networking') secara diam-diam, sehingga kesalahan tulis
# di file konfigurasi lolos tanpa peringatan.
selected="$(awk '{ sub(/#.*/, ""); gsub(/^[ \t]+|[ \t]+$/, ""); if (length) print }' "$PROFILES_CONF")"

if [ -z "$selected" ]; then
	info "tidak ada profile dipilih; image minimal"
else
	# Dibaca per BARIS, bukan per kata. `for x in $selected` memecah input
	# pada spasi, sehingga 'net working' menjadi dua nama yang tampak sah.
	# Input yang rusak harus ditolak, bukan dipecah menjadi sesuatu yang lolos.
	while IFS= read -r name; do
		[ -n "$name" ] || continue

		# Nama profile divalidasi SEBELUM dipakai untuk menyusun path.
		# Tanpa ini, nama seperti '../../etc/passwd' bisa keluar dari PROFILE_DIR.
		printf '%s' "$name" | grep -Eq '^[a-z0-9][a-z0-9-]{0,31}$' \
			|| die "nama profile tidak valid: '$name'"

		list="$PROFILE_DIR/$name.list"
		if [ ! -f "$list" ]; then
			info "profile tersedia di $PROFILE_DIR:"
			for f in "$PROFILE_DIR"/*.list; do
				[ -e "$f" ] || continue
				printf '  - %s\n' "$(basename "$f" .list)" >&2
			done
			die "profile '$name' dipilih di $PROFILES_CONF tapi $list tidak ada"
		fi

		# Paket juga divalidasi. Nama paket Debian: huruf kecil, angka, + . -
		# Tanpa validasi, baris aneh bisa masuk ke apt sebagai argumen asing.
		# Spasi di ujung dibuang; spasi di tengah dibiarkan supaya nama rusak
		# ditolak, bukan diperbaiki diam-diam.
		awk '{ sub(/#.*/, ""); gsub(/^[ 	]+|[ 	]+$/, ""); if (length) print }' "$list" \
			> "$WORK/pkgs.raw"
		while IFS= read -r p; do
			[ -n "$p" ] || continue
			printf '%s' "$p" | grep -Eq '^[a-z0-9][a-z0-9+.-]*$' \
				|| die "nama paket tidak valid di $list: '$p'"
			printf '%s\n' "$p" >> "$RAW"
		done < "$WORK/pkgs.raw"

		info "profile '$name' dipilih"
	done <<EOF
$(printf '%s\n' "$selected")
EOF
fi

# Buang duplikat, pertahankan urutan kemunculan pertama.
# Dua profile boleh memuat paket yang sama tanpa memasangnya dua kali.
awk 'NF && !seen[$0]++' "$RAW" > "$WORK/packages.final"
count="$(grep -c . "$WORK/packages.final" || true)"

if [ -z "$OUT" ]; then
	cat "$WORK/packages.final"
	info "$count paket"
	exit 0
fi

if [ "$count" -eq 0 ]; then
	# Jangan tinggalkan file kosong: live-build memperlakukannya sebagai
	# package-list tanpa isi dan bisa gagal.
	rm -f -- "$OUT"
	info "0 paket; $OUT tidak dibuat"
	exit 0
fi

mkdir -p -- "$(dirname -- "$OUT")"
cp -- "$WORK/packages.final" "$OUT"
info "$count paket -> $OUT"