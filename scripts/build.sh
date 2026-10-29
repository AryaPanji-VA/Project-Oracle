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
	log "  builder   : ${BUILDER_IMAGE} (podman rootful)"
	if ! command -v qemu-system-x86_64 >/dev/null 2>&1; then
		log "  catatan   : qemu belum ada — build bisa jalan, uji boot belum"
	fi
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

# ---------------------------------------------------------------------------
# Workspace bersih. build/ adalah artefak yang bisa dibuat ulang, jadi
# menghapusnya aman. Sisa build lama = sumber bug paling membingungkan
# ("kok hasilnya sama padahal sudah diubah?").
# ---------------------------------------------------------------------------
if [ -d "${BUILD_DIR}" ]; then
	log "membersihkan workspace lama: ${BUILD_DIR}"
	sudo rm -rf -- "${BUILD_DIR}"
fi
mkdir -p -- "${BUILD_DIR}"

log "menyalin sumber image/ -> build/"
cp -a -- "${SOURCE_DIR}/." "${BUILD_DIR}/"

# Identitas disalin MASUK ke image. Hook berjalan di dalam chroot, tempat
# ${ORACLE_ROOT} tidak ada, jadi hook membaca /etc/oracle/oracle.conf ini.
# Tanpa langkah ini build gagal: "ORACLE_ROOT: unbound variable".
install -d -m 0755 "${BUILD_DIR}/config/includes.chroot/etc/oracle"
install -m 0644 "${ORACLE_ROOT}/config/oracle.conf" \
	"${BUILD_DIR}/config/includes.chroot/etc/oracle/oracle.conf"

# Profile terpilih ikut masuk ke image, dibaca hook 0200 saat build.
install -m 0644 "${ORACLE_ROOT}/config/profiles.conf" \
	"${BUILD_DIR}/config/includes.chroot/etc/oracle/profiles.conf"

chmod +x "${BUILD_DIR}/auto/config"
chmod +x "${BUILD_DIR}/config/includes.chroot/usr/local/bin/oracle"
find "${BUILD_DIR}/config/hooks" -type f -name '*.hook.*' -exec chmod +x {} + 2>/dev/null || true

# ---------------------------------------------------------------------------
# Image builder: sekali bangun, dipakai berulang.
# ---------------------------------------------------------------------------
if ! $PODMAN image exists "${BUILDER_IMAGE}" 2>/dev/null; then
	log "membangun builder ${BUILDER_IMAGE} (sekali saja, butuh jaringan)"
	$PODMAN build -t "${BUILDER_IMAGE}" -f "${SOURCE_DIR}/Containerfile" "${SOURCE_DIR}"
else
	log "builder ${BUILDER_IMAGE} sudah ada"
fi

# ---------------------------------------------------------------------------
# Build di dalam container.
#   --privileged  : lb build perlu mount loop & chroot ke dalam image
#   --userns=host : tanpa pemetaan UID; keep-id dihapus karena memblokir mount
#   -w /work/build: live-build menulis config/binary/chroot di sini, BUKAN di
#                   root repo, sehingga config/oracle.conf proyek aman
# ---------------------------------------------------------------------------
log "mulai build image (lama; output live-build menyusul)"
$PODMAN run --rm -it \
	--privileged \
	--userns=host \
	-v "${ORACLE_ROOT}:/work:Z" \
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