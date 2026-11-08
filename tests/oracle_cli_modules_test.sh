#!/bin/sh
# ============================================================================
# tests/oracle_cli_modules_test.sh — tes statis untuk `oracle status`,
# `oracle doctor`, dan `oracle lab`.
#
# Kenapa tes STATIS: modul-modul ini butuh root, network namespace, dan
# sistem hidup. Yang bisa diuji tanpa itu adalah hal-hal yang paling sering
# salah dan paling mahal kalau lolos:
#
#   1. POSIX compliance (dash, bukan bash) — Debian /bin/sh = dash.
#   2. Entry point modul terdaftar di CLI utama dan bisa dieksekusi.
#   3. Bug yang SUDAH PERNAH terjadi tidak kembali (regresi):
#      - `[ -w / ]` untuk deteksi read-only (false negative untuk non-root)
#      - `grep -qx` pada `ip netns list` (output punya " (id: N)")
#      - `ip route get` untuk cek isolasi (selalu sukses karena default route)
#      - `unshare --net=FILE` untuk masuk namespace (MERUSAK namespace)
#      - `/dev/tcp` untuk uji konektivitas (bashism, di dash selalu gagal)
#      - menulis state sebelum `mkdir` direktori state
# ============================================================================

set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BIN="$ROOT/image/config/includes.chroot/usr/local/bin/oracle"
LIB="$ROOT/image/config/includes.chroot/usr/local/lib/oracle"

pass=0
fail=0
ok()   { pass=$((pass+1)); printf '  ok   %s\n' "$*"; }
bad()  { fail=$((fail+1)); printf '  FAIL %s\n' "$*"; }
check(){ if eval "$2"; then ok "$1"; else bad "$1"; fi; }

# Kode tanpa komentar. PENTING: modul ini mendokumentasikan bug yang pernah
# terjadi di komentar (mis. "JANGAN pakai `unshare --net=FILE`"). Kalau
# pemindaian ikut membaca komentar, dokumentasi itu terbaca sebagai bug dan
# tes gagal pada kode yang benar. Semua pemindaian pola memakai ini.
code_only() {
	sed 's/[[:space:]]*#.*$//' "$1" 2>/dev/null | grep -v '^[[:space:]]*$'
}

echo "== Modul CLI ORACLE =="

# ---------------------------------------------------------------------------
echo "-- berkas ada dan executable"
# ---------------------------------------------------------------------------
for f in oracle-status oracle-doctor oracle-lab; do
	if [ -f "$LIB/$f" ]; then
		ok "$f ada"
	else
		bad "$f tidak ada"
		continue
	fi
	if [ -x "$LIB/$f" ]; then
		ok "$f executable"
	else
		bad "$f tidak executable (chmod +x)"
	fi
done

# ---------------------------------------------------------------------------
echo "-- terdaftar di CLI utama"
# ---------------------------------------------------------------------------
for f in status doctor lab; do
	if grep -qE "(^|[|[:space:]])$f([|)]|$)" "$BIN" 2>/dev/null; then
		ok "perintah '$f' ada di dispatch"
	else
		bad "perintah '$f' tidak terdaftar di dispatch CLI"
	fi
done

# ---------------------------------------------------------------------------
echo "-- help mencantumkan perintah baru"
# ---------------------------------------------------------------------------
help_out="$("$BIN" help 2>&1 || true)"
for c in "oracle status" "oracle doctor" "oracle lab"; do
	case "$help_out" in
		*"$c"*) ok "help menyebut '$c'" ;;
		*)      bad "help tidak menyebut '$c'" ;;
	esac
done

# ---------------------------------------------------------------------------
echo "-- POSIX sh (dash), bukan bash"
# ---------------------------------------------------------------------------
for f in "$LIB/oracle-status" "$LIB/oracle-doctor" "$LIB/oracle-lab"; do
	n="$(basename "$f")"
	# bashism yang paling berbahaya: [[ ]], /dev/tcp, local, function
	# Dipindai pada KODE saja, bukan komentar.
	#
	# Pemeriksaan `[[` memakai `grep -F` (fixed string), BUKAN regex. Di ERE
	# `[[` adalah awal bracket expression, bukan dua kurung siku literal —
	# pola regex untuk itu selalu salah cocok. Sebagai string literal, `[[ `
	# (dengan spasi) adalah bentuk bash yang sebenarnya.
	#
	# String itu disusun dari variabel, bukan ditulis langsung: berkas ini
	# sendiri diperiksa tests/posix_test.sh, yang memindai literal `[[`
	# sebagai bashism.
	_br='['
	if code_only "$f" | grep -qF "${_br}${_br} " \
	   || code_only "$f" | grep -qE '/dev/tcp|^[[:space:]]*local[[:space:]]|^[[:space:]]*function[[:space:]]'; then
		bad "$n memakai bashism"
	else
		ok "$n POSIX-compatible"
	fi
done

# ---------------------------------------------------------------------------
echo "-- REGRESI: bug yang sudah pernah terjadi"
# ---------------------------------------------------------------------------
# 1. Deteksi root read-only tidak boleh pakai `[ -w / ]`.
if code_only "$LIB/oracle-doctor" | grep -q '\[ -w / \]'; then
	bad "oracle-doctor memakai '[ -w / ]' (false negative untuk non-root)"
else
	ok "oracle-doctor tidak memakai '[ -w / ]'"
fi
# Harus memeriksa opsi mount sebagai gantinya.
if code_only "$LIB/oracle-doctor" | grep -q 'proc/mounts\|findmnt'; then
	ok "oracle-doctor memeriksa opsi mount untuk read-only"
else
	bad "oracle-doctor tidak memeriksa opsi mount"
fi

# 2. `ip netns list` tidak boleh dicocokkan dengan `grep -qx`.
if code_only "$LIB/oracle-lab" | grep -q 'netns list.*grep -qx'; then
	bad "oracle-lab memakai 'grep -qx' pada 'ip netns list' (selalu gagal)"
else
	ok "oracle-lab tidak memakai 'grep -qx' untuk 'ip netns list'"
fi

# 3. Isolasi tidak boleh diperiksa dengan `ip route get`.
if code_only "$LIB/oracle-lab" | grep -q "ip route get"; then
	bad "oracle-lab memakai 'ip route get' (selalu sukses, false positive)"
else
	ok "oracle-lab tidak memakai 'ip route get' untuk cek isolasi"
fi

# 4. `unshare --net=FILE` merusak namespace — tidak boleh dipakai.
if code_only "$LIB/oracle-lab" | grep -qE 'unshare[^|]*--net='; then
	bad "oracle-lab memakai 'unshare --net=' (MERUSAK namespace)"
else
	ok "oracle-lab tidak memakai 'unshare --net='"
fi

# 5. Uji konektivitas tidak boleh memakai /dev/tcp (bashism).
if code_only "$LIB/oracle-lab" | grep -q '/dev/tcp'; then
	bad "oracle-lab memakai /dev/tcp (bashism; di dash selalu gagal)"
else
	ok "oracle-lab tidak memakai /dev/tcp"
fi

# 6. State dir harus dibuat SEBELUM menulis state.
#    Cek: baris `mkdir -p "$STATE_DIR"` muncul sebelum penulisan state.
mkdir_line="$(grep -n 'mkdir -p "\$STATE_DIR"' "$LIB/oracle-lab" 2>/dev/null | head -1 | cut -d: -f1)"
write_line="$(grep -n 'STATE_FILE.tmp" || die' "$LIB/oracle-lab" 2>/dev/null | head -1 | cut -d: -f1)"
if [ -n "$mkdir_line" ] && [ -n "$write_line" ] && [ "$mkdir_line" -lt "$write_line" ]; then
	ok "state dir dibuat sebelum menulis state"
else
	bad "state dir mungkin ditulis sebelum dibuat (urutan salah)"
fi

# ---------------------------------------------------------------------------
echo "-- lab: perintah wajib ada"
# ---------------------------------------------------------------------------
for sub in do_start do_status do_stop _enter; do
	if grep -q "^$sub()" "$LIB/oracle-lab" 2>/dev/null; then
		ok "fungsi $sub ada"
	else
		bad "fungsi $sub tidak ada"
	fi
done

# ---------------------------------------------------------------------------
echo "-- lab: tidak mengubah host secara diam-diam"
# ---------------------------------------------------------------------------
# Tidak boleh ada NAT/iptables: lab sengaja tanpa jalan keluar.
if grep -qE 'iptables|nft |masquerade' "$LIB/oracle-lab" 2>/dev/null; then
	bad "oracle-lab mengubah firewall host (tidak boleh)"
else
	ok "oracle-lab tidak menyentuh firewall host"
fi
# Tidak boleh ada default route yang ditambahkan.
if grep -qE 'route add default|ip route add.*default' "$LIB/oracle-lab" 2>/dev/null; then
	bad "oracle-lab menambahkan default route (isolasi bocor)"
else
	ok "oracle-lab tidak menambahkan default route"
fi

# ---------------------------------------------------------------------------
echo "-- status: jujur, bukan menebak"
# ---------------------------------------------------------------------------
# `status` harus melaporkan bila lab tidak berjalan, bukan diam.
if grep -q 'tidak berjalan' "$LIB/oracle-status" 2>/dev/null; then
	ok "oracle-status melaporkan lab yang tidak berjalan"
else
	bad "oracle-status tidak melaporkan status lab"
fi

echo
if [ "$fail" -eq 0 ]; then
	printf 'hasil: %d lulus, 0 gagal\n' "$pass"
	exit 0
else
	printf 'hasil: %d lulus, %d gagal\n' "$pass" "$fail"
	exit 1
fi