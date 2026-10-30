# ORACLE OS

**ORACLE OS** adalah proyek eksperimental untuk membangun distribusi Linux sendiri sebagai lab pembelajaran sistem operasi dan cybersecurity.

## Visi

- Membangun distribusi Linux yang ringan, fungsional, dan dapat dikustomisasi.
- Memahami cara kerja Linux, kernel, boot process, dan manajemen sistem.
- Menyediakan lingkungan lab cybersecurity yang aman dan terisolasi.
- Mengembangkan image OS yang dapat diuji melalui QEMU tanpa mengganggu sistem utama.

## Rencana Pengembangan

1. Menyiapkan struktur proyek dan dokumentasi.
2. Mempelajari proses boot dan arsitektur Linux.
3. Membangun image Linux berbasis Debian menggunakan `live-build` (Debian Live).
4. Menguji image di mesin virtual QEMU.
5. Mengembangkan fitur dan tooling khas ORACLE.

## Dokumentasi

- [`docs/ROADMAP.md`](docs/ROADMAP.md) — rencana pengembangan dan acceptance criteria per fase.
- [`docs/SPECIFICATION.md`](docs/SPECIFICATION.md) — ruang lingkup, kebutuhan, dan acceptance criteria proyek.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — keputusan teknis: base system, build system, tooling, dan batas keamanan.
- [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) — workflow development, pemeriksaan, testing, dan build terisolasi.
- [`docs/STATUS.md`](docs/STATUS.md) — kondisi terkini, blocker, dan bukti verifikasi.
- `config/oracle.conf` — identitas proyek (nama, ID, versi, base distribution, purpose).

## Struktur Repository

```
Oracle-OS/
├── image/          # sumber build live-build (di-commit)
│   ├── auto/config #   konfigurasi `lb config`
│   ├── config/     #   package-lists & hooks
│   └── Containerfile
├── config/         # identitas proyek: oracle.conf
├── docs/           # spesifikasi, arsitektur, workflow, roadmap, status
├── scripts/        # build.sh
└── build/          # workspace build — DIABAIKAN Git, dibuat ulang tiap build
```

## Build

Jalankan build di dalam VM sementara (Debian 13 disarankan), bukan langsung di
host utama. Script menolak build privileged di bare metal. Di dalam VM, build
memakai Podman rootful (`sudo podman`) dan `--network=host`; VM tetap perlu
koneksi keluar melalui NAT:

```bash
sudo apt-get update && sudo apt-get install podman sudo  # di Debian VM
./scripts/build.sh --check                         # cek prasyarat dasar
./scripts/build.sh                                 # build image ISO
```

Hasil build muncul di `build/` dan tidak pernah masuk Git.
Setiap build menghapus seluruh workspace `build/` yang lama sebelum staging ulang;
jangan simpan file manual di direktori itu.

**Keamanan:** container builder memakai `--privileged` dan jaringan host VM.
Jangan pasang disk fisik host atau gunakan folder bersama ke checkout asli.
Salin repo ke VM, gunakan jaringan NAT, dan hapus VM setelah build selesai.

## Catatan

ORACLE dimulai sebagai distribusi Linux berbasis kernel yang sudah ada. Pengembangan kernel sendiri merupakan tujuan jangka panjang yang terpisah.

## Status

`Early Development`

Proyek ini masih dalam tahap awal pembelajaran dan eksperimen.
