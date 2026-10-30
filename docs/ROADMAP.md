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

- [ ] Memahami struktur dan proses pembangunan distribusi Linux.
- [ ] Menghasilkan image ORACLE OS yang dapat di-boot.
- [ ] Mengembangkan dan menguji sistem di QEMU tanpa mengganggu sistem utama.
- [ ] Membentuk identitas, konfigurasi, paket, dan tooling ORACLE OS.
- [ ] Membangun cybersecurity lab yang terisolasi.
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

**Status:** In Progress

**Goal:** Menghasilkan image Linux minimal berbasis Debian menggunakan `live-build` (Debian Live) dan membuktikan bahwa image tersebut dapat di-boot.

**Lingkungan build:** container Podman **rootful** (`sudo podman`) berbasis Debian 13, sumber di `image/`, workspace di `build/`. Dibutuhkan karena `lb build` memasang `/proc`, `/sys`, `/dev/pts` di dalam chroot image dan menjalankan `chroot(2)`. Keputusan dan alasannya ada di `docs/ARCHITECTURE.md` §8.

Tasks:

- [ ] Memahami cara kerja Debian Live dan `live-build`.
- [x] Menentukan lingkungan build yang aman dan terpisah (VM Debian 13 disposable; NAT, tanpa disk/shared folder host; smoke test rootful Podman lulus).
- [ ] Menyiapkan konfigurasi image minimal ORACLE OS.
- [ ] Menentukan paket awal yang benar-benar diperlukan.
- [x] Menjalankan proses build image (berhasil di VM Debian 13 pada 2026-10-31).
- [x] Memverifikasi file image dan hasil build (format ISO9660/hybrid, checksum cocok).
- [ ] Menjalankan image menggunakan QEMU.
- [ ] Mendokumentasikan hasil pengujian dan masalah yang ditemukan.

**Catatan build (2026-10-31):** ISO `build/live-image-amd64.hybrid.iso`
berhasil dibuat dan checksum dicatat di `build/SHA256SUMS`. Format media telah
diperiksa, tetapi ISO belum di-boot; milestone First Boot tetap belum tercapai.

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

**Milestone:** ORACLE OS berhasil melakukan boot pertama.

### Phase 2 — Core Identity & System

**Status:** Planned

**Goal:** Membentuk identitas ORACLE OS dan menjadikan konfigurasi sistem lebih terstruktur.

Tasks:

- [ ] Menentukan hostname dan identitas distribusi.
- [ ] Menetapkan konfigurasi dasar sistem.
- [ ] Menentukan paket bawaan berdasarkan kebutuhan nyata.
- [ ] Membuat mekanisme konfigurasi ORACLE OS.
- [ ] Menambahkan skrip pemeliharaan yang terdokumentasi.
- [ ] Menguji perubahan konfigurasi di QEMU.
- [ ] Memastikan sistem tetap dapat di-boot setelah perubahan.

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

**Status:** Planned

**Goal:** Mengembangkan lingkungan pembelajaran cybersecurity yang terisolasi dan dapat digunakan untuk eksperimen yang terkontrol.

Tasks:

- [ ] Mendefinisikan model isolasi lab.
- [ ] Menentukan kebutuhan virtual network dan VM.
- [ ] Menyiapkan snapshot untuk pemulihan eksperimen.
- [ ] Memilih tool berdasarkan tujuan pembelajaran.
- [ ] Menyiapkan target latihan lokal yang sengaja dibuat untuk pengujian.
- [ ] Mendokumentasikan prosedur eksperimen dan pemulihan.
- [ ] Memverifikasi batas jaringan dan akses sebelum menjalankan pengujian.

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

**Status:** Planned

**Goal:** Mengembangkan utilitas dan command-line tools sendiri untuk membantu pengelolaan dan pembelajaran sistem.

Tasks:

- [ ] Mengidentifikasi kebutuhan tooling yang benar-benar muncul selama pengembangan.
- [ ] Menentukan fungsi dan antarmuka CLI awal.
- [ ] Membuat tool pertama dengan ruang lingkup kecil.
- [ ] Menambahkan validasi input dan penanganan error.
- [ ] Membuat pengujian dan dokumentasi penggunaan.
- [ ] Mengintegrasikan tool ke image hanya setelah pengujian berhasil.

Contoh kemungkinan tooling:

- Pemeriksaan informasi sistem.
- Pemeriksaan status konfigurasi ORACLE OS.
- Pembantu proses build dan validasi image.
- Pemeriksaan kesehatan sistem.
- Pengelolaan catatan eksperimen lab.

Deliverables:

- Satu atau lebih CLI tools yang berfungsi.
- Dokumentasi perintah dan contoh penggunaan.
- Pengujian untuk fungsi utama.

**Acceptance criteria:**

- Setiap tool memiliki tujuan yang jelas.
- Perilaku dan output dapat diverifikasi.
- Error ditangani dengan baik.
- Tool tidak melakukan perubahan destruktif secara diam-diam.

### Phase 5 — Reliability & Release

**Status:** Planned

**Goal:** Membuat proses build dan pengujian ORACLE OS lebih konsisten, terdokumentasi, dan mudah direproduksi.

Tasks:

- [ ] Mengulang proses build dari kondisi yang terdokumentasi.
- [ ] Menetapkan checklist pengujian untuk setiap image.
- [ ] Menguji boot, konfigurasi, dan fungsi inti.
- [ ] Mendokumentasikan known issues.
- [ ] Menetapkan versi dan catatan perubahan.
- [ ] Menyimpan checksum untuk artefak rilis.
- [ ] Menetapkan prosedur backup dan pemulihan proyek.

Deliverables:

- Checklist pengujian.
- Build instructions yang diperbarui.
- Release notes.
- Informasi versi dan checksum image.
- Dokumentasi known issues.

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
