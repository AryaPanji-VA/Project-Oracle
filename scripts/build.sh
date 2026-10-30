#!/usr/bin/env bash
# ============================================================================
# scripts/build.sh — pembungkus build + uji ORACLE OS
#
# Aturan yang dipegang:
#   1. Host tidak diubah selain pemasangan podman/qemu (diminta terpisah).
#   2. `config/` milik proyek tidak pernah tertimpa: live-build menulis folder
#      `config/`, `binary/`, `chroot/`, `cache/` di direktori kerjanya, jadi ia
#      dijalankan di build/ (gitignored), bukan di root repo.
#   3. Tidak pernah melaporkan sukses tanpa artefak ISO di disk.
#
# Pemakaian:
#   ./scripts/build.sh --check    cek prasyarat saja
#   ./scripts/build.sh            build ISO
#   ./scripts/build.sh --test     boot ISO di QEMU (butuh ISO hasil build)
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ORACLE_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
export ORACLE_ROOT

BUILD_DIR="${ORACLE_ROOT}/build"
SOURCE_DIR="${ORACLE_ROOT}/image"
BUILDER_IMAGE="oracle-builder:13"

# shellcheck disable=SC1091
. "${ORACLE_ROOT}/config/oracle.conf"

log()  { printf '\033[1;34m[oracle]\033[0m %s\n' "$*"; }
die()  { printf '\033[1;31m[oracle] ERROR:\033[0m %s\n' "$*" >&2; exit 1; }

# Podman ROOTFUL (sudo). Alasan tercatat di docs/STATUS.md (B-2, B-3):
# di rootless, --privileged tidak memberi CAP_SYS_ADMIN ke UID non-0 dan
# pemetaan UID menghalangi bind mount, sehingga `lb build` gagal saat mount.
# Host network dipakai karena uji rootful bridge gagal DNS/TCP, sedangkan
# image yang sama berhasil dengan --network=host. Trade-off akses jaringan
# host dicatat di docs/ARCHITECTURE.md.
PODMAN="sudo podman"

preflight() {
	command -v podman >/dev/null 2>&1 || die "podman belum terpasang.
  Pasang:  sudo pacman -S podman
  Cek:     podman info"
	command -v sudo >/dev/null 2>&1 || die "sudo tidak tersedia, tetapi build butuh 'sudo podman'."

	[ -f "${SOURCE_DIR}/auto/config" ]   || die "sumber build tidak lengkap: image/auto/config hilang"
	[ -d "${SOURCE_DIR}/config" ]        || die "sumber build tidak lengkap: image/config/ hilang"
	[ -f "${SOURCE_DIR}/Containerfile" ] || die "sumber build tidak lengkap: image/Containerfile hilang"

	log "prasyarat dasar OK"
	log "  identitas : ${NAME} ${VERSION} (${BASE} ${DEBIAN_RELEASE} ${DEBIAN_CODENAME})"
	log "  builder   : ${BUILDER_IMAGE} (podman rootful, host network)"
	if ! command -v qemu-system-x86_64 >/dev/null 2>&1; then
		log "  catatan   : qemu belum ada — build bisa jalan, uji boot belum"
	fi
}

require_build_vm() {
	local virt
	virt="$(systemd-detect-virt --vm 2>/dev/null || true)"
	[ -n "$virt" ] && [ "$virt" != "none" ] || die "build privileged ditolak di bare metal.
  Jalankan di VM sementara tanpa disk fisik host terpasang.
  --check tetap bisa dipakai untuk memeriksa prasyarat dasar."
	log "  VM build : ${virt}"
}

qemu_test() {
	local iso
	iso="$(find "${BUILD_DIR}" -maxdepth 1 -name '*.iso' -type f -print -quit 2>/dev/null || true)"
	[ -n "${iso}" ] || die "tidak ada ISO di ${BUILD_DIR}. Build dulu: ./scripts/build.sh"
	command -v qemu-system-x86_64 >/dev/null 2>&1 || die "qemu belum terpasang.
  Pasang:  sudo pacman -S qemu-base"

	[ -e /dev/kvm ] || log "peringatan: /dev/kvm tidak ada, boot lambat (mode TCG)"

	log "boot ${iso} di QEMU — keluar: Ctrl+A lalu X"
	log "  isolasi: jaringan user-mode, tidak ada disk fisik dipasang"
	exec qemu-system-x86_64 \
		-m 2048 -smp 2 \
		-cdrom "${iso}" \
		-boot d \
		-netdev user,id=n0 \
		-device virtio-net-pci,netdev=n0
}

case "${1:-}" in
	--check) preflight; log "mode --check: tidak ada yang dibangun."; exit 0 ;;
	--test)  qemu_test ;;
	"")      ;;
	*)       die "argumen tidak dikenal: $1 (pakai: --check | --test | kosong)" ;;
esac

preflight
require_build_vm

# ---------------------------------------------------------------------------
# Workspace bersih. build/ adalah artefak yang bisa dibuat ulang, jadi
# menghapusnya aman. Sisa build lama = sumber bug paling membingungkan
# ("kok hasilnya sama padahal sudah diubah?").
# ---------------------------------------------------------------------------
if [ -d "${BUILD_DIR}" ]; then
	[ "${BUILD_DIR}" = "${ORACLE_ROOT}/build" ] || die "menolak membersihkan path di luar workspace build: ${BUILD_DIR}"
	[ -e "${ORACLE_ROOT}/.git" ] || die "menolak membersihkan build/ karena root Git tidak terverifikasi: ${ORACLE_ROOT}"
	[ ! -L "${BUILD_DIR}" ] || die "menolak membersihkan build/ yang berupa symlink"
	log "menghapus seluruh workspace build lama: ${BUILD_DIR}"
	sudo rm -rf -- "${BUILD_DIR}"
fi
mkdir -p -- "${BUILD_DIR}"

log "menyalin sumber image/ -> build/"
cp -a -- "${SOURCE_DIR}/." "${BUILD_DIR}/"

chmod +x "${BUILD_DIR}/auto/config"

# ---------------------------------------------------------------------------
# Image builder: sekali bangun, dipakai berulang.
# ---------------------------------------------------------------------------
if ! $PODMAN image exists "${BUILDER_IMAGE}" 2>/dev/null; then
	log "membangun builder ${BUILDER_IMAGE} (sekali saja, butuh jaringan)"
	$PODMAN build --network=host -t "${BUILDER_IMAGE}" -f "${SOURCE_DIR}/Containerfile" "${SOURCE_DIR}"
else
	log "builder ${BUILDER_IMAGE} sudah ada"
fi

# ---------------------------------------------------------------------------
# TAHAP 1 — `lb config`
#
# `lb build` TIDAK berdiri sendiri. Tanpa `lb config` lebih dulu, live-build
# berhenti dengan:
#     E: the following stage is required to be done first: config
#
# Pemanggilan ini TANPA argumen: seluruh opsi lb config dimiliki oleh
# image/auto/config, yang dijalankan otomatis oleh `lb config`. auto/config
# memakai `noauto` sehingga konfigurasi hanya terjadi sekali, bukan rekursif.
# Jangan menambah flag di sini — itu membuat dua pemilik konfigurasi.
#
# MOUNT (kedua tahap sama):
#   /work       :ro   -> repo hanya DIBACA. build.sh terbukti hanya menulis
#                       ke build/; image/ tidak pernah ditulis.
#   /work/build :rw   -> satu-satunya jalur tulis. Dipasang terpisah karena
#                       submount tidak ikut aturan :ro induknya.
# Ini GUARDRAIL terhadap salah tulis, bukan kontrol keamanan: di container
# --privileged, CAP_SYS_ADMIN cukup untuk `mount -o remount,rw`. Lihat
# docs/ARCHITECTURE.md bagian "Blast radius".
# ---------------------------------------------------------------------------
log "tahap 1/2: lb config (menyiapkan config/ untuk live-build)"
$PODMAN run --rm -it \
	--network=host \
	--privileged \
	--userns=host \
	-v "${ORACLE_ROOT}:/work:ro,Z" \
	-v "${BUILD_DIR}:/work/build:rw,Z" \
	-e ORACLE_ROOT=/work \
	-e HOME=/root \
	-w /work/build \
	"${BUILDER_IMAGE}" \
	/bin/sh -c 'lb config'

# ---------------------------------------------------------------------------
# Bukti tahap config selesai — JANGAN pakai `config/` sebagai penanda.
#
# build/config SUDAH ADA sebelum lb config, karena `cp -a image/. build/`
# menyalin image/config beserta isinya. Memeriksa `config/` karenanya tidak
# membuktikan apa pun.
#
# Yang dipakai sebagai penanda HANYA yang tersurat di dokumentasi:
#   lb_config(1) menyebut config/ berisi berkas
#   config/{binary,bootstrap,chroot,common,source} yang dihasilkan lb config.
# `config/binary` karenanya bukti sah.
#
# `.build/` TIDAK dipakai sebagai syarat gagal. Keberadaannya adalah asumsi
# (direktori internal live-build, tidak dijamin oleh manpage). Menjadikannya
# syarat bisa membuat build yang sebenarnya benar ikut berhenti. Kalau ada,
# dicatat; kalau tidak ada, hanya peringatan.
# ---------------------------------------------------------------------------
if [ ! -e "${BUILD_DIR}/config/binary" ]; then
	die "tahap 'lb config' GAGAL: ${BUILD_DIR}/config/binary tidak ada.

  Berkas itu dihasilkan oleh 'lb config' (lb_config(1) menyebut
  config/{binary,bootstrap,chroot,common,source} sebagai berkas konfigurasi
  yang dibuatnya). Direktori config/ sendiri TIDAK bisa dipakai sebagai bukti,
  karena sudah ada sejak image/ disalin.

  Periksa log lb config di atas. Kemungkinan penyebab:
    - auto/config gagal (mis. ORACLE_ROOT salah di dalam container)
    - noauto hilang sehingga terjadi rekursi
    - image builder tidak lengkap"
fi

if [ -d "${BUILD_DIR}/.build" ]; then
	log "tahap config terverifikasi (config/binary ada, .build ada)"
else
	# Bukan kegagalan: keberadaan .build/ tidak dijamin dokumentasi.
	log "tahap config terverifikasi (config/binary ada; catatan: .build/ tidak ada)"
fi

# ---------------------------------------------------------------------------
# TAHAP 2 — aset proyek DIPULIHKAN setelah `lb config`
#
# Kenapa dipulihkan, bukan sekadar "ditulis sekali di awal": `lb config`
# mempopulasi config/ dan dapat membuang/mengganti isi includes.chroot serta
# package-lists. Apa pun yang ditaruh di sana sebelum tahap config bisa
# hilang, jadi seluruhnya disalin ULANG dari image/ (sumber asli), bukan dari
# build/ yang sudah disentuh live-build.
#
# PENTING: yang dipulihkan adalah SELURUH package-lists/, bukan hanya file
# hasil generator. oracle-core.list.chroot berisi paket inti (live-boot,
# live-config, kernel, sudo). Kalau hanya file profile yang dipulihkan,
# paket inti bisa hilang tanpa suara dan image dibangun tanpa sistem dasar.
# ---------------------------------------------------------------------------
INCLUDES="${BUILD_DIR}/config/includes.chroot"
mkdir -p "${INCLUDES}"
cp -a -- "${SOURCE_DIR}/config/includes.chroot/." "${INCLUDES}/"

# Pulihkan SELURUH package-lists dari sumber (oracle-core dan apa pun yang
# ditambahkan nanti). File hasil generator ditulis sesudah ini.
PACKAGE_LISTS="${BUILD_DIR}/config/package-lists"
mkdir -p "${PACKAGE_LISTS}"
cp -a -- "${SOURCE_DIR}/config/package-lists/." "${PACKAGE_LISTS}/"

# Bukti: paket inti harus benar-benar ada dan tidak kosong.
[ -s "${PACKAGE_LISTS}/oracle-core.list.chroot" ] || die "oracle-core.list.chroot hilang atau kosong setelah lb config.
  Tanpa paket inti, image tidak akan punya live-boot/kernel. Build dihentikan."

# Identitas disalin MASUK ke image. Hook berjalan di dalam chroot, tempat
# ${ORACLE_ROOT} tidak ada, jadi hook membaca /etc/oracle/oracle.conf ini.
# Tanpa langkah ini build gagal: "ORACLE_ROOT: unbound variable".
install -d -m 0755 "${INCLUDES}/etc/oracle"
install -m 0644 "${ORACLE_ROOT}/config/oracle.conf" \
	"${INCLUDES}/etc/oracle/oracle.conf"

# Profile terpilih ikut masuk ke image, dibaca CLI saat runtime.
install -m 0644 "${ORACLE_ROOT}/config/profiles.conf" \
	"${INCLUDES}/etc/oracle/profiles.conf"

# Hook proyek: juga dipulihkan, karena `lb config` menata ulang config/hooks.
if [ -d "${SOURCE_DIR}/config/hooks" ]; then
	mkdir -p "${BUILD_DIR}/config/hooks"
	cp -a -- "${SOURCE_DIR}/config/hooks/." "${BUILD_DIR}/config/hooks/"
fi

# Package-list dari profile. Ditulis di sini (setelah lb config) supaya tidak
# tertimpa, tetapi tetap jauh SEBELUM lb build sehingga paket inti dan paket
# profile dipasang lewat satu jalur yang sama.
PACKAGE_LIST="${BUILD_DIR}/config/package-lists/oracle-profiles.list.chroot"
PROFILES_CONF="${ORACLE_ROOT}/config/profiles.conf" \
PROFILE_DIR="${BUILD_DIR}/config/includes.chroot/usr/share/oracle/profiles" \
OUT="${PACKAGE_LIST}" \
	"${ORACLE_ROOT}/scripts/gen-profile-list.sh"

# `lb config` menyiapkan symlink hook; pastikan hook proyek tetap executable
# dan CLI punya bit eksekusi di dalam image.
chmod +x "${INCLUDES}/usr/local/bin/oracle"
find "${BUILD_DIR}/config/hooks" -type f -name '*.hook.*' -exec chmod +x {} + 2>/dev/null || true

# ---------------------------------------------------------------------------
# TAHAP 3 — `lb build`
#   --privileged  : lb build memasang /proc, /sys, /dev/pts di dalam chroot
#                   image (helper lb chroot_proc/sysfs/devpts) dan menjalankan
#                   debootstrap yang memakai chroot(2). Keduanya butuh
#                   CAP_SYS_ADMIN + CAP_SYS_CHROOT. Ini melumpuhkan isolasi
#                   container — lihat docs/ARCHITECTURE.md "Blast radius".
#   --userns=host : tanpa pemetaan UID; keep-id dihapus karena memblokir mount
#   -w /work/build: live-build menulis config/binary/chroot di sini, BUKAN di
#                   root repo, sehingga config/oracle.conf proyek aman
# ---------------------------------------------------------------------------
log "tahap 2/2: lb build"
$PODMAN run --rm -it \
	--network=host \
	--privileged \
	--userns=host \
	-v "${ORACLE_ROOT}:/work:ro,Z" \
	-v "${BUILD_DIR}:/work/build:rw,Z" \
	-e ORACLE_ROOT=/work \
	-e HOME=/root \
	-w /work/build \
	"${BUILDER_IMAGE}" \
	/bin/sh -c 'lb build'

# ---------------------------------------------------------------------------
# Sukses hanya kalau ISO benar-benar ada di disk.
# ---------------------------------------------------------------------------
ISO="$(find "${BUILD_DIR}" -maxdepth 1 -name '*.iso' -type f -print -quit 2>/dev/null || true)"

if [ -z "${ISO}" ]; then
	die "build selesai tanpa ISO di ${BUILD_DIR}. Ini artinya GAGAL.
  Jangan anggap sukses. Baca log di atas."
fi

log "selesai: ${ISO}"
ls -lh "${ISO}"
sha256sum "${ISO}" | tee "${ISO}.sha256"
