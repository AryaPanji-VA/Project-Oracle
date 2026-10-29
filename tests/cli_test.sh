#!/usr/bin/env bash
# ============================================================================
# tests/cli_test.sh — uji logika CLI `oracle` di host
#
# Batas yang diakui: ini menguji LOGIKA CLI (validasi nama, pembacaan profile,
# pembentukan argv). Ini BUKAN uji pemasangan paket di sistem target — apt-get
# tidak dijalankan di sini. Uji runtime nyata hanya valid di dalam image
# ORACLE OS hasil build, yang belum ada.
#
# Jalankan: ./tests/cli_test.sh
# ============================================================================

set -uo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
CLI="${ROOT}/image/config/includes.chroot/usr/local/bin/oracle"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

pass=0; fail=0
ok()   { printf '  ok   %s\n' "$1"; pass=$((pass+1)); }
no()   { printf '  FAIL %s\n' "$1"; fail=$((fail+1)); }

# Fixture: profile dan conf palsu, supaya host tidak tersentuh.
mkdir -p "$TMP/profiles"
printf 'iproute2\ncurl\n' > "$TMP/profiles/networking.list"
printf '# profile uji\nnmap\n' > "$TMP/profiles/web-security.list"
cp "${ROOT}/config/oracle.conf" "$TMP/oracle.conf"

run() { ORACLE_CONF="$TMP/oracle.conf" ORACLE_PROFILE_DIR="$TMP/profiles" "$@"; }

echo "== CLI oracle: logika =="

out="$(run sh "$CLI" version 2>&1)"
[ "$out" = "ORACLE OS 0.1.0" ] && ok "version" || no "version -> '$out'"

out="$(run sh "$CLI" identity 2>&1)"
case "$out" in *"ID              : oracle"*) ok "identity: ID";;       *) no "identity: ID";; esac
case "$out" in *"trixie"*)                  ok "identity: trixie";;    *) no "identity: trixie";; esac
case "$out" in *"networking"*)              ok "identity: profile list";; *) no "identity: profile list";; esac

out="$(run sh "$CLI" profile list 2>&1)"
case "$out" in *networking*)   ok "profile list: networking";;  *) no "profile list: networking";; esac
case "$out" in *web-security*) ok "profile list: web-security";; *) no "profile list: web-security";; esac

out="$(run sh "$CLI" profile check networking 2>&1)"
case "$out" in *iproute2*) ok "profile check: isi paket";; *) no "profile check: isi paket -> $out";; esac

# --- Validasi input: harus MENOLAK, bukan menjalankan --------------------
for bad in '"; rm -rf /' '../../etc/passwd' 'net working' 'UPPER' 'a$(id)' '' ; do
	out="$(run sh "$CLI" profile check "$bad" 2>&1)"; rc=$?
	if [ "$rc" -ne 0 ]; then ok "tolak nama tidak valid: '$bad'"; else no "terima nama tidak valid: '$bad'"; fi
done

# Nama valid tapi profile tidak ada -> harus gagal, bukan diam.
out="$(run sh "$CLI" profile check tidak-ada 2>&1)"; rc=$?
[ "$rc" -ne 0 ] && ok "profile tidak ada ditolak" || no "profile tidak ada lolos"

# --- install tanpa root harus menolak -----------------------------------
if [ "$(id -u)" -ne 0 ]; then
	out="$(run sh "$CLI" profile install networking 2>&1)"; rc=$?
	if [ "$rc" -ne 0 ] && printf '%s' "$out" | grep -q administrator; then
		ok "install tanpa root ditolak"
	else
		no "install tanpa root tidak ditolak -> $out"
	fi
else
	echo "  skip install-tanpa-root (dijalankan sebagai root)"
fi

# --- perintah tidak dikenal ---------------------------------------------
run sh "$CLI" ngawur >/dev/null 2>&1; rc=$?
[ "$rc" -ne 0 ] && ok "perintah asing ditolak" || no "perintah asing lolos"

run sh "$CLI" profile >/dev/null 2>&1; rc=$?
[ "$rc" -ne 0 ] && ok "profile tanpa subperintah ditolak" || no "profile tanpa subperintah lolos"

echo
printf 'hasil: %d lulus, %d gagal\n' "$pass" "$fail"
[ "$fail" -eq 0 ]