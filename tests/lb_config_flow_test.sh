#!/usr/bin/env bash
# ============================================================================
# tests/lb_config_flow_test.sh — uji alur konfigurasi live-build
#
# Yang diuji adalah SEMANTIK yang didokumentasikan, bukan biner live-build.
# live-build tidak terpasang di host ini dan memasangnya butuh sudo, jadi
# `lb` di sini adalah tiruan yang meniru dua aturan dari Debian Live Manual:
#
#   1. §6.1.1 — `lb config` menjalankan `auto/config` secara otomatis
#      ("Each of these scripts is run automatically every time you run the
#       corresponding lb command").
#   2. §6.1.2 — parameter `noauto` menekan pemanggilan otomatis itu
#      ("A special noauto parameter is used here to suppress another call to
#       auto/config, thereby preventing infinite recursion").
#
# KETERBATASAN: kalau tiruan ini salah meniru live-build, tes bisa lulus
# padahal live-build asli berperilaku lain. Tes ini membuktikan KONSISTENSI
# berkas kita terhadap aturan yang didokumentasikan — bukan perilaku
# live-build yang sebenarnya.
#
# Jalankan: ./tests/lb_config_flow_test.sh
# ============================================================================

set -uo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

pass=0; fail=0
ok() { printf '  ok   %s\n' "$1"; pass=$((pass+1)); }
no() { printf '  FAIL %s\n' "$1"; fail=$((fail+1)); }

echo "== Alur konfigurasi live-build (tiruan semantik manual) =="

# --- lb palsu ------------------------------------------------------------
mkdir -p "$TMP/bin"
cat > "$TMP/bin/lb" <<'FAKE'
#!/bin/sh
# Tiruan `lb` sesuai Debian Live Manual 6.1.1 dan 6.1.2.
#   - subperintah `config` menjalankan ./auto/config bila ada dan executable,
#     KECUALI pemanggilan itu memuat argumen `noauto`.
#   - setiap pemanggilan dicatat ke $LB_LOG.
cmd="${1:-}"
[ $# -gt 0 ] && shift

case " $* " in
	*" noauto "*) NOAUTO=1 ;;
	*)            NOAUTO=0 ;;
esac

printf '%s|noauto=%s|args=%s\n' "$cmd" "$NOAUTO" "$*" >> "${LB_LOG:?}"

# Batas keras: rekursi tanpa henti harus gagal cepat, bukan menggantung.
COUNT="$(wc -l < "$LB_LOG")"
if [ "$COUNT" -gt 50 ]; then
	echo "[fake-lb] BATAS REKURSI TERLAMPAUI ($COUNT panggilan) — hampir pasti rekursi." >&2
	exit 9
fi

if [ "$cmd" = "config" ] && [ "$NOAUTO" = "0" ] && [ -x ./auto/config ]; then
	exec ./auto/config "$@"
fi

exit 0
FAKE
chmod +x "$TMP/bin/lb"

# --- Siapkan salinan auto/config yang bisa jalan tanpa container ---------
cp -a "$ROOT/image" "$TMP/image"
sed -e "s#\${ORACLE_ROOT}/config/oracle.conf#$ROOT/config/oracle.conf#" \
	"$ROOT/image/auto/config" > "$TMP/image/auto/config"
chmod +x "$TMP/image/auto/config"

export LB_LOG="$TMP/lb.log"
export PATH="$TMP/bin:$PATH"
export ORACLE_ROOT="$ROOT"
export LB_NO_ENV_WARN=1

cd "$TMP/image" || exit 1

# === T-1: auto/config memakai noauto ===
echo
echo "-- auto/config memakai noauto --"
if grep -Eq 'lb[[:space:]]+config[[:space:]]+noauto' "$ROOT/image/auto/config"; then
	ok "auto/config memanggil 'lb config noauto'"
else
	no "auto/config TIDAK memakai noauto -> rekursi tak terbatas"
fi

if grep -q '"\${@}"' "$ROOT/image/auto/config"; then
	ok "auto/config meneruskan \"\${@}\""
else
	no "auto/config tidak meneruskan \"\${@}\" (argumen pemanggil hilang)"
fi

# === T-2: pemanggilan tunggal, tanpa rekursi ============================
echo
echo "-- tidak ada rekursi --"
: > "$LB_LOG"
timeout 20 sh -c './auto/config' >"$TMP/out.txt" 2>"$TMP/err.txt"; rc=$?

[ "$rc" -ne 124 ] && ok "tidak menggantung (exit $rc)" || no "auto/config menggantung (timeout)"
[ "$rc" -ne 9 ]   && ok "tidak menembus batas rekursi" || no "rekursi terdeteksi (batas 50 panggilan)"

calls="$(wc -l < "$LB_LOG" | tr -d ' ')"
[ "$calls" -eq 1 ] && ok "tepat 1 pemanggilan lb config (tercatat: $calls)" \
	|| { no "pemanggilan lb config: $calls (harus 1)"; sed 's/^/         /' "$LB_LOG"; }

# === T-3: pemanggilan dari build.sh (lb config tanpa argumen) ==========
echo
echo "-- interaksi build.sh -> lb config -> auto/config --"
: > "$LB_LOG"
timeout 20 sh -c 'lb config' >"$TMP/out2.txt" 2>"$TMP/err2.txt"; rc=$?
[ "$rc" -eq 0 ] && ok "lb config dari luar selesai (exit 0)" || no "lb config exit $rc"

total="$(wc -l < "$LB_LOG" | tr -d ' ')"
[ "$total" -eq 2 ] && ok "2 panggilan tercatat: luar + dalam (bukan rekursi)" \
	|| { no "panggilan tercatat: $total (harus 2)"; sed 's/^/         /' "$LB_LOG"; }

# Panggilan pertama tanpa noauto (dari build.sh), kedua dengan noauto.
first_noauto="$(sed -n '1p' "$LB_LOG" | cut -d'|' -f2)"
second_noauto="$(sed -n '2p' "$LB_LOG" | cut -d'|' -f2)"
[ "$first_noauto" = "noauto=0" ]  && ok "panggilan luar tanpa noauto (sesuai desain)" || no "panggilan luar: $first_noauto"
[ "$second_noauto" = "noauto=1" ] && ok "panggilan dalam memakai noauto (rekursi terhenti)" || no "panggilan dalam: $second_noauto"

# === T-4: argumen diteruskan ============================================
echo
echo "-- argumen diteruskan --"
: > "$LB_LOG"
timeout 20 sh -c 'lb config --verbose' >/dev/null 2>&1; rc=$?
inner="$(grep 'noauto=1' "$LB_LOG" | tail -1)"
case "$inner" in
	*--verbose*) ok "argumen luar (--verbose) sampai ke pemanggilan dalam" ;;
	*)           no "argumen luar hilang di pemanggilan dalam -> $inner" ;;
esac

# === T-5: build.sh TIDAK menambah flag lb config sendiri ================
echo
echo "-- build.sh tidak memegang flag konfigurasi --"
# Periksa secara POSITIF dan PRESIS, bukan grep longgar. Teks di dalam pesan
# error multi-baris juga menyebut "lb config", dan itu dokumentasi, bukan
# perintah. Yang dicari hanya baris yang BERAWALAN perintah lb:
#   ^<spasi>lb config   -> perintah dengan flag (dilarang di build.sh)
cmd_hit="$(grep -nE '^[[:space:]]*lb config' "$ROOT/scripts/build.sh" || true)"
if [ -n "$cmd_hit" ]; then
	no "build.sh memanggil 'lb config' langsung dengan flag (dua pemilik konfigurasi)"
	printf '%s\n' "$cmd_hit" | sed 's/^/         /'
else
	ok "build.sh tidak memanggil 'lb config' langsung (flag hanya di auto/config)"
fi

# Satu-satunya pemanggilan harus bentuk polos di dalam container.
n_polos="$(grep -cF "sh -c 'lb config'" "$ROOT/scripts/build.sh" || true)"
[ "$n_polos" -eq 1 ] && ok "tepat 1 pemanggilan: /bin/sh -c 'lb config' (polos)" \
	|| no "jumlah pemanggilan polos: $n_polos (harus 1)"

# === T-6: guard build.sh memakai artefak lb config, bukan config/ ======
echo
echo "-- guard tahap config --"
grep -q 'config/binary' "$ROOT/scripts/build.sh" \
	&& ok "guard memeriksa config/binary" \
	|| no "guard tidak memeriksa config/binary"
grep -q '\[ -d "${BUILD_DIR}/config" \] || die' "$ROOT/scripts/build.sh" \
	&& no "masih ada guard 'config/' yang selalu benar" \
	|| ok "guard 'config/' yang selalu benar sudah diganti"
# .build/ adalah asumsi; tidak boleh dijadikan syarat gagal.
if grep -q 'if \[ ! -d "${BUILD_DIR}/.build" \]; then' "$ROOT/scripts/build.sh"; then
	no ".build/ dijadikan syarat gagal (asumsi, bukan fakta terdokumentasi)"
else
	ok ".build/ tidak dijadikan syarat gagal (hanya informatif)"
fi

# === T-7: build.sh memulihkan seluruh package-lists =====================
echo
echo "-- pemulihan package-lists --"
grep -Eq 'cp -a.*SOURCE_DIR}/config/package-lists' "$ROOT/scripts/build.sh" \
	&& ok "build.sh menyalin ulang seluruh config/package-lists" \
	|| no "build.sh tidak memulihkan package-lists (hanya oracle-core?)"
grep -q 'oracle-core.list.chroot' "$ROOT/scripts/build.sh" \
	&& ok "build.sh memverifikasi oracle-core.list.chroot" \
	|| no "build.sh tidak memverifikasi paket inti"

echo
printf 'hasil: %d lulus, %d gagal\n' "$pass" "$fail"
echo
echo "CATATAN: lb adalah tiruan semantik manual. Perilaku live-build asli"
echo "         TIDAK terbukti oleh tes ini."
[ "$fail" -eq 0 ]