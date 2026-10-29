#!/usr/bin/env bash
# ============================================================================
# tests/profile_list_test.sh — uji scripts/gen-profile-list.sh
#
# Uji ini murni logika: membaca file profile, memvalidasi, merakit package-list.
# Tidak ada apt, tidak ada live-build, tidak ada ISO.
#
# Cakupan yang diminta:
#   1. profile kosong        -> tidak ada file keluaran, exit 0
#   2. profile valid         -> paket keluar benar, duplikat dibuang
#   3. profile tidak valid   -> exit 1, tidak ada file keluaran
#   4. input berbahaya       -> exit 1, tidak ada path traversal / eksekusi
#
# Jalankan: ./tests/profile_list_test.sh
# ============================================================================

set -uo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
GEN="${ROOT}/scripts/gen-profile-list.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

pass=0; fail=0
ok() { printf '  ok   %s\n' "$1"; pass=$((pass+1)); }
no() { printf '  FAIL %s\n' "$1"; fail=$((fail+1)); }

# Fixture: dua profile, salah satunya berbagi paket dengan yang lain.
mkdir -p "$TMP/profiles"
printf '# networking\niproute2\ncurl\nnmap\n' > "$TMP/profiles/networking.list"
printf '# web\nnmap\nnikto\n'                > "$TMP/profiles/web-security.list"

run_gen() {
	PROFILES_CONF="$1" PROFILE_DIR="$TMP/profiles" OUT="$2" sh "$GEN"
}

echo "== gen-profile-list =="

# --- 1. Profile kosong ---------------------------------------------------
printf '# hanya komentar\n\n   \n' > "$TMP/empty.conf"
out="$(run_gen "$TMP/empty.conf" "$TMP/out-empty.list" 2>&1)"; rc=$?
[ "$rc" -eq 0 ] && ok "kosong: exit 0" || no "kosong: exit $rc"
[ ! -e "$TMP/out-empty.list" ] && ok "kosong: file tidak dibuat" || no "kosong: file dibuat padahal kosong"
case "$out" in *"image minimal"*) ok "kosong: pesan image minimal";; *) no "kosong: pesan -> $out";; esac

# File konfirmasi yang benar-benar kosong (0 byte) juga harus aman.
: > "$TMP/zero.conf"
run_gen "$TMP/zero.conf" "$TMP/out-zero.list" >/dev/null 2>&1; rc=$?
[ "$rc" -eq 0 ] && [ ! -e "$TMP/out-zero.list" ] && ok "conf 0 byte: exit 0, tanpa file" \
	|| no "conf 0 byte: rc=$rc"

# --- 2. Profile valid ----------------------------------------------------
printf 'networking\n' > "$TMP/one.conf"
run_gen "$TMP/one.conf" "$TMP/out-one.list" >/dev/null 2>&1; rc=$?
[ "$rc" -eq 0 ] && ok "valid: exit 0" || no "valid: exit $rc"
if [ -f "$TMP/out-one.list" ]; then
	content="$(cat "$TMP/out-one.list")"
	[ "$content" = "$(printf 'iproute2\ncurl\nnmap')" ] && ok "valid: isi paket benar" \
		|| no "valid: isi -> $(echo "$content" | tr '\n' ' ')"
else
	no "valid: file tidak dibuat"
fi

# Dua profile dengan paket beririsan -> duplikat harus dibuang, urutan tetap.
printf 'networking\nweb-security\n' > "$TMP/two.conf"
run_gen "$TMP/two.conf" "$TMP/out-two.list" >/dev/null 2>&1; rc=$?
[ "$rc" -eq 0 ] && ok "dua profile: exit 0" || no "dua profile: exit $rc"
if [ -f "$TMP/out-two.list" ]; then
	content="$(cat "$TMP/out-two.list")"
	[ "$content" = "$(printf 'iproute2\ncurl\nnmap\nnikto')" ] && ok "dua profile: duplikat dibuang, urutan tetap" \
		|| no "dua profile: isi -> $(echo "$content" | tr '\n' ' ')"
	[ "$(grep -c '^nmap$' "$TMP/out-two.list")" -eq 1 ] && ok "dua profile: nmap hanya sekali" \
		|| no "dua profile: nmap dobel"
else
	no "dua profile: file tidak dibuat"
fi

# Tanpa OUT -> cetak ke stdout.
printf 'networking\n' > "$TMP/one.conf"
out="$(PROFILES_CONF="$TMP/one.conf" PROFILE_DIR="$TMP/profiles" sh "$GEN" 2>/dev/null)"
[ "$out" = "$(printf 'iproute2\ncurl\nnmap')" ] && ok "stdout mode: isi benar" \
	|| no "stdout mode: -> $out"

# --- 3. Profile tidak valid ---------------------------------------------
# Nama valid tapi file tidak ada.
printf 'tidak-ada\n' > "$TMP/missing.conf"
run_gen "$TMP/missing.conf" "$TMP/out-missing.list" >/dev/null 2>&1; rc=$?
[ "$rc" -ne 0 ] && ok "profile hilang: exit non-zero" || no "profile hilang: lolos"
[ ! -e "$TMP/out-missing.list" ] && ok "profile hilang: tanpa file setengah jadi" \
	|| no "profile hilang: meninggalkan file"

# profile dir tidak ada.
PROFILES_CONF="$TMP/one.conf" PROFILE_DIR="$TMP/nope" OUT="$TMP/x.list" sh "$GEN" >/dev/null 2>&1; rc=$?
[ "$rc" -ne 0 ] && ok "PROFILE_DIR hilang: exit non-zero" || no "PROFILE_DIR hilang: lolos"

# PROFILES_CONF tidak ada.
PROFILES_CONF="$TMP/nope.conf" PROFILE_DIR="$TMP/profiles" OUT="$TMP/y.list" sh "$GEN" >/dev/null 2>&1; rc=$?
[ "$rc" -ne 0 ] && ok "PROFILES_CONF hilang: exit non-zero" || no "PROFILES_CONF hilang: lolos"

# Nama paket tidak valid di dalam file profile.
mkdir -p "$TMP/badprofiles"
printf 'iproute2\n$(id)\n' > "$TMP/badprofiles/inject.list"
printf 'inject\n' > "$TMP/inject.conf"
PROFILES_CONF="$TMP/inject.conf" PROFILE_DIR="$TMP/badprofiles" OUT="$TMP/out-inject.list" \
	sh "$GEN" >/dev/null 2>&1; rc=$?
[ "$rc" -ne 0 ] && ok "nama paket berbahaya: exit non-zero" || no "nama paket berbahaya: lolos"
[ ! -e "$TMP/out-inject.list" ] && ok "nama paket berbahaya: tanpa file" || no "nama paket berbahaya: ada file"

# --- 4. Input berbahaya --------------------------------------------------
for bad in '../../etc/passwd' 'net working' 'UPPER' 'a$(id)' 'x;rm -rf /' '../networking'; do
	printf '%s\n' "$bad" > "$TMP/bad.conf"
	run_gen "$TMP/bad.conf" "$TMP/out-bad.list" >/dev/null 2>&1; rc=$?
	if [ "$rc" -ne 0 ]; then ok "tolak nama berbahaya: '$bad'"; else no "terima nama berbahaya: '$bad'"; fi
	rm -f "$TMP/out-bad.list"
done

# Path traversal: nama yang lolos validasi tidak boleh keluar dari PROFILE_DIR.
printf '../networking\n' > "$TMP/trav.conf"
run_gen "$TMP/trav.conf" "$TMP/out-trav.list" >/dev/null 2>&1; rc=$?
[ "$rc" -ne 0 ] && ok "path traversal ditolak" || no "path traversal lolos"

# Tidak boleh ada file yang tercipta di luar TMP karena injeksi.
[ ! -e "${ROOT}/config/package-lists" ] && ok "tidak ada direktori liar di repo" \
	|| no "ada direktori liar di repo"

# --- Idempoten -----------------------------------------------------------
printf 'networking\n' > "$TMP/one.conf"
run_gen "$TMP/one.conf" "$TMP/out-idem.list" >/dev/null 2>&1
run_gen "$TMP/one.conf" "$TMP/out-idem.list" >/dev/null 2>&1
[ "$(wc -l < "$TMP/out-idem.list")" -eq 3 ] && ok "idempoten: 3 baris, tidak menumpuk" \
	|| no "idempoten: $(wc -l < "$TMP/out-idem.list") baris"

echo
printf 'hasil: %d lulus, %d gagal\n' "$pass" "$fail"
[ "$fail" -eq 0 ]