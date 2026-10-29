#!/usr/bin/env bash
# ============================================================================
# tests/posix_test.sh — deteksi bashism pada berkas ber-shebang #!/bin/sh
#
# KENAPA TES INI ADA
# Di host Omarchy, /bin/sh adalah symlink ke bash. Akibatnya bashism lolos
# tanpa keluhan di semua uji lain. Di Debian, /bin/sh adalah dash, dan
# konstruksi bash akan gagal dengan "Bad substitution" atau "not found"
# TEPAT SAAT BUILD — momen paling mahal untuk menemukannya.
#
# KETERBATASAN YANG DIAKUI
# Tes ini STATIS. Ia mencari pola, bukan menjalankan dash. dash dan busybox
# tidak terpasang di host ini dan memasangnya butuh sudo. Jadi:
#   - Lolos tes ini = tidak ada pola bashism yang dikenal. BUKAN bukti bahwa
#     skrip benar-benar jalan di dash.
#   - Gagal tes ini = pasti ada masalah.
# Klaim "sudah diuji di dash" TIDAK boleh dibuat dari hasil tes ini.
#
# Jalankan: ./tests/posix_test.sh
# ============================================================================

set -uo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 1

pass=0; fail=0
ok() { printf '  ok   %s\n' "$1"; pass=$((pass+1)); }
no() { printf '  FAIL %s\n' "$1"; fail=$((fail+1)); }

# Kumpulkan semua berkas skrip yang diklaim POSIX (shebang #!/bin/sh).
mapfile -t FILES < <(
	grep -rl --include='*' -m1 '^#!/bin/sh$' . 2>/dev/null \
		| grep -v '^\./\.git/' \
		| sort
)

echo "== POSIX sh: berkas yang diperiksa =="
if [ "${#FILES[@]}" -eq 0 ]; then
	no "tidak ada berkas #!/bin/sh ditemukan — periksa pola pencarian"
else
	for f in "${FILES[@]}"; do printf '  %s\n' "$f"; done
fi
echo

# Pola bashism. Format: "label|regex ERE".
# Hati-hati: `[[` juga muncul di dalam kelas karakter regex seperti
# [[:space:]], jadi pola double-bracket harus mengecualikan `:` setelah `[[`.
PATTERNS=(
	'parameter case modification|\$\{[A-Za-z_][A-Za-z0-9_]*(\^\^|,,)'
	'double bracket test|(^|[^[:alnum:]_])\[\[([^:]|$)'
	'here-string|<<<'
	'function keyword|^[[:space:]]*function[[:space:]]'
	'array assignment|^[[:space:]]*[A-Za-z_][A-Za-z0-9_]*=\([[:space:]]*["\x27]'
	'process substitution|<\(|>\('
	'brace expansion sequence|\{[0-9]+\.\.[0-9]+\}'
	'$RANDOM|RANDOM'
	'source builtin|^[[:space:]]*source[[:space:]]'
)

echo "== Pemindaian bashism =="
for f in "${FILES[@]}"; do
	for entry in "${PATTERNS[@]}"; do
		label="${entry%%|*}"
		rx="${entry#*|}"
		# Abaikan baris komentar: penjelasan tentang bashism bukan bashism.
		# `grep -n` memberi awalan "N:", jadi pola komentar harus ikut itu.
		hit="$(grep -nE "$rx" "$f" 2>/dev/null | grep -vE '^[0-9]+:[[:space:]]*#' || true)"
		if [ -n "$hit" ]; then
			no "$f — $label"
			printf '%s\n' "$hit" | sed 's/^/         /'
		fi
	done
done

if [ "$fail" -eq 0 ]; then
	ok "tidak ada pola bashism pada ${#FILES[@]} berkas #!/bin/sh"
fi

echo
echo "== Perilaku yang diuji langsung (tidak butuh dash) =="

# Bukti konkret: nilai yang dihasilkan konversi uppercase harus benar.
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
ID="oracle"
got="$(printf '%s' "$ID" | tr 'a-z' 'A-Z')"
[ "$got" = "ORACLE" ] && ok "tr a-z A-Z: 'oracle' -> 'ORACLE'" || no "tr: '$got'"

ID="oracle-os-13"
got="$(printf '%s' "$ID" | tr 'a-z' 'A-Z')"
[ "$got" = "ORACLE-OS-13" ] && ok "tr a-z A-Z: tanda hubung & angka tetap" || no "tr: '$got'"

# auto/config harus benar-benar memakai ISO_VOLUME, bukan ${ID^^}.
# Diperiksa HANYA pada baris perintah, bukan komentar: komentar yang
# menjelaskan "${ID^^}" itu benar dan tidak boleh dianggap pelanggaran.
code_hit="$(
	awk '
		/^[[:space:]]*#/ { next }
		/\$\{[A-Za-z_][A-Za-z0-9_]*\^\^/ { print FNR": "$0 }
	' image/auto/config
)"
if [ -n "$code_hit" ]; then
	no "image/auto/config masih memakai \${ID^^} di kode"
	printf '%s\n' "$code_hit" | sed 's/^/         /'
else
	ok "image/auto/config tidak memakai \${ID^^} di kode"
fi
grep -q 'tr .a-z. .A-Z.' image/auto/config \
	&& ok "image/auto/config memakai tr untuk uppercase" \
	|| no "image/auto/config tidak memakai tr"

# Validasi ID: tolak nilai yang tidak aman untuk nama volume ISO.
for bad in 'Oracle OS' 'oracle_os' '../x' '' 'ORACLE'; do
	if printf '%s' "$bad" | grep -Eq '^[a-z0-9][a-z0-9-]*$'; then
		no "ID tidak valid lolos validasi: '$bad'"
	else
		ok "ID tidak valid ditolak: '$bad'"
	fi
done
for good in 'oracle' 'oracle-os' 'o13' 'a1-b2'; do
	if printf '%s' "$good" | grep -Eq '^[a-z0-9][a-z0-9-]*$'; then
		ok "ID valid diterima: '$good'"
	else
		no "ID valid ditolak: '$good'"
	fi
done

echo
printf 'hasil: %d lulus, %d gagal\n' "$pass" "$fail"
echo
echo "CATATAN: tes ini statis. Tidak ada eksekusi di bawah dash."
[ "$fail" -eq 0 ]