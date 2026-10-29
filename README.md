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
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — keputusan teknis: base system, build system, tooling, dan batas keamanan.
- `config/oracle.conf` — identitas proyek (nama, ID, versi, base distribution, purpose).

## Struktur Repository

```
Oracle-OS/
├── image/          # sumber build live-build (di-commit)
│   ├── auto/config #   konfigurasi `lb config`
│   ├── config/     #   package-lists & hooks
│   └── Containerfile
├── config/         # identitas proyek: oracle.conf
├── docs/           # ROADMAP.md, ARCHITECTURE.md
├── scripts/        # build.sh
└── build/          # workspace build — DIABAIKAN Git, dibuat ulang tiap build
```

## Build

Butuh `podman`. Build berjalan di dalam container Debian 13, **bukan di host**:

```bash
sudo pacman -S podman     # sekali saja
./scripts/build.sh --check   # cek prasyarat tanpa build
./scripts/build.sh           # build image ISO
```

Hasil build muncul di `build/` dan tidak pernah masuk Git.

## Catatan

ORACLE dimulai sebagai distribusi Linux berbasis kernel yang sudah ada. Pengembangan kernel sendiri merupakan tujuan jangka panjang yang terpisah.

## Status

`Early Development`

Proyek ini masih dalam tahap awal pembelajaran dan eksperimen.