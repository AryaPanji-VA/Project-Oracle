# ORACLE OS — Project Roadmap

> **Status:** Early Development  
> **Versi roadmap:** 0.1.0  
> **Base distribution:** Debian 13 (trixie)  
> **Build system:** Debian Live (`live-build`) di container Podman rootful
> **Testing environment:** QEMU virtual machine  
> **Project focus:** Linux systems learning and isolated cybersecurity lab

## 1. Project Vision

ORACLE OS adalah distribusi Linux eksperimental yang dikembangkan untuk mempelajari cara kerja sistem operasi Linux, membangun lingkungan cybersecurity yang terisolasi, dan mengembangkan tooling sistem sendiri.

Pengembangan dimulai dengan menggunakan kernel Linux yang sudah tersedia dan membangun distribusi berbasis Debian. Pengembangan kernel sendiri merupakan tujuan jangka panjang yang akan dikerjakan sebagai proyek riset terpisah.

### Project Goals

- [x] Memahami struktur dan proses pembangunan distribusi Linux.
- [x] Menghasilkan image ORACLE OS yang dapat di-boot.
- [x] Mengembangkan dan menguji sistem di QEMU tanpa mengganggu sistem utama.
- [x] Membentuk identitas, konfigurasi, paket, dan tooling ORACLE OS.
- [ ] Membangun cybersecurity lab yang terisolasi. (sebagian: `oracle lab` sudah berjalan dan terverifikasi; target latihan & prosedur eksperimen belum)
- [ ] Mempelajari arsitektur kernel dan mengembangkan kernel eksperimental pada tahap lanjutan.

### Non-Goals untuk Versi Awal

- Membuat kernel sendiri sebelum fondasi distribusi stabil.
- Menggantikan Omarchy atau instalasi Windows yang sudah ada.
- Melakukan instalasi langsung ke SSD utama.
- Menambahkan banyak fitur sebelum image dasar berhasil di-boot dan diuji.
- Mengklaim keamanan sistem sebelum pengujian yang memadai dilakukan.

---

## 2. Development Principles

1. **Build before expanding:** prioritaskan image minimal yang berhasil di-boot.
2. **Learn by doing:** setiap tahap harus menghasilkan sesuatu yang bisa diuji.
3. **Reproducibility:** proses build harus terdokumentasi dan dapat diulang.
4. **Version control:** perubahan proyek harus tercatat menggunakan Git.
5. **Isolation first:** pengujian sistem dilakukan di virtual machine.
6. **Explicit permission:** tidak ada perubahan pada sistem utama, partisi, bootloader, atau Windows tanpa persetujuan eksplisit.
7. **Understand the tools:** setiap tool atau perintah baru harus dipahami tujuannya sebelum digunakan.

---

## 3. Development Roadmap

### Phase 0 — Foundation & Project Specification

**Status:** Complete

**Goal:** Menetapkan identitas, ruang lingkup, dan struktur dasar proyek sebelum membangun sistem.

Tasks:

- [x] Membuat repository Git untuk ORACLE OS.
- [x] Membuat README awal.
- [x] Membuat struktur direktori awal.
- [x] Mendokumentasikan arsitektur dan keputusan teknis.
- [x] Menetapkan spesifikasi proyek secara tertulis (`docs/SPECIFICATION.md`).
- [x] Menetapkan workflow development dan testing (`docs/DEVELOPMENT.md`).
- [x] Memverifikasi konfigurasi proyek dan struktur repository.

Deliverables:

- `README.md`
- `docs/ROADMAP.md`
- `config/oracle.conf`
- `docs/ARCHITECTURE.md`
- `docs/SPECIFICATION.md`
- `docs/DEVELOPMENT.md`
- `.gitignore`

**Acceptance criteria:**

- Tujuan dan batasan ORACLE OS terdokumentasi.
- Struktur proyek dipahami dan konsisten.
- Keputusan teknis utama memiliki alasan yang jelas.
- Tidak ada perubahan pada sistem utama yang diperlukan untuk menyelesaikan tahap ini.

**Verifikasi Phase 0 (2026-10-30):** konfigurasi identitas dan struktur repo telah diperiksa; shell syntax, test suite, dan pemeriksaan diff dijalankan. Ini tidak mencakup build ISO atau boot.

### Phase 1 — First Bootable ORACLE OS

**Status:** Complete (2026-11-08)

**Goal:** Menghasilkan image Linux minimal berbasis Debian menggunakan `live-build` (Debian Live) dan membuktikan bahwa image tersebut dapat di-boot.

**Lingkungan build:** container Podman **rootful** (`sudo podman`) berbasis Debian 13, sumber di `image/`, workspace di `build/`. Dibutuhkan karena `lb build` memasang `/proc`, `/sys`, `/dev/pts` di dalam chroot image dan menjalankan `chroot(2)`. Keputusan dan alasannya ada di `docs/ARCHITECTURE.md` §8.

Tasks:

- [x] Memahami cara kerja Debian Live dan `live-build`. (didokumentasikan di `docs/ARCHITECTURE.md`; pipeline `lb config` → debootstrap → chroot hooks → squashfs → xorriso dipakai dan di-debug sendiri selama Phase 5)
- [x] Menentukan lingkungan build yang aman dan terpisah (VM Debian 13 disposable; NAT, tanpa disk/shared folder host; smoke test rootful Podman lulus).
- [x] Menyiapkan konfigurasi image minimal ORACLE OS (console core + source config XFCE/LightDM terpisah).
- [x] Menentukan paket awal yang benar-benar diperlukan untuk varian console dan desktop.
- [x] Menjalankan proses build image (berhasil di VM Debian 13 pada 2026-10-31).
- [x] Memverifikasi file image dan hasil build (format ISO9660/hybrid, checksum cocok).
- [x] Menjalankan image menggunakan QEMU (boot console tervalidasi; ISO desktop lama belum di-boot).
- [x] Memvalidasi boot graphical end-to-end: serial console menangkap boot hingga `oracle login:`, sesi XFCE mencapai `graphical.target` (Stage 3D–3H).
- [x] Membangun ulang dan memvalidasi varian XFCE + LightDM (2026-11-01; ISO graphical phase 2 terbentuk dan di-boot: GRUB, autologin LightDM, session XFCE, keyboard, dan input mouse via QMP semuanya tervalidasi).
- [x] Mendokumentasikan hasil pengujian desktop dan masalah yang ditemukan (lihat `docs/STATUS.md` bagian Phase 2).

**Catatan build (2026-10-31):** ISO `build/live-image-amd64.hybrid.iso`
berhasil dibuat dan checksum dicatat di `build/SHA256SUMS`. Format media,
checksum, dan boot console tervalidasi, sehingga milestone First Boot (console)
tercapai.

**Catatan build graphical (2026-11-01):** dua ISO desktop dibangun di VM
Debian 13 disposable. Baseline `b76d429c…0be09` (tanpa `xfce4-terminal`)
dan refinement `6e0e744f…3cc9d4` (dengan `xfce4-terminal`) sudah di-boot di
QEMU dan mencapai desktop XFCE. **Milestone First Boot graphical tercapai.**
Rincian bukti ada di `docs/STATUS.md`.

Deliverables:

- Konfigurasi build ORACLE OS.
- Image ISO hasil build.
- Catatan proses build.
- Dokumentasi hasil pengujian QEMU.

**Acceptance criteria:**

- Proses build berhasil diselesaikan.
- Image dapat di-boot di QEMU.
- Sistem mencapai lingkungan yang diharapkan tanpa kegagalan kritis.
- Proses build dan pengujian dapat diulang mengikuti dokumentasi.

**Milestone:** ORACLE OS berhasil melakukan boot pertama (console dan graphical).

### Phase 2 — Core Identity & System

**Status:** Complete (2026-11-08) — seluruh task selesai; keputusan menutup phase diambil 2026-11-08

**Goal:** Membentuk identitas ORACLE OS dan menjadikan konfigurasi sistem lebih terstruktur.

Tasks:

- [x] Menentukan hostname dan identitas distribusi. (`config/oracle.conf`: `NAME="ORACLE OS"`, `ID="oracle"`, `VERSION="0.1.0"`; hook `0100-oracle-identity` menulis `/etc/os-release`, `/etc/hosts`, `/etc/hostname`, `/etc/oracle-release` — diverifikasi 2× run byte-identik)
- [x] Menetapkan konfigurasi dasar sistem. (`image/auto/config` + `image/config/` — struktur Debian Live terpisah source/workspace)
- [x] Menentukan paket bawaan berdasarkan kebutuhan nyata. (`oracle-core.list.chroot` + `oracle-desktop.list.chroot`; 17 paket desktop, tiap paket berkomentar alasan; `--apt-recommends false`)
- [x] Membuat mekanisme konfigurasi ORACLE OS. (CLI `/usr/local/bin/oracle` — identity/version/profile list/check/install; `tests/cli_test.sh` 17/17 lulus)
- [x] Menambahkan skrip pemeliharaan yang terdokumentasi. (`scripts/build.sh`, `scripts/gen-profile-list.sh`; `docs/DEVELOPMENT.md` 61 baris)
- [x] Menguji perubahan konfigurasi di QEMU. (Stage 3D–3H: boot graphical end-to-end, serial console, sesi XFCE, wallpaper/panel/dock/ikon/font/terminal terverifikasi piksel)
- [x] Memastikan sistem tetap dapat di-boot setelah perubahan. (ISO `35fadba2…ad3ca` boot bersih → `oracle login:`; 0 `[FAILED]`, 0 panic)

Deliverables:

- Konfigurasi sistem ORACLE OS.
- Daftar paket bawaan beserta alasan pemilihannya.
- Skrip pemeliharaan awal.
- Dokumentasi konfigurasi dan troubleshooting.

**Acceptance criteria:**

- Identitas distribusi dapat diverifikasi.
- Konfigurasi tidak tersebar tanpa struktur yang jelas.
- Skrip dapat dijalankan dan diuji sesuai dokumentasinya.
- Image tetap dapat di-boot setelah perubahan.

### Phase 3 — Sentinel Security Lab

**Status:** In Progress — 4/7 task selesai lewat `oracle lab` (2026-11-08)

**Goal:** Mengembangkan lingkungan pembelajaran cybersecurity yang terisolasi dan dapat digunakan untuk eksperimen yang terkontrol.

Tasks:

- [x] Mendefinisikan model isolasi lab. (dua network namespace `oracle-lab-atk`/`oracle-lab-tgt` dihubungkan veth pair, tanpa default route dan tanpa NAT; didokumentasikan di `docs/ORACLE-TOOLING.md`)
- [x] Menentukan kebutuhan virtual network dan VM. (netns + veth, bukan VM: lebih ringan dan tidak butuh image tambahan; subnet `10.66.0.0/24`, attacker `10.66.0.1`, target `10.66.0.2`)
- [ ] Menyiapkan snapshot untuk pemulihan eksperimen.
- [x] Memilih tool berdasarkan tujuan pembelajaran. (profil `networking` + `web-security`; `oracle lab` melaporkan alat yang belum terpasang alih-alih gagal diam)
- [ ] Menyiapkan target latihan lokal yang sengaja dibuat untuk pengujian.
- [ ] Mendokumentasikan prosedur eksperimen dan pemulihan.
- [x] Memverifikasi batas jaringan dan akses sebelum menjalankan pengujian. (`oracle lab start` menjalankan `_verify`: host tidak bisa menjangkau lab, lab tidak punya rute keluar, DNS ditutup; diverifikasi 22/22 di ISO hidup)

Deliverables:

- Dokumentasi arsitektur lab.
- Konfigurasi lingkungan virtual.
- Prosedur snapshot dan recovery.
- Panduan eksperimen keamanan lokal.

**Acceptance criteria:**

- Lab dapat dijalankan dan dipulihkan secara terkontrol.
- Pengujian awal menggunakan target lokal atau sistem yang memiliki izin.
- Batas jaringan dan dampak setiap eksperimen dipahami.
- Eksperimen tidak bergantung pada akses ke sistem utama.

### Phase 4 — ORACLE Tooling

**Status:** Done (2026-11-08)

**Goal:** Mengembangkan utilitas dan command-line tools sendiri untuk membantu pengelolaan dan pembelajaran sistem.

Tasks:

- [x] Mengidentifikasi kebutuhan tooling yang benar-benar muncul selama pengembangan.
- [x] Menentukan fungsi dan antarmuka CLI awal.
- [x] Membuat tool pertama dengan ruang lingkup kecil.
- [x] Menambahkan validasi input dan penanganan error.
- [x] Membuat pengujian dan dokumentasi penggunaan.
- [x] Mengintegrasikan tool ke image hanya setelah pengujian berhasil.

Contoh kemungkinan tooling:

- Pemeriksaan informasi sistem. → `oracle status`
- Pemeriksaan status konfigurasi ORACLE OS. → `oracle doctor`
- Pembantu proses build dan validasi image. → `scripts/build.sh`, `tests/run_all.sh`
- Pemeriksaan kesehatan sistem. → `oracle doctor`
- Pengelolaan catatan eksperimen lab. → `oracle lab`

Deliverables:

- Satu atau lebih CLI tools yang berfungsi. → `oracle status`, `oracle doctor`, `oracle lab`
- Dokumentasi perintah dan contoh penggunaan. → `docs/ORACLE-TOOLING.md`
- Pengujian untuk fungsi utama. → `tests/oracle_cli_modules_test.sh` (29 pemeriksaan)

**Acceptance criteria:**

- Setiap tool memiliki tujuan yang jelas. ✓
- Perilaku dan output dapat diverifikasi. ✓ (`oracle lab status` memverifikasi
  isolasi secara struktural; `oracle doctor` melaporkan temuan)
- Error ditangani dengan baik. ✓ (pesan menyebutkan sebab dan perintah perbaikan,
  mis. `sudo oracle profile install networking`)
- Tool tidak melakukan perubahan destruktif secara diam-diam. ✓ (`status` dan
  `doctor` hanya membaca; `lab start/stop` hanya menyentuh namespace dan state
  miliknya sendiri)

Catatan: modul ditulis POSIX sh dan dijalankan dengan `dash`, bukan bash.
Rincian desain dan jebakan yang sudah dilewati ada di `docs/ORACLE-TOOLING.md`.

### Phase 5 — Reliability & Release

**Status:** Done (2026-11-08)

**Goal:** Membuat proses build dan pengujian ORACLE OS lebih konsisten, terdokumentasi, dan mudah direproduksi.

Tasks:

- [x] Mengulang proses build dari kondisi yang terdokumentasi. (build dari `0a639ae` di guest Debian 13; 5 iterasi sampai ISO demo; `docs/PHASE5-DEMO-USABLE.md`)
- [x] Menetapkan checklist pengujian untuk setiap image. (`verify-iso.py` — 40/40 cek E2E: boot, login, identitas, panel, audio, polkit, unit gagal)
- [x] Menguji boot, konfigurasi, dan fungsi inti. (40/40 pada ISO demo; 22/22 pada ISO tooling)
- [x] Mendokumentasikan known issues. (`docs/PHASE5-DEMO-USABLE.md` §batas: belum ada installer, tidak ada persistensi, belum diuji hardware asli, belum ada hardening)
- [x] Menetapkan versi dan catatan perubahan. (`config/oracle.conf` `VERSION="0.1.0"`; `/etc/oracle-release`; `oracle version`)
- [x] Menyimpan checksum untuk artefak rilis. (`build/SHA256SUMS`; `~/Backups/ORACLE-OS-*.iso.sha256`, `sha256sum -c` OK)
- [x] Menetapkan prosedur backup dan pemulihan proyek. (`~/oracle-recovery/README.md`, `boot-vm.sh`, `run-demo.sh`, `PHASE5-SUMMARY.md`; snapshot qcow2 `pre-phase5-recovery`)

Deliverables:

- Checklist pengujian. (`verify-iso.py`, `verify-tooling.py`, `tests/run_all.sh` 10/10 suite / 246 assertion)
- Build instructions yang diperbarui. (`docs/DEVELOPMENT.md`, `docs/PHASE5-DEMO-RUNBOOK.md`)
- Release notes. (`docs/PHASE5-DEMO-USABLE.md`)
- Informasi versi dan checksum image. (`build/SHA256SUMS`, `~/Backups/*.sha256`)
- Dokumentasi known issues. (`docs/PHASE5-DEMO-USABLE.md`)

**Acceptance criteria:**

- Image dapat dibangun ulang mengikuti instruksi proyek.
- Pengujian inti memiliki hasil yang tercatat.
- Masalah yang diketahui tidak disembunyikan.
- Setiap artefak rilis memiliki versi yang dapat diidentifikasi.

### Phase 6 — Kernel Research

**Status:** Long-Term Research

**Goal:** Mempelajari arsitektur kernel secara mendalam dan memulai eksperimen kernel sebagai proyek terpisah.

Tasks:

- [ ] Mempelajari proses boot Linux.
- [ ] Memahami system calls dan interaksi user space dengan kernel.
- [ ] Mempelajari manajemen memori.
- [ ] Mempelajari proses, thread, dan scheduling.
- [ ] Mempelajari interrupt dan driver.
- [ ] Membangun lingkungan eksperimen kernel yang terpisah.
- [ ] Menjalankan eksperimen menggunakan QEMU.
- [ ] Mendokumentasikan perbedaan antara kernel Linux yang digunakan dan kernel eksperimental.

Deliverables:

- Catatan riset kernel.
- Program eksperimen kecil.
- Lingkungan pengujian kernel.
- Dokumentasi hasil dan keterbatasan eksperimen.

**Acceptance criteria:**

- Konsep yang dipelajari dibuktikan melalui eksperimen.
- Kernel eksperimental tidak menggantikan kernel sistem utama.
- Pengujian dapat dilakukan di lingkungan virtual yang terisolasi.
- Hasil eksperimen dan keterbatasannya terdokumentasi.

**Catatan:** Kernel Research bukan prasyarat untuk membuat image awal ORACLE OS. Tahap ini dimulai setelah fondasi distribusi cukup stabil dan pemahaman dasar sistem sudah berkembang.

---

## 4. Milestone Overview

| Milestone | Hasil yang diharapkan |
|---|---|
| M0 — Foundation | Struktur proyek dan spesifikasi terdokumentasi |
| M1 — First Boot | Image ORACLE OS berhasil di-boot di QEMU |
| M2 — Core System | Identitas dan konfigurasi sistem terstruktur |
| M3 — Security Lab | Lingkungan cybersecurity terisolasi berfungsi |
| M4 — ORACLE Tooling | Tooling CLI awal berfungsi dan teruji |
| M5 — Reliable Build | Build dan pengujian dapat diulang |
| M6 — Kernel Research | Eksperimen kernel terpisah berjalan di lingkungan virtual |

Milestone diselesaikan berdasarkan acceptance criteria, bukan hanya karena semua task sudah dicentang.

---

## 5. Development Workflow

Untuk setiap perubahan:

1. Tentukan satu tujuan kecil.
2. Pelajari tool dan konsep yang diperlukan.
3. Implementasikan perubahan.
4. Jalankan pengujian yang relevan.
5. Catat hasil dan masalah yang ditemukan.
6. Simpan perubahan menggunakan Git setelah hasilnya diperiksa.

Hindari mengerjakan beberapa fitur besar secara bersamaan sebelum fondasi yang diperlukan selesai.

---

## 6. Safety Boundaries

- Pengembangan awal berfokus pada build dan pengujian di lingkungan virtual.
- Jangan menulis image ke SSD internal atau USB fisik tanpa persetujuan eksplisit dan verifikasi target perangkat.
- Jangan mengubah partisi, EFI, bootloader, konfigurasi Omarchy, atau Windows sebagai bagian dari workflow default.
- Jangan menjalankan perintah destruktif tanpa menjelaskan dampak dan mendapatkan persetujuan.
- Gunakan snapshot atau salinan VM sebelum eksperimen yang berisiko.
- Pengujian keamanan dibatasi pada sistem milik sendiri atau sistem yang memiliki izin eksplisit.
- Jika suatu langkah berpotensi mengganggu sistem utama, hentikan dan evaluasi alternatif yang lebih aman.

---

## 7. Current Focus

**Prioritas saat ini: menyelesaikan Foundation dan mempersiapkan First Boot.**

Langkah berikutnya:

1. Memeriksa isi repository dan dokumen yang sudah tersedia.
2. Melengkapi spesifikasi proyek dan keputusan arsitektur.
3. Memahami kebutuhan build Debian Live (`live-build`).
4. Menyiapkan workflow build yang terisolasi.
5. Menghasilkan dan menguji image minimal di QEMU.

**Prinsip utama:** ORACLE OS tidak perlu langsung menjadi distribusi yang lengkap. Target awalnya adalah image minimal yang benar-benar bisa dibangun, di-boot, diuji, dan dipahami proses kerjanya.
