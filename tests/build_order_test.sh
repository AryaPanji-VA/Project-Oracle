#!/usr/bin/env bash
# ============================================================================
# tests/build_order_test.sh — uji URUTAN staging di scripts/build.sh
#
# KENAPA TES INI ADA
# `lb build` tanpa `lb config` sebelumnya gagal total di live-build. Bug itu
# tidak tertangkap tes mana pun karena tidak ada tes yang memeriksa urutan.
#
# CARA KERJA
# podman dipalsukan: ia mencatat setiap pemanggilan ke berkas log, dan
# MENIRU efek `lb config` sejauh yang bisa ditiru tanpa live-build asli:
# membuat config/binary, config/bootstrap, .build/, menulis
# config/package-lists/live.list.chroot bawaan, dan menaruh symlink hook.
# Tiruan itu sengaja "merusak" aset proyek (menimpa includes.chroot dan
# package-list) supaya terlihat apakah build.sh menulis ulang setelahnya.
#
# KETERBATASAN YANG DIAKUI
# Ini TIDAK menguji live-build. live-build tidak terpasang, podman tidak
# terpasang, dan ISO belum pernah dibangun. Yang diuji: urutan pemanggilan,
# dan bahwa aset proyek ditulis setelah tahap config sehingga tidak hilang.
# Klaim "build berhasil" tetap TIDAK boleh dibuat dari tes ini.
#
# Jalankan: ./tests/build_order_test.sh
# ============================================================================

set -uo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

pass=0; fail=0
ok() { printf '  ok   %s\n' "$1"; pass=$((pass+1)); }
no() { printf '  FAIL %s\n' "$1"; fail=$((fail+1)); }

echo "== build.sh: urutan lb config -> lb build =="

# --- Salinan repo di TMP: repo asli tidak disentuh -----------------------
cp -a "$ROOT" "$TMP/repo"
rm -rf "$TMP/repo/.git" "$TMP/repo/build"
REPO="$TMP/repo"
LOG="$TMP/calls.log"
: > "$LOG"

# --- podman palsu --------------------------------------------------------
mkdir -p "$TMP/bin"
cat > "$TMP/bin/podman" <<'FAKE'
#!/usr/bin/env bash
# podman palsu: catat panggilan, tiru efek lb config.
#
# Penting: `-w /work/build` adalah path DI DALAM container. Tiruan ini harus
# menerjemahkannya ke path host lewat FAKE_HOSTROOT, karena mount
# -v "$ORACLE_ROOT:/work" tidak benar-benar terjadi di sini.
LOG="${FAKE_LOG:?}"
HOSTROOT="${FAKE_HOSTROOT:?}"

CONTAINER_WORK=""
prev=""
for a in "$@"; do
	if [ "$prev" = "-w" ]; then CONTAINER_WORK="$a"; fi
	prev="$a"
done

# /work/... -> $HOSTROOT/...
WORK="${CONTAINER_WORK#/work}"
WORK="${HOSTROOT}${WORK}"

# Ambil subperintah: argumen terakhir setelah "/bin/sh -c '<cmd>'"
CMD=""
for a in "$@"; do
	case "$a" in
		"lb config"|"lb build") CMD="$a" ;;
	esac
done

printf '%s\n' "${CMD:-other}" >> "$LOG"

case "$CMD" in
	"lb config")
		# Tiru efek nyata `lb config`: populasi config/ dan .build/.
		mkdir -p "$WORK/config/binary" "$WORK/config/bootstrap" \
		         "$WORK/config/chroot" "$WORK/config/common" \
		         "$WORK/.build"

		# config/binary HARUS berupa file penanda, karena build.sh memeriksa
		# keberadaannya sebagai bukti tahap config selesai. Kalau tiruan ini
		# hanya membuat direktori kosong, guard build.sh akan salah menilai.
		printf 'boot=live\n' > "$WORK/config/binary"

		# Tiru perilaku yang BERBAHAYA dan paling merusak: live-build
		# menganggap config/ miliknya sendiri. Di sini `lb config` menghapus
		# SELURUH includes.chroot DAN SELURUH package-lists, termasuk paket
		# inti (oracle-core.list.chroot). Ini kasus terburuk, dan build.sh
		# harus mampu memulihkan keduanya.
		rm -rf "$WORK/config/includes.chroot"
		rm -rf "$WORK/config/package-lists"
		mkdir -p "$WORK/config/includes.chroot"
		mkdir -p "$WORK/config/package-lists"
		printf 'placeholder\n' > "$WORK/config/includes.chroot/PLACEHOLDER"

		# package-list bawaan live-build sendiri (bukan milik proyek).
		printf 'live-boot\n' > "$WORK/config/package-lists/live.list.chroot"

		# Tiru "P: Symlinking hooks...": hook proyek harus tetap ada.
		mkdir -p "$WORK/config/hooks/live"
		;;
	"lb build")
		# `lb build` mensyaratkan .build/ sudah ada (hasil lb config).
		if [ ! -d "$WORK/.build" ]; then
			echo "E: the following stage is required to be done first: config" >&2
			exit 1
		fi
		: > "$WORK/.build/build-done"
		# Kalau FAKE_NO_ISO=1, tiruan sengaja TIDAK menghasilkan ISO, supaya
		# bisa diuji apakah build.sh menolak mengklaim sukses.
		if [ "${FAKE_NO_ISO:-0}" != "1" ]; then
			printf 'fake iso\n' > "$WORK/$(printf 'oracle-%s-%s-amd64.hybrid.iso' \
				"$(sed -n 's/^VERSION="\(.*\)"/\1/p' "$HOSTROOT/config/oracle.conf")" \
				"$(sed -n 's/^DEBIAN_CODENAME="\(.*\)"/\1/p' "$HOSTROOT/config/oracle.conf")")"
		fi
		;;
esac
exit 0
FAKE
chmod +x "$TMP/bin/podman"

# sudo palsu: jalankan perintah apa adanya (jangan minta password).
cat > "$TMP/bin/sudo" <<'FAKE'
#!/usr/bin/env bash
exec "$@"
FAKE
chmod +x "$TMP/bin/sudo"

echo "  repo salinan: $REPO"
echo

# --- Jalankan build.sh dengan podman & sudo palsu -----------------------
export FAKE_LOG="$LOG"
export FAKE_HOSTROOT="$REPO"
export PATH="$TMP/bin:$PATH"
out="$(cd "$REPO" && ./scripts/build.sh 2>&1)"; rc=$?

[ "$rc" -eq 0 ] \
	&& ok "build.sh selesai tanpa error (dengan podman palsu)" \
	|| { no "build.sh gagal (exit $rc)"; printf '%s\n' "$out" | tail -15 | sed 's/^/         /'; }

# `build.sh` WAJIB menolak mengklaim sukses kalau tidak ada ISO.
echo
echo "== guard: tanpa ISO, build.sh harus GAGAL =="
rm -rf "$REPO/build"
: > "$LOG"
out_noiso="$(cd "$REPO" && FAKE_NO_ISO=1 ./scripts/build.sh 2>&1)"; rc_ni=$?
[ "$rc_ni" -ne 0 ] \
	&& ok "tanpa ISO: exit non-zero (exit $rc_ni)" \
	|| no "tanpa ISO: build.sh mengklaim sukses"
printf '%s' "$out_noiso" | grep -qi 'tanpa ISO\|GAGAL' \
	&& ok "tanpa ISO: pesan kegagalan eksplisit" \
	|| no "tanpa ISO: tidak ada pesan kegagalan"
printf '%s' "$out_noiso" | grep -qi 'selesai: ' \
	&& no "tanpa ISO: tetap mencetak 'selesai:'" \
	|| ok "tanpa ISO: tidak mencetak 'selesai:'"

# Kembalikan workspace ke hasil run pertama untuk pemeriksaan artefak.
rm -rf "$REPO/build"
: > "$LOG"
out="$(cd "$REPO" && ./scripts/build.sh 2>&1)"; rc=$?

# --- Guard tahap config: tanpa config/binary, build.sh harus berhenti ----
echo
echo "== guard: lb config tidak menghasilkan artefak -> build berhenti =="
if printf '#!/bin/sh\nexit 0\n' > "$TMP/bin/podman_noconfig"; then :; fi
# podman palsu yang MENGABAIKAN lb config (tidak membuat .build/config/binary)
mkdir -p "$TMP/bin2"
cat > "$TMP/bin2/podman" <<'FAKE2'
#!/usr/bin/env bash
LOG="${FAKE_LOG:?}"
HOSTROOT="${FAKE_HOSTROOT:?}"
CMD=""
for a in "$@"; do
	case "$a" in "lb config"|"lb build") CMD="$a" ;; esac
done
printf '%s\n' "${CMD:-other}" >> "$LOG"
if [ "$CMD" = "lb build" ]; then
	echo "[fake] lb build seharusnya tidak pernah sampai di sini" >&2
	exit 1
fi
exit 0    # lb config "sukses" tapi tidak menghasilkan apa pun
FAKE2
chmod +x "$TMP/bin2/podman"

rm -rf "$REPO/build"
: > "$LOG"
out_nc="$(cd "$REPO" && PATH="$TMP/bin2:$PATH" ./scripts/build.sh 2>&1)"; rc_nc=$?
[ "$rc_nc" -ne 0 ] && ok "lb config tanpa artefak: build.sh exit non-zero ($rc_nc)" \
	|| no "lb config tanpa artefak: build.sh melanjutkan (exit $rc_nc)"
printf '%s' "$out_nc" | grep -qi 'config.*GAGAL\|GAGAL.*config' \
	&& ok "lb config tanpa artefak: pesan menyebut tahap config gagal" \
	|| no "lb config tanpa artefak: pesan tidak jelas"
grep -q '^lb build$' "$LOG" && no "lb build dipanggil padahal config gagal" \
	|| ok "lb build TIDAK dipanggil saat config gagal"

# --- T-1: package-lists dihapus total oleh lb config -> pulih ----------
echo
echo "== T-1: lb config menghapus SELURUH package-lists -> harus dipulihkan =="
rm -rf "$REPO/build"
: > "$LOG"
# podman palsu yang membuat artefak config TAPI menghapus seluruh package-lists,
# termasuk oracle-core.list.chroot (paket inti). Ini kasus terburuk.
mkdir -p "$TMP/bin3"
cat > "$TMP/bin3/podman" <<'FAKE3'
#!/usr/bin/env bash
LOG="${FAKE_LOG:?}"; HOSTROOT="${FAKE_HOSTROOT:?}"
CONTAINER_WORK=""; prev=""
for a in "$@"; do [ "$prev" = "-w" ] && CONTAINER_WORK="$a"; prev="$a"; done
WORK="${HOSTROOT}${CONTAINER_WORK#/work}"
CMD=""
for a in "$@"; do case "$a" in "lb config"|"lb build") CMD="$a" ;; esac; done
printf '%s\n' "${CMD:-other}" >> "$LOG"
if [ "$CMD" = "lb config" ]; then
	mkdir -p "$WORK/.build"
	printf 'boot=live\n' > "$WORK/config/binary"
	# Hapus package-lists SELURUHNYA, termasuk oracle-core.
	rm -rf "$WORK/config/package-lists"
	mkdir -p "$WORK/config/package-lists"
	printf 'live-boot\n' > "$WORK/config/package-lists/live.list.chroot"
fi
exit 0
FAKE3
chmod +x "$TMP/bin3/podman"

out_pk="$(cd "$REPO" && PATH="$TMP/bin3:$PATH" ./scripts/build.sh 2>&1)"; rc_pk=$?

# Yang diharapkan: build.sh MEMULIHKAN oracle-core, bukan gagal.
if [ -s "$REPO/build/config/package-lists/oracle-core.list.chroot" ]; then
	ok "oracle-core.list.chroot dipulihkan setelah dihapus lb config"
	n_core="$(grep -c . "$REPO/build/config/package-lists/oracle-core.list.chroot" || true)"
	[ "$n_core" -ge 10 ] && ok "isi oracle-core utuh ($n_core paket)" \
		|| no "isi oracle-core hanya $n_core paket"
	grep -qx 'live-boot' "$REPO/build/config/package-lists/oracle-core.list.chroot" \
		&& ok "paket inti live-boot ada di daftar" || no "live-boot tidak ada di daftar"
	ok "build.sh tidak berhenti karena pemulihan berhasil (exit $rc_pk)"
else
	no "oracle-core.list.chroot TIDAK dipulihkan setelah lb config menghapusnya"
fi

# package-list bawaan live-build tidak boleh ikut terhapus oleh pemulihan.
# (build.sh menyalin dari image/, jadi live.list.chroot dari live-build tetap ada
#  karena cp tidak menghapus file yang tidak ada di sumber.)
[ -f "$REPO/build/config/package-lists/live.list.chroot" ] \
	&& ok "package-list bawaan live-build tetap ada" \
	|| no "package-list bawaan live-build hilang"

# Kembalikan workspace ke hasil run normal.
rm -rf "$REPO/build"
: > "$LOG"
out="$(cd "$REPO" && ./scripts/build.sh 2>&1)"; rc=$?

# --- Pemeriksaan urutan --------------------------------------------------
echo
echo "== urutan panggilan tercatat =="
sed 's/^/    /' "$LOG"

build_line="$(grep -n '^lb build$' "$LOG" | head -1 | cut -d: -f1)"
config_line="$(grep -n '^lb config$' "$LOG" | head -1 | cut -d: -f1)"

[ -n "$config_line" ] && ok "lb config dipanggil" || no "lb config TIDAK dipanggil"
[ -n "$build_line" ]  && ok "lb build dipanggil"  || no "lb build TIDAK dipanggil"

if [ -n "$config_line" ] && [ -n "$build_line" ]; then
	[ "$config_line" -lt "$build_line" ] \
		&& ok "lb config SEBELUM lb build (baris $config_line < $build_line)" \
		|| no "urutan salah: lb build (baris $build_line) mendahului lb config (baris $config_line)"
	[ "$(grep -c '^lb config$' "$LOG")" -eq 1 ] \
		&& ok "lb config dipanggil tepat sekali" \
		|| no "lb config dipanggil $(grep -c '^lb config$' "$LOG") kali"
fi

# --- Pemeriksaan artefak: aset proyek selamat dari tahap config ----------
echo
echo "== aset proyek setelah tahap config =="

B="$REPO/build"

[ -d "$B/.build" ] && ok ".build/ ada (tahap config benar-benar jalan)" || no ".build/ tidak ada"

[ -f "$B/config/includes.chroot/etc/oracle/oracle.conf" ] \
	&& ok "identitas ada: includes.chroot/etc/oracle/oracle.conf" \
	|| no "identitas HILANG setelah lb config"

[ -f "$B/config/includes.chroot/etc/oracle/profiles.conf" ] \
	&& ok "profiles.conf ada di image" || no "profiles.conf HILANG"

[ -f "$B/config/includes.chroot/usr/local/bin/oracle" ] \
	&& ok "CLI oracle ada di image" || no "CLI oracle HILANG setelah lb config"

[ -f "$B/config/includes.chroot/usr/share/oracle/profiles/networking.list" ] \
	&& ok "file profile ada di image" || no "file profile HILANG"

[ -x "$B/config/includes.chroot/usr/local/bin/oracle" ] \
	&& ok "CLI oracle executable" || no "CLI oracle tidak executable"

# placeholder dari podman palsu membuktikan lb config memang menimpa;
# keberadaan aset kita membuktikan kita menulis ulang sesudahnya.
if [ -f "$B/config/includes.chroot/PLACEHOLDER" ]; then
	ok "tiruan lb config menimpa includes.chroot, dan aset proyek tetap ditulis ulang sesudahnya"
else
	no "tiruan tidak berjalan seperti yang diharapkan (PLACEHOLDER tidak ada)"
fi

# Package-list: inti tetap ada, profile tidak dibuat karena pilihan kosong.
[ -f "$B/config/package-lists/oracle-core.list.chroot" ] \
	&& ok "package-list inti ada" || no "package-list inti HILANG"
[ -f "$B/config/package-lists/live.list.chroot" ] \
	&& ok "package-list bawaan live-build tetap ada" || no "package-list bawaan live-build hilang"

if [ -f "$B/config/package-lists/oracle-profiles.list.chroot" ]; then
	no "package-list profile dibuat padahal pilihan kosong"
else
	ok "pilihan kosong: package-list profile TIDAK dibuat (image minimal)"
fi

# --- Kasus kedua: profile dipilih -> package-list harus ada --------------
echo
echo "== ulangi dengan profile dipilih =="
rm -rf "$B"
: > "$LOG"
printf 'networking\n' > "$REPO/config/profiles.conf"

out2="$(cd "$REPO" && ./scripts/build.sh 2>&1)"; rc2=$?
[ "$rc2" -eq 0 ] && ok "build.sh jalan lagi dengan profile dipilih" \
	|| { no "build.sh gagal (exit $rc2)"; printf '%s\n' "$out2" | tail -10 | sed 's/^/         /'; }

if [ -f "$B/config/package-lists/oracle-profiles.list.chroot" ]; then
	ok "package-list profile dibuat setelah lb config"
	n="$(grep -c . "$B/config/package-lists/oracle-profiles.list.chroot" || true)"
	[ "$n" -eq 10 ] && ok "isi package-list profile: 10 paket" || no "isi package-list: $n paket (harus 10)"
	grep -qx 'network-manager' "$B/config/package-lists/oracle-profiles.list.chroot" \
		&& ok "paket pertama benar: network-manager" || no "isi package-list tidak sesuai"
else
	no "package-list profile TIDAK dibuat padahal profile dipilih"
fi

# Urutan tetap benar pada run kedua.
c2="$(grep -n '^lb config$' "$LOG" | head -1 | cut -d: -f1)"
b2="$(grep -n '^lb build$'  "$LOG" | head -1 | cut -d: -f1)"
[ -n "$c2" ] && [ -n "$b2" ] && [ "$c2" -lt "$b2" ] \
	&& ok "run kedua: lb config tetap sebelum lb build" || no "run kedua: urutan salah"

# --- Repo asli tidak berubah --------------------------------------------
echo
echo "== repo asli tidak tersentuh =="
[ ! -d "$ROOT/build" ] && ok "tidak ada build/ di repo asli" || no "build/ muncul di repo asli"
if git -C "$ROOT" rev-parse --git-dir >/dev/null 2>&1; then
	dirty="$(git -C "$ROOT" status --porcelain -- build tests/__nonexistent 2>/dev/null || true)"
	[ -z "$dirty" ] && ok "git status bersih untuk build/" || no "git status kotor: $dirty"
fi

echo
printf 'hasil: %d lulus, %d gagal\n' "$pass" "$fail"
echo
echo "CATATAN: live-build asli TIDAK dijalankan. Ini uji urutan + staging."
[ "$fail" -eq 0 ]