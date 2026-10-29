#!/usr/bin/env bash
# ============================================================================
# tests/cli_packages_test.sh — parser & validasi paket di CLI `oracle`
#
# Fokus: F-3 (spasi internal dihapus diam-diam) dan F-4 (nama paket tidak
# divalidasi sebelum apt dipanggil).
#
# CARA KERJA
# CLI dipanggil dengan ORACLE_CONF / ORACLE_PROFILE_DIR yang diarahkan ke
# fixture di TMP. apt-get dipalsukan: ia hanya mencatat argumennya, sehingga
# bisa dibuktikan apakah apt SEMPAT dipanggil atau tidak.
#
# KETERBATASAN
# Yang diuji adalah logika CLI di host. apt-get yang asli tidak dijalankan,
# paket tidak dipasang, dan pemasangan nyata di image ORACLE OS belum diuji.
#
# Jalankan: ./tests/cli_packages_test.sh
# ============================================================================

set -uo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
CLI="${ROOT}/image/config/includes.chroot/usr/local/bin/oracle"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

pass=0; fail=0
ok() { printf '  ok   %s\n' "$1"; pass=$((pass+1)); }
no() { printf '  FAIL %s\n' "$1"; fail=$((fail+1)); }

mkdir -p "$TMP/profiles" "$TMP/bin"
cp "${ROOT}/config/oracle.conf" "$TMP/oracle.conf"
APTLOG="$TMP/apt.log"

# apt-get palsu: catat, jangan pasang apa pun.
cat > "$TMP/bin/apt-get" <<'FAKE'
#!/usr/bin/env bash
printf 'apt-get' >> "${APT_LOG:?}"
for a in "$@"; do printf ' [%s]' "$a" >> "${APT_LOG:?}"; done
printf '\n' >> "${APT_LOG:?}"
exit "${FAKE_APT_RC:-0}"
FAKE
chmod +x "$TMP/bin/apt-get"

# id palsu yang melaporkan uid 0, supaya jalur install bisa diuji tanpa root.
cat > "$TMP/bin/id" <<'FAKE'
#!/usr/bin/env bash
if [ "$1" = "-u" ]; then echo 0; else /usr/bin/id "$@"; fi
FAKE
chmod +x "$TMP/bin/id"

run() { ORACLE_CONF="$TMP/oracle.conf" ORACLE_PROFILE_DIR="$TMP/profiles" \
        APT_LOG="$APTLOG" PATH="$TMP/bin:$PATH" "$@"; }

reset_apt() { : > "$APTLOG"; }

echo "== F-3: spasi internal tidak boleh dihapus =="

# ip route2 -> harus DITOLAK, bukan dirapikan menjadi iproute2
printf 'ip route2\nnmap\n' > "$TMP/profiles/spaced.list"
reset_apt
out="$(run sh "$CLI" profile check spaced 2>&1)"; rc=$?
[ "$rc" -ne 0 ] && ok "'ip route2' ditolak oleh check" || no "'ip route2' lolos check"
printf '%s' "$out" | grep -q 'ip route2' \
	&& ok "'ip route2' dilaporkan apa adanya (tidak diubah jadi iproute2)" \
	|| no "'ip route2' berubah bentuk -> $out"

# bad name
printf ' bad name \n' > "$TMP/profiles/badspace.list"
reset_apt
out="$(run sh "$CLI" profile check badspace 2>&1)"; rc=$?
[ "$rc" -ne 0 ] && ok "'bad name' ditolak" || no "'bad name' lolos"

# install juga harus menolak, dan apt TIDAK boleh dipanggil
reset_apt
out="$(run sh "$CLI" profile install spaced 2>&1)"; rc=$?
[ "$rc" -ne 0 ] && ok "install 'ip route2': exit non-zero" || no "install 'ip route2': lolos"
[ ! -s "$APTLOG" ] && ok "install 'ip route2': apt-get TIDAK dipanggil" \
	|| no "install 'ip route2': apt-get dipanggil -> $(cat "$APTLOG")"

echo
echo "== F-4: nama paket berbahaya ditolak sebelum apt =="

for bad in '$(id)' 'rm-rf/' 'bad name' 'UPPER' '../etc/passwd' 'pkg;rm -rf /'; do
	printf '%s\n' "$bad" > "$TMP/profiles/evil.list"
	reset_apt
	out="$(run sh "$CLI" profile check evil 2>&1)"; rc=$?
	if [ "$rc" -ne 0 ]; then ok "check menolak: '$bad'"; else no "check lolos: '$bad'"; fi
	printf '%s' "$out" | grep -q 'nama paket tidak valid' \
		&& ok "  pesan jelas untuk: '$bad'" || no "  pesan tidak jelas untuk: '$bad'"

	reset_apt
	out="$(run sh "$CLI" profile install evil 2>&1)"; rc=$?
	if [ "$rc" -ne 0 ]; then ok "  install menolak: '$bad'"; else no "  install lolos: '$bad'"; fi
	[ ! -s "$APTLOG" ] && ok "  apt-get TIDAK dipanggil: '$bad'" \
		|| no "  apt-get dipanggil: '$bad' -> $(cat "$APTLOG")"
done

echo
echo "== Input valid harus tetap berhasil =="

printf '# komentar\niproute2\nnmap\n\ncurl\n' > "$TMP/profiles/good.list"
reset_apt
out="$(run sh "$CLI" profile check good 2>&1)"; rc=$?
[ "$rc" -eq 0 ] && ok "check profil valid: exit 0" || no "check profil valid: exit $rc -> $out"
for p in iproute2 nmap curl; do
	printf '%s' "$out" | grep -q "  - $p" && ok "  check menampilkan: $p" || no "  check tidak menampilkan: $p"
done

# Nama paket Debian yang sah tapi mengandung + . - harus diterima.
printf 'g++\nlibssl-dev\npython3.11\nca-certificates\n' > "$TMP/profiles/chars.list"
out="$(run sh "$CLI" profile check chars 2>&1)"; rc=$?
[ "$rc" -eq 0 ] && ok "nama paket sah dengan + . - diterima" || no "nama paket sah ditolak: $out"

reset_apt
out="$(run sh "$CLI" profile install good 2>&1)"; rc=$?
[ "$rc" -eq 0 ] && ok "install profil valid: exit 0" || no "install profil valid: exit $rc -> $out"
[ -s "$APTLOG" ] && ok "install valid: apt-get dipanggil" || no "install valid: apt-get TIDAK dipanggil"
grep -q '\[iproute2\]' "$APTLOG" && ok "  apt menerima iproute2" || no "  apt tidak menerima iproute2"
grep -q '\[nmap\]'     "$APTLOG" && ok "  apt menerima nmap"     || no "  apt tidak menerima nmap"
grep -q '\[curl\]'     "$APTLOG" && ok "  apt menerima curl"     || no "  apt tidak menerima curl"

# apt gagal -> CLI harus gagal, bukan mengklaim sukses.
reset_apt
out="$(run sh -c "FAKE_APT_RC=100 sh '$CLI' profile install good" 2>&1)"; rc=$?
[ "$rc" -ne 0 ] && ok "apt gagal: CLI exit non-zero" || no "apt gagal: CLI mengklaim sukses"
printf '%s' "$out" | grep -q 'TIDAK terpasang penuh' \
	&& ok "apt gagal: pesan eksplisit" || no "apt gagal: pesan tidak jelas"

# Profil kosong (hanya komentar) -> ditolak, apt tidak dipanggil.
printf '# hanya komentar\n\n' > "$TMP/profiles/empty.list"
reset_apt
out="$(run sh "$CLI" profile install empty 2>&1)"; rc=$?
[ "$rc" -ne 0 ] && ok "profil kosong: install ditolak" || no "profil kosong: install lolos"
[ ! -s "$APTLOG" ] && ok "profil kosong: apt-get TIDAK dipanggil" || no "profil kosong: apt dipanggil"

echo
echo "== Konsistensi dengan generator =="
# Kasus yang sama harus memberi keputusan sama di gen-profile-list.sh dan CLI.
# Kedua konsumen membaca DIRECTORY berbeda, jadi fixture disiapkan di keduanya
# dengan isi identik — kalau tidak, kegagalan "profile tidak ada" akan
# tertukar dengan kegagalan validasi.
GEN="${ROOT}/scripts/gen-profile-list.sh"
mkdir -p "$TMP/genprof"

# Isi identik di kedua direktori.
printf 'iproute2\nnmap\n' > "$TMP/genprof/consok.list"
printf 'iproute2\nnmap\n' > "$TMP/profiles/consok.list"
printf 'ip route2\n'      > "$TMP/genprof/consbad.list"
printf 'ip route2\n'      > "$TMP/profiles/consbad.list"

for case in consok consbad; do
	printf '%s\n' "$case" > "$TMP/sel.conf"
	PROFILES_CONF="$TMP/sel.conf" PROFILE_DIR="$TMP/genprof" OUT="$TMP/gen-out.list" \
		sh "$GEN" >/dev/null 2>&1; grc=$?

	reset_apt
	run sh "$CLI" profile check "$case" >/dev/null 2>&1; crc=$?

	# Keputusan harus SAMA: keduanya terima, atau keduanya tolak.
	if { [ "$grc" -eq 0 ] && [ "$crc" -eq 0 ]; } || { [ "$grc" -ne 0 ] && [ "$crc" -ne 0 ]; }; then
		if [ "$grc" -eq 0 ]; then
			ok "generator & CLI sama-sama TERIMA '$case'"
		else
			ok "generator & CLI sama-sama TOLAK '$case'"
		fi
	else
		no "tidak konsisten untuk '$case' (gen=$grc cli=$crc)"
	fi
done

echo
printf 'hasil: %d lulus, %d gagal\n' "$pass" "$fail"
echo
echo "CATATAN: apt-get palsu. Tidak ada paket dipasang di host."
[ "$fail" -eq 0 ]