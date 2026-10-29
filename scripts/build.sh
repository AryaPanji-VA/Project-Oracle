#!/usr/bin/env bash
# ============================================================================
# scripts/build.sh — pembungkus build ORACLE OS
#
# Prinsip file ini:
#   1. Tidak menyentuh host. Semua kerja terjadi di dalam container.
#   2. `config/` milik proyek TIDAK PERNAH tertimpa. live-build menulis folder
#      `config/`, `binary/`, `chroot/`, `cache/` di direktori tempat ia
#      dijalankan, jadi kita jalankan di build/ (gitignored), bukan di root repo.
#   3. Gagal dengan pesan jelas, bukan gagal secara misterius.
#
# Pemakaian:
#   ./scripts/build.sh              # build image lengkap
#   ./scripts/build.sh --check      # hanya cek prasyarat, tidak build
# ============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Lokasi proyek ditentukan dari lokasi script ini, bukan dari $PWD.
# Jadi script aman dipanggil dari direktori mana pun.
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ORACLE_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
export ORACLE_ROOT

BUILD_DIR="${ORACLE_ROOT}/build"
SOURCE_DIR="${ORACLE_ROOT}/image"
BUILDER_IMAGE="oracle-builder:13"

# shellcheck disable=SC1091
. "${ORACLE_ROOT}/config/oracle.conf"

log()  { printf '\033[1;34m[oracle]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[oracle]\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31m[oracle] ERROR:\033[0m %s\n' "$*" >&2; exit 1; }

# ---------------------------------------------------------------------------
# 1. Prasyarat
# ---------------------------------------------------------------------------
require_podman() {
	command -v podman >/dev/null 2>&1 || die "podman belum terpasang.
  Pasang dulu:  sudo pacman -S podman
  Lalu cek:     podman info"
	podman info >/dev/null 2>&1 || die "podman terpasang tapi tidak bisa dipakai.
  Cek dengan:   podman info"
}

preflight() {
	require_podman
	[ -f "${SOURCE_DIR}/auto/config" ] || die "sumber build tidak lengkap: image/auto/config tidak ada"
	[ -d "${SOURCE_DIR}/config" ]      || die "sumber build tidak lengkap: image/config/ tidak ada"
	log "prasyarat OK"
	log "  proyek     : ${ORACLE_ROOT}"
	log "  identitas  : ${NAME} ${VERSION} (${BASE} ${DEBIAN_RELEASE} ${DEBIAN_CODENAME})"
	log "  sumber     : ${SOURCE_DIR}"
	log "  workspace  : ${BUILD_DIR}"
	log "  builder    : ${BUILDER_IMAGE}"
}

if [ "${1:-}" = "--check" ]; then
	preflight
	log "mode --check: tidak ada yang dibangun."
	exit 0
fi

preflight

# ---------------------------------------------------------------------------
# 2. Siapkan workspace build yang bersih
#
# build/ sengaja dihapus tiap kali. Alasan: sisa build lama adalah sumber
# bug paling membingungkan ("kok hasilnya sama padahal sudah diubah?").
# Karena build/ adalah artefak yang bisa dibuat ulang, menghapusnya aman.
# ---------------------------------------------------------------------------
if [ -d "${BUILD_DIR}" ]; then
	log "membersihkan workspace lama: ${BUILD_DIR}"
	rm -rf -- "${BUILD_DIR}"
fi
mkdir -p -- "${BUILD_DIR}"

log "menyalin sumber image/ -> build/"
cp -a -- "${SOURCE_DIR}/." "${BUILD_DIR}/"

# Pastikan file executable di sumber tetap executable.
chmod +x "${BUILD_DIR}/auto/config"
find "${BUILD_DIR}/config/hooks" -type f -name '*.hook.*' -exec chmod +x {} + 2>/dev/null || true

# ---------------------------------------------------------------------------
# 3. Build image builder (kalau belum ada)
# ---------------------------------------------------------------------------
if ! podman image exists "${BUILDER_IMAGE}"; then
	log "membangun image builder ${BUILDER_IMAGE} (sekali saja, butuh jaringan)"
	podman build -t "${BUILDER_IMAGE}" -f "${SOURCE_DIR}/Containerfile" "${SOURCE_DIR}"
else
	log "image builder ${BUILDER_IMAGE} sudah ada"
fi

# ---------------------------------------------------------------------------
# 4. Jalankan build di dalam container
#
# --privileged diperlukan karena live-build melakukan mount loop device
#   dan operasi chroot. Container ini TIDAK menjalankan kode dari jaringan
#   secara langsung; ia build image. Tetap: hanya dijalankan oleh pemilik repo.
# --userns=keep-id      : file hasil build tetap milik user, bukan root.
# -v ${ORACLE_ROOT}:/work: proyek ter-mount, hasilnya muncul di build/
# HOME=/root            : live-build butuh HOME yang bisa ditulis.
# ---------------------------------------------------------------------------
log "memulai build image (ini bisa lama; output live-build di bawah)"
podman run --rm -it \
	--privileged \
	--userns=keep-id \
	-v "${ORACLE_ROOT}:/work:Z" \
	-e ORACLE_ROOT=/work \
	-e HOME=/root \
	-w /work/build \
	"${BUILDER_IMAGE}" \
	/bin/sh -c 'lb build'

# ---------------------------------------------------------------------------
# 5. Laporkan hasil — jangan pernah bilang sukses tanpa artefak
# ---------------------------------------------------------------------------
ISO="$(find "${BUILD_DIR}" -maxdepth 1 -name '*.iso' -type f -print -quit 2>/dev/null || true)"

if [ -z "${ISO}" ]; then
	die "build selesai tanpa menghasilkan file .iso di ${BUILD_DIR}.
  Ini artinya build GAGAL. Periksa log di atas — jangan anggap sukses."
fi

log "selesai: ${ISO}"
ls -lh "${ISO}"
if command -v sha256sum >/dev/null 2>&1; then
	sha256sum "${ISO}" | tee "${ISO}.sha256"
fi