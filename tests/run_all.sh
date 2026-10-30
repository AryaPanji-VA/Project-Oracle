#!/usr/bin/env bash
# ============================================================================
# tests/run_all.sh — menjalankan seluruh tes ORACLE OS
#
# Mengembalikan exit 0 hanya jika SEMUA tes lulus.
# Kegagalan tidak disembunyikan: tiap tes dilaporkan, dan ringkasan di akhir
# menyebut mana yang gagal.
#
# Pemakaian:
#   ./tests/run_all.sh              jalankan semua
#   ./tests/run_all.sh --stop       berhenti pada kegagalan pertama
#   ./tests/run_all.sh --quiet      hanya ringkasan
# ============================================================================

set -uo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 1

STOP_ON_FAIL=0
QUIET=0
for arg in "$@"; do
	case "$arg" in
		--stop)  STOP_ON_FAIL=1 ;;
		--quiet) QUIET=1 ;;
		-h|--help) sed -n '2,14p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
		*) echo "argumen tidak dikenal: $arg" >&2; exit 2 ;;
	esac
done

# Urutan: yang paling murah dan paling dasar dulu.
TESTS=(
	"tests/posix_test.sh"          # statis: bahasa POSIX
	"tests/profile_list_test.sh"   # generator package-list
	"tests/cli_test.sh"            # CLI dasar
	"tests/cli_packages_test.sh"   # parser & validasi paket CLI
	"tests/containerfile_test.sh"  # statis: Containerfile & mount policy
	"tests/lb_config_flow_test.sh" # alur konfigurasi lb (tiruan semantik)
	"tests/build_order_test.sh"    # staging & urutan build (podman tiruan)
)

echo "=============================================================="
echo " ORACLE OS — test suite"
echo "=============================================================="
echo

declare -a FAILED=()
TOTAL_PASS=0
TOTAL_FAIL=0
N_OK=0

for t in "${TESTS[@]}"; do
	if [ ! -f "$t" ]; then
		printf '%-34s %s\n' "$t" "HILANG"
		FAILED+=("$t (file tidak ditemukan)")
		TOTAL_FAIL=$((TOTAL_FAIL+1))
		continue
	fi

	out="$(bash "$t" 2>&1)"; rc=$?
	if [ "$QUIET" -eq 0 ]; then
		echo "--------------------------------------------------------------"
		echo ">> $t"
		echo "--------------------------------------------------------------"
		printf '%s\n' "$out" | sed 's/^/   /'
	fi

	# Ambil angka dari baris 'hasil: N lulus, M gagal'.
	line="$(printf '%s' "$out" | grep '^hasil:' | tail -1)"
	p="$(printf '%s' "$line" | sed -n 's/^hasil: \([0-9]*\) lulus.*/\1/p')"
	f="$(printf '%s' "$line" | sed -n 's/.*, \([0-9]*\) gagal.*/\1/p')"
	p="${p:-0}"; f="${f:-0}"

	TOTAL_PASS=$((TOTAL_PASS + p))
	TOTAL_FAIL=$((TOTAL_FAIL + f))

	if [ "$rc" -eq 0 ]; then
		N_OK=$((N_OK+1))
		printf '  %-34s OK    (%s lulus)\n' "$(basename "$t")" "$p"
	else
		FAILED+=("$t")
		printf '  %-34s GAGAL (%s lulus, %s gagal)\n' "$(basename "$t")" "$p" "$f"
		if [ "$STOP_ON_FAIL" -eq 1 ]; then
			echo
			echo "berhenti pada kegagalan pertama (--stop)"
			exit 1
		fi
	fi
done

echo
echo "=============================================================="
printf ' Suite : %d/%d tes lulus\n' "$N_OK" "${#TESTS[@]}"
printf ' Assert: %d lulus, %d gagal\n' "$TOTAL_PASS" "$TOTAL_FAIL"
if [ "${#FAILED[@]}" -gt 0 ]; then
	echo " Gagal :"
	for f in "${FAILED[@]}"; do echo "   - $f"; done
fi
echo "=============================================================="
echo
echo "CATATAN: tes ini TIDAK membuktikan ISO dapat dibangun."
echo "         live-build dan podman tidak dijalankan; keduanya ditiru."

if [ "${#FAILED[@]}" -gt 0 ] || [ "$TOTAL_FAIL" -gt 0 ]; then
	exit 1
fi
exit 0
