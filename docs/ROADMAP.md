# ORACLE OS — Project Roadmap

> **Status:** Early Development  
> **Versi roadmap:** 0.1.0  
> **Base distribution:** Arch Linux  
> **Build system:** Archiso  
> **Testing environment:** QEMU virtual machine  
> **Project focus:** Linux systems learning and isolated cybersecurity lab

## 1. Project Vision

ORACLE OS adalah distribusi Linux eksperimental yang dikembangkan untuk mempelajari cara kerja sistem operasi Linux, membangun lingkungan cybersecurity yang terisolasi, dan mengembangkan tooling sistem sendiri.

Pengembangan dimulai dengan menggunakan kernel Linux yang sudah tersedia dan membangun distribusi berbasis Arch Linux. Pengembangan kernel sendiri merupakan tujuan jangka panjang yang akan dikerjakan sebagai proyek riset terpisah.

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

**Status:** In Progress

**Goal:** Menetapkan identitas, ruang lingkup, dan struktur dasar proyek sebelum membangun sistem.

Tasks:

- [x] Membuat repository Git untuk ORACLE OS.
- [x] Membuat README awal.
- [x] Membuat struktur direktori awal.
- [ ] Menetapkan spesifikasi proyek secara tertulis.
- [ ] Mendokumentasikan arsitektur dan keputusan teknis.
- [ ] Menetapkan workflow development dan testing.
- [ ] Memverifikasi konfigurasi proyek dan struktur repository.

Deliverables:

- `README.md`
- `docs/ROADMAP.md`
- `config/oracle.conf`
- `docs/ARCHITECTURE.md`
- `docs/DEVELOPMENT.md`

**Acceptance criteria:**

- Tujuan dan batasan ORACLE OS terdokumentasi.
- Struktur proyek dipahami dan konsisten.
- Keputusan teknis utama memiliki alasan yang jelas.
- Tidak ada perubahan pada sistem utama yang diperlukan untuk menyelesaikan tahap ini.

### Phase 1 — First Bootable ORACLE OS

**Status:** Planned

**Goal:** Menghasilkan image Linux minimal berbasis Arch Linux menggunakan Archiso dan membuktikan bahwa image tersebut dapat di-boot.

Tasks:

- [ ] Memahami cara kerja Archiso.
- [ ] Menentukan lingkungan build yang aman dan terpisah.
- [ ] Menyiapkan profil image minimal ORACLE OS.
- [ ] Menentukan paket awal yang benar-benar diperlukan.
- [ ] Menjalankan proses build image.
- [ ] Memverifikasi file image dan hasil build.
- [ ] Menjalankan image menggunakan QEMU.
- [ ] Mendokumentasikan hasil pengujian dan masalah yang ditemukan.

Deliverables:

- Profil build ORACLE OS.
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
- B