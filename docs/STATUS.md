# ORACLE OS — Status

> Living document. Perbarui setiap sesi kerja.
> Terakhir diperbarui: 2026-10-29 (audit, fix, CLI, profiles)

## Kondisi repo

| Item | Kondisi |
|---|---|
| Branch | `main` |
| Working tree | bersih setelah commit terakhir |
| Podman | **belum terpasang** di host |
| QEMU | **belum terpasang** di host |
| Disk kosong | 135 GB |
| ISO terbangun | **belum ada — belum pernah sekali pun** |

## Temuan audit (Prioritas A)

### B-1 — BLOCKER (sudah diperbaiki): hook gagal di dalam chroot

Hook `0100-oracle-identity` membaca `${ORACLE_ROOT}/config/oracle.conf`.
Hook berjalan di dalam chroot image, tempat `ORACLE_ROOT` tidak ada. Dengan
`set -eu`, build berhenti dengan `ORACLE_ROOT: unbound variable`.

Dibuktikan: `env -u ORACLE_ROOT sh hook` → exit 1.

**Perbaikan:** `scripts/build.sh` menyalin `config/oracle.conf` ke
`build/config/includes.chroot/etc/oracle/oracle.conf`. Hook membaca path itu
dan tidak lagi bergantung pada variabel host.

### B-2 — (sudah diperbaiki) `--privileged` + `--userns=keep-id` saling mengganggu

Kombinasi ini membuat `mount` gagal di container rootless; podman melaporkan
EUID 1000 (podman issue #6735). `lb build` memakai mount loop/bind, jadi
`--userns=keep-id` dihapus.

### B-3 — (sudah diperbaiki) `--privileged` rootless tidak cukup

`lb build` butuh `CAP_SYS_ADMIN`. Di podman rootless, `--privileged` hanya
memberi `SYS_ADMIN` ke UID 0 di dalam container (podman issue #13449), dan
pemetaan UID rootless tetap menghalangi bind mount.

**Perbaikan:** build lewat podman **rootful** (`sudo podman`) dengan
`--userns=host`. Konsekuensi: isi `build/` milik root, jadi pembersihan
workspace juga memakai `sudo`.

### B-4 — (sudah diperbaiki) hitungan paket profile kurang satu

`wc -l` melaporkan 9 untuk file berisi 10 paket bila file tidak diakhiri
newline. Diganti `grep -c .`.

## Yang sudah jadi

| Komponen | Status | Bukti |
|---|---|---|
| Identitas di image (hostname, os-release, oracle-release) | jalan | 2x run hook, entri `127.0.1.1` tidak duplikat |
| CLI `oracle` — identity/version/profile list/check/install | jalan | `tests/cli_test.sh` 17/17 lulus |
| Validasi input CLI (anti command injection) | jalan | 6 nama berbahaya ditolak |
| Profile networking (10 paket) & web-security (5 paket) | terdefinisi | satu sumber, dipakai build + runtime |
| Hook profiles (build-time) | jalan | profil kosong → image minimal; profil valid → apt dipanggil; profil hilang → exit 1 |
| Staging build (`image/` → `build/`) | jalan | 10 file di workspace, executable bit utuh |
| Preflight & pesan error `build.sh` | jalan | `--check` lolos; tanpa podman gagal dengan pesan jelas |
| Uji QEMU (`--test`) | terpasang di script | **belum pernah dijalankan** — belum ada ISO |

## Perintah tes yang dijalankan

```
sh -n  image/config/hooks/live/*.chroot                    # OK
sh -n  image/config/includes.chroot/usr/local/bin/oracle   # OK
bash -n scripts/build.sh                                   # OK
bash -n tests/cli_test.sh                                  # OK
./tests/cli_test.sh                                        # 17 lulus, 0 gagal
```

Uji hook dilakukan dengan menyalin hook ke direktori sementara dan
mengalihkan `/etc` serta `/usr/share`. Semua uji berjalan di host, bukan
di dalam image.

## Blocker yang belum terselesaikan

1. **Podman belum terpasang.** Butuh `sudo pacman -S podman` oleh pemilik mesin.
2. **QEMU belum terpasang.** Butuh `sudo pacman -S qemu-base` sebelum uji boot.
3. **ISO belum pernah dibangun.** Setiap klaim "build berhasil" sampai saat ini
   belum punya bukti. Jangan ada yang mengklaim sebaliknya.
4. **Pemasangan profile saat runtime belum diuji di sistem target.** Yang diuji
   hanya logika CLI di host. Uji nyata hanya valid di dalam image hasil build.

## Utang teknis (bukan blocker)

- Hook `0200-oracle-profiles` memasang paket profile lewat apt **di dalam
  chroot**, setelah live-build memasang paket inti. Cara yang lebih bersih:
  hasilkan file `.list` di `build/config/package-lists/` **sebelum** `lb build`,
  supaya semua paket dipasang lewat satu jalur. Pekerjaan lanjutan.
- Desktop environment, firewall default, dan hardening belum ditentukan
  (ARCHITECTURE §5 dan §6 masih TBD).

## Langkah berikutnya

```bash
cd ~/Projects/Oracle-OS
sudo pacman -S podman qemu-base   # butuh izin pemilik mesin
./scripts/build.sh --check
./scripts/build.sh                # build ISO pertama
./scripts/build.sh --test         # boot di QEMU setelah ISO ada
```

Yang harus diverifikasi di dalam QEMU setelah ISO ada:

```bash
cat /etc/oracle-release      # ORACLE OS 0.1.0 (debian trixie)
hostname                     # oracle
cat /etc/os-release          # PRETTY_NAME="ORACLE OS 0.1.0"
oracle identity
oracle profile list
ip addr                      # jaringan dasar
```

## Melanjutkan setelah sesi AI berakhir

1. `git log --oneline -3` — lihat posisi terakhir.
2. Baca file ini.
3. Jalankan `./tests/cli_test.sh` — kalau lulus, dasar CLI masih utuh.
4. Lanjut ke blocker nomor 1: pasang podman, lalu build.