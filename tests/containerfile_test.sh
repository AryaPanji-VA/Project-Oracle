#!/usr/bin/env bash
# ============================================================================
# tests/containerfile_test.sh — uji statis image/Containerfile & mount policy
#
# KENAPA TES INI ADA
# Dua hal di proyek ini tidak bisa diuji dengan menjalankan build (butuh
# Podman rootful + jaringan + waktu lama), tetapi bisa diverifikasi secara
# statis dan itu sudah cukup untuk mencegah regresi:
#
#   1. Containerfile HARUS memeriksa hasil `apt-get update`.
#      `apt-get update` mengembalikan exit 0 walaupun SEMUA repo gagal.
#      Tanpa pemeriksaan tambahan, kegagalan jaringan lolos diam-diam.
#      Fakta ini sudah dibuktikan dengan `--network none` (lihat STATUS.md).
#
#   2. scripts/build.sh HARUS memasang repo read-only dan build/ read-write.
#      Itu guardrail terhadap salah tulis, bukan kontrol keamanan.
#
# KETERBATASAN
# Ini tes STATIS. Ia memeriksa teks konfigurasi, bukan perilaku runtime.
# Lulus tes ini TIDAK membuktikan image bisa dibangun.
#
# Jalankan: ./tests/containerfile_test.sh
# ============================================================================

set -uo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
CF="${ROOT}/image/Containerfile"
BS="${ROOT}/scripts/build.sh"

pass=0; fail=0
ok() { printf '  ok   %s\n' "$1"; pass=$((pass+1)); }
no() { printf '  FAIL %s\n' "$1"; fail=$((fail+1)); }

echo "== Containerfile: guard apt-get update =="

[ -f "$CF" ] && ok "Containerfile ada" || { no "Containerfile tidak ada"; exit 1; }

# 1. Harus ada pemeriksaan indeks SETELAH apt-get update.
if grep -qE 'apt-get update' "$CF"; then
	ok "memanggil apt-get update"
else
	no "tidak memanggil apt-get update"
fi

if grep -qE '/var/lib/apt/lists/\*_InRelease|_InRelease' "$CF"; then
	ok "memeriksa indeks *_InRelease setelah update"
else
	no "TIDAK memeriksa apakah indeks benar-benar terunduh"
fi

# 2. apt-get update tidak boleh langsung diikuti && apt-get install
#    tanpa pemeriksaan di antaranya.
if grep -qE 'apt-get update[[:space:]]*&&[[:space:]]*apt-get install' "$CF"; then
	no "apt-get update && install bersambung langsung (tanpa guard)"
else
	ok "apt-get update tidak langsung menyambung ke install"
fi

# 3. install harus tetap ada.
grep -qE 'apt-get install' "$CF" && ok "memanggil apt-get install" || no "apt-get install hilang"

# 4. Base image harus Debian 13.
grep -qE '^FROM debian:13' "$CF" && ok "FROM debian:13" || no "base image bukan debian:13"

# 5. Paket toolchain wajib ada.
for p in live-build debootstrap xorriso squashfs-tools; do
	grep -qE "^[[:space:]]+${p}\\\\$|^[[:space:]]+${p}[[:space:]]" "$CF" \
		&& ok "paket toolchain: $p" || no "paket toolchain hilang: $p"
done

echo
echo "== build.sh: mount policy =="

[ -f "$BS" ] && ok "build.sh ada" || { no "build.sh tidak ada"; exit 1; }

# 6. Repo harus read-only.
if grep -qE '\$\{ORACLE_ROOT\}:/work:ro' "$BS"; then
	ok "repo dipasang :ro (read-only)"
else
	no "repo TIDAK dipasang :ro"
fi

# 7. build/ harus read-write dan dipasang terpisah.
if grep -qE '\$\{BUILD_DIR\}:/work/build:rw' "$BS"; then
	ok "build/ dipasang :rw (read-write), terpisah"
else
	no "build/ tidak dipasang :rw secara terpisah"
fi

# 8. Harus ada tepat 2 mount per tahap (repo ro + build rw).
n_ro=$(grep -cE '\$\{ORACLE_ROOT\}:/work:ro' "$BS" || true)
n_rw=$(grep -cE '\$\{BUILD_DIR\}:/work/build:rw' "$BS" || true)
[ "$n_ro" -eq "$n_rw" ] && [ "$n_ro" -ge 2 ] \
	&& ok "mount konsisten di $n_ro tahap (ro==rw)" \
	|| no "mount tidak konsisten: ro=$n_ro rw=$n_rw"

# 9. Ketiga operasi Podman yang perlu jaringan harus memakai jalur host
#    yang sudah diverifikasi; jangan kembali ke bridge rootful yang gagal.
code_only_build="$(awk '!/^[[:space:]]*#/ { print }' "$BS")"
n_host_flags="$(printf '%s\n' "$code_only_build" | grep -c -- '--network=host' || true)"
n_podman_build="$(grep -cE '^[[:space:]]*\$PODMAN build ' "$BS" || true)"
n_podman_run="$(grep -cE '^[[:space:]]*\$PODMAN run ' "$BS" || true)"
[ "$n_host_flags" -eq 3 ] && [ "$n_podman_build" -eq 1 ] && [ "$n_podman_run" -eq 2 ] \
	&& ok "host network dipasang pada build builder dan dua tahap live-build" \
	|| no "network mode tidak konsisten: host=$n_host_flags build=$n_podman_build run=$n_podman_run"

# 10. Build privileged hanya boleh berjalan di VM, bukan bare metal.
grep -q 'systemd-detect-virt --vm' "$BS" \
	&& ok "build mewajibkan deteksi VM sebelum membersihkan workspace" \
	|| no "build tidak memeriksa VM sebelum operasi privileged"

# 11. Jangan ada lagi mount lama yang menulis repo.
if grep -qE '\$\{ORACLE_ROOT\}:/work:Z' "$BS"; then
	no "masih ada mount lama ':Z' tanpa :ro"
else
	ok "tidak ada mount lama ':Z' tanpa :ro"
fi

echo
echo "== build.sh: guard & validasi =="

# 12. set -euo pipefail wajib ada.
grep -q 'set -euo pipefail' "$BS" && ok "set -euo pipefail" || no "set -euo pipefail hilang"

# 13. Guard hasil lb config.
grep -q 'config/binary' "$BS" && ok "guard config/binary (bukti lb config)" \
	|| no "tidak ada guard config/binary"

# 14. Guard paket inti.
grep -q 'oracle-core.list.chroot' "$BS" && ok "guard oracle-core.list.chroot" \
	|| no "tidak ada guard oracle-core"

# 15. Validasi artefak ISO.
grep -q '\*.iso' "$BS" && ok "mencari artefak *.iso" || no "tidak mencari *.iso"
grep -q 'die "build selesai tanpa ISO' "$BS" && ok "gagal eksplisit bila ISO tidak ada" \
	|| no "tidak gagal eksplisit saat ISO tidak ada"

# 16. Tidak boleh ada rm -rf tanpa -- (perlindungan argumen aneh).
if grep -qE 'rm -rf (?!.*--)' "$BS" 2>/dev/null || grep -qE 'rm -rf [^-]' "$BS"; then
	no "rm -rf tanpa '--'"
else
	ok "rm -rf memakai '--'"
fi

echo
echo "== auto/config: POSIX & noauto =="
AC="${ROOT}/image/auto/config"

# Periksa hanya baris PERINTAH, bukan komentar: auto/config menjelaskan
# "${ID^^}" di komentar justru sebagai dokumentasi kenapa TIDAK memakainya.
code_only() { awk '/^[[:space:]]*#/ { next } { print FNR": "$0 }' "$1"; }

if code_only "$AC" | grep -qE 'lb config noauto'; then
	ok "auto/config memakai noauto di kode"
else
	no "noauto tidak ada di kode auto/config"
fi

bashism="$(code_only "$AC" | grep -E '\$\{[A-Za-z_]+\^\^\}' || true)"
if [ -n "$bashism" ]; then
	no "auto/config memakai bashism \${var^^} di kode"
	printf '%s\n' "$bashism" | sed 's/^/         /'
else
	ok "tidak ada bashism \${var^^} di kode auto/config"
fi

# "${@}" harus diteruskan agar argumen pemanggil tidak hilang.
if code_only "$AC" | grep -q '"\${@}"'; then
	ok 'auto/config meneruskan "${@}"'
else
	no 'auto/config tidak meneruskan "${@}"'
fi

echo
printf 'hasil: %d lulus, %d gagal\n' "$pass" "$fail"
echo
echo "CATATAN: tes statis. Tidak membuktikan image dapat dibangun."
[ "$fail" -eq 0 ]
