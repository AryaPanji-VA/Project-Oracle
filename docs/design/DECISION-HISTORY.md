# ORACLE-OS — Decision History

Catatan keputusan yang sudah **superseded**, riwayat penting, dan klaim yang
**tidak dapat diverifikasi**. Dokumen ini ada supaya tidak ada yang dihapus
diam-diam.

Dokumen ini **bukan** rujukan aktif. Untuk keputusan yang berlaku, lihat
`MASTER-DESIGN.md`.

Sumber: `docs/DESIGN.md` (v0.1, dibubarkan) dan `docs/DESIGN-ASSETS.md`
(ledger kerja, dibubarkan) pada Stage 3B.1.

---

## 1. Keputusan yang SUPERSEDED

### 1.1 "Rasio kontras wajib diukur saat implementasi"

**Dari:** `DESIGN.md` §2, kalimat terakhir.

> "Rasio kontras final per pasangan warna wajib diukur saat implementasi,
> bukan diasumsikan dari tabel ini."

**Status:** SUPERSEDED — sudah dilakukan, bukan lagi tugas masa depan.

**Digantikan oleh:** `MASTER-DESIGN.md` §10.1 dan §4. Semua pasangan warna
sudah diukur dengan rumus WCAG relatif luminans dan dicatat dengan angka.

**Nilai riwayat:** kalimat ini benar sebagai prinsip. Yang berubah hanya
statusnya: dari "belum" menjadi "sudah".

---

### 1.2 IBM Plex Sans Condensed sebagai display font

**Dari:** `DESIGN.md` §3 dan §7 butir 2.

> "Display | IBM Plex Sans Condensed | **Belum diverifikasi.**"

**Status:** **SUPERSEDED — dicoret sepenuhnya.**

**Bukti:** `DESIGN-ASSETS.md` §4 mengaudit `Packages.gz` trixie:
`fonts-ibm-plex` **tidak ada**, dan pencarian nama mengandung "plex" hanya
mengembalikan paket tidak relevan.

**Digantikan oleh:** `MASTER-DESIGN.md` §5.1. Inter menjadi satu-satunya
font UI. Tata letak tidak boleh bergantung pada display font.

**Catatan:** fallback yang diantisipasi dokumen lama sudah benar — Inter
memang menjadi jawabannya.

---

### 1.3 Wallpaper "tipografis"

**Dari:** `DESIGN.md` §4 dan §7 butir 4.

> "Wallpaper | Tipografis" / "Berkas wallpaper tipografis: teks, komposisi,
> dan ukuran kanvas [belum diputuskan]."

**Status:** SUPERSEDED — arah berubah.

**Digantikan oleh:** `MASTER-DESIGN.md` §7. Wallpaper final memakai **Dial
sebagai watermark Dusty 18%** plus motto "Work with clarity.", bukan
tipografi sebagai elemen utama.

**Mengapa berubah:** Dial adalah aset identitas paling kuat yang dimiliki
proyek. Wallpaper tipografis akan menduplikasi motto yang sudah ada di
panel/desktop, sementara Dial memberi tanda yang tidak bisa disalahartikan.

---

### 1.4 Geometri Dial hasil pengukuran preview

**Dari:** `DESIGN-ASSETS.md` §2.

| Parameter | Nilai terukur (lama) | Nilai final | Selisih |
|---|---:|---:|---|
| stroke/Ø | 0,130 | **0,1250** | −0,005 |
| tick_h/Ø | 0,402 | **0,3913** | −0,011 |
| protrude/Ø | 0,065 | **0,0543** | −0,011 |
| tick_w/Ø | 0,1087 | 0,1087 | sama |
| cap/Ø | 0,511 | 0,5109 | sama |
| gap/Ø | 0,457 | 0,4565 | sama |

**Status:** SUPERSEDED.

**Mengapa berbeda:** DESIGN-ASSETS mengukur **piksel preview** yang sudah
melalui rasterisasi. Tepi stroke dan anti-aliasing membuat angka pengukuran
lebih besar dari geometri sebenarnya.

**Digantikan oleh:** `ASSET-README.md` §2 — spesifikasi generator yang
diverifikasi `audit_assets.py` dengan IoU 0,902 terhadap render font asli.

**Pelajaran:** mengukur raster bukan cara menentukan geometri vektor.

---

### 1.5 Tabel optical variant per ukuran

**Dari:** `DESIGN-ASSETS.md` §2.1.

| Target | Stroke/Ø | Tick gap |
|---|---:|---:|
| 48 px | 0,179 | 9,6% Ø |
| 32 px | 0,170 | 9,4% Ø |
| 24 px | 0,175 | 11,0% Ø |
| 16 px | 0,192 | 13,5% Ø |

**Status:** SUPERSEDED — pendekatannya salah.

**Mengapa:** tabel ini menyiratkan **empat** varian (satu per ukuran). Hasil
produksi menunjukkan hanya **dua** yang dibutuhkan: master (dipakai 24 px ke
atas) dan optical-16.

**Digantikan oleh:** `ASSET-README.md` §2.1 — master untuk 24 px+, optical
untuk ≤16 px. Terbukti dengan pengukuran simetri: master memberi celah
`(2,1)` di 16 px, optical memberi `(2,2)`.

**Pelajaran:** masalah optik pada ukuran kecil tidak perlu diselesaikan
dengan interpolasi per ukuran; satu varian yang disesuaikan sudah cukup.

---

### 1.6 Palet ANSI 16 warna versi lama

**Dari:** `DESIGN-ASSETS.md` §5.

| # | Nama | Hex lama | Kontras lama |
|---|---|---|---|
| 0 | black | `#333A3F` | 10,41 |
| 1 | red | `#9C3A2C` | 6,19 |
| 2 | green | `#4A6B3F` | 5,46 |
| 3 | yellow | `#8C6A1F` | 4,51 |
| 4 | blue | `#2E5A78` | 6,64 |
| 5 | magenta | `#714B6E` | 6,45 |
| 6 | cyan | `#2E6B6B` | 5,51 |
| 7 | white | `#5F666D` | 5,24 |
| 8 | bright black | `#5A6268` | 5,59 |
| 9 | bright red | `#B2452F` | 5,00 |
| 10 | bright green | `#42763A` | 4,87 |
| 11 | bright yellow | `#7A5C15` | 5,61 |
| 12 | bright blue | `#2A6690` | 5,56 |
| 13 | bright magenta | `#6E3F6C` | 7,30 |
| 14 | bright cyan | `#1F7676` | 4,84 |
| 15 | bright white | `#7E838A` | 3,44 |

**Status:** SUPERSEDED — dihitung ulang dengan metode berbeda.

**Mengapa berbeda:** versi lama memilih warna dengan **mata** lalu mengukur
kontrasnya. Versi final memilih **lightness tertinggi yang masih lolos
5:1** secara algoritmik, dengan saturasi dikunci 0,50 dan hue ANSI standar.

**Digantikan oleh:** `MASTER-DESIGN.md` §4.1.

Perbedaan pendekatan yang penting:

| Aspek | Lama (DESIGN-ASSETS) | Final (MASTER) |
|---|---|---|
| Ambang | 4,5 slot 0–7; 3,0 slot 8–15 | **4,5 semua slot teks** |
| "Bright" | lebih terang | **lebih pekat** (light theme) |
| Slot 7 | `#5F666D` (5,24) | `#667D89` Dusty (3,89, UI saja) |
| Metode | pilih-mata lalu ukur | algoritmik: L maksimum yang lolos |

**Kesalahan lama yang diperbaiki:** menganggap "bright" = lebih terang. Di
latar terang, bright yang lebih terang justru menghilang.

**Yang dipertahankan dari versi lama:** ide bahwa slot 8–15 boleh di bawah
4,5:1 karena dipakai sebagai aksen. Versi final memilih lebih ketat —
semua slot teks ≥4,5:1 — dan hanya menyisakan slot 7/8/15 sebagai
peran latar.

---

### 1.7 "Tidak ada direktori `scalable` di Papirus Debian"

**Dari:** `DESIGN-ASSETS.md` §4.

> "**Tidak ada direktori `scalable`** di paket Debian ini — jadi setiap
> referensi ikon harus menunjuk ukuran raster yang ada."

**Status:** **TIDAK DIVERIFIKASI ULANG** — berpotensi keliru.

Daftar ukuran yang tercatat: `8/16/18/22/24/32/42/48/64/84/96/128 px` plus
`@2x`. Stage 2F-A menemukan struktur yang sama, tetapi **tidak** secara
khusus memeriksa keberadaan direktori `scalable`.

**Dampak:** rendah. Aset Papirus yang dipakai semuanya SVG raster-per-ukuran,
jadi referensi tetap valid. Klaim ini tidak dipakai untuk keputusan apa pun.

---

### 1.8 "Nama ikon Papirus: `xfce4-terminal` tidak ada, pakai `org.xfce.terminal`"

**Dari:** `DESIGN-ASSETS.md` §4.

**Status:** SUPERSEDED — koreksi sebagian.

Stage 2F-A menguji ulang dan menemukan:

| Nama | Klaim lama | Temuan Stage 2F-A |
|---|---|---|
| `org.xfce.terminalemulator` | (tidak disebut) | **ADA** di Papirus penuh |
| `org.xfce.terminal` | ada | ada |
| `utilities-terminal` | ada | ada |
| `xfce4-terminal` | tidak ada | **benar tidak ada** |

**Yang berubah:** `.desktop` XFCE di image memakai
`Icon=org.xfce.terminalemulator`, bukan `org.xfce.terminal`. Stage 2F-A
memetakan nama yang **benar-benar dipakai**, bukan nama yang dikira dipakai.

**Digantikan oleh:** `ASSET-DOCUMENTATION.md` §6.

---

### 1.9 Daftar 22 greeter widget ID

**Dari:** `DESIGN-ASSETS.md` §7.

> "ID CSS greeter yang sah sudah diverifikasi dari
> `lightdm-gtk-greeter.glade` tag `lightdm-gtk-greeter-2.0.9` — gunakan yang
> ini, jangan menebak."

Diklaim 22 ID. Diverifikasi ulang terhadap **binary** 2.0.9 (Stage 3B.1):

| Status | Jumlah | ID |
|---|---:|---|
| ADA | **18** | `login_window`, `panel_window`, `menubar`, `password_entry`, `username_entry`, `login_button`, `user_image`, `user_image_border`, `user_combobox`, `message_label`, `greeter_infobar`, `power_window`, `power_icon`, `power_title`, `power_text`, `power_ok_button`, `power_cancel_button`, `screen_overlay` |
| TIDAK ADA | 5 | `login_box`, `cancel_button`, `power_menu`, `power_buttonbox_frame`, `power_content_frame` |

**Status:** SUPERSEDED sebagian — 18 dari 22 terkonfirmasi, 5 tidak.

**Catatan penting soal `cancel_button`:** tidak ada literal string di binary,
**tetapi** CSS ORACLE memakainya dan preview GTK 3.24.52 berhasil menatanya.
Kemungkinan widget dibuat runtime lewat kode, bukan `.glade`. **Tidak dapat
dipastikan dari binary** — lihat §3.

**Digantikan oleh:** `MASTER-DESIGN.md` §12.3 (18 ID terverifikasi).

**Pelajaran:** `.glade` adalah sumber desain, bukan bukti runtime. Yang
menentukan adalah binary yang benar-benar dijalankan.

---

### 1.10 Enam hal "sengaja belum diputuskan"

**Dari:** `DESIGN-ASSETS.md` §8.

| # | Pertanyaan lama | Jawaban final | Status |
|---|---|---|---|
| 1 | Tema GTK3: turunan Arc atau dari nol | **Turunan Arc** — Stage 2C | selesai |
| 2 | Muted Brass di indikator status | **Ya, latar gelap saja** (4,24:1) | selesai |
| 3 | Susunan plugin panel | 8 atas / 7 bawah — Stage 2D | selesai |
| 4 | Skala tipografi 1280×800 | Inter 11 / JetBrains Mono 11 | selesai |
| 5 | Tata letak tombol XFWM4 | **belum** — di luar scope Stage 2 | **masih terbuka** |
| 6 | Ring 18% dinaikkan untuk presentasi | **Tidak** — v0.1 tetap 18% | selesai |

---

## 2. Yang dipertahankan dari dokumen lama (tidak superseded)

Informasi ini masih berlaku dan sudah dipindahkan ke dokumen aktif:

| Isi | Dari | Ke |
|---|---|---|
| Karakter "Creative and Professional", nada, target pengguna, distribusi | DESIGN.md §1 | MASTER §1 |
| Aturan pemakaian palet (paragraf) | DESIGN.md §2 | MASTER §2.1 |
| Definisi Classic layout (tak ada panel samping/mengambang/autohide) | DESIGN.md §4 | MASTER §6.1 |
| Alasan dock = panel kedua | DESIGN.md §4 | MASTER §6.2 |
| **Larangan Plank + konsekuensi diterima** | DESIGN.md §5.2 | MASTER §6.3 |
| Prinsip penilaian 5 butir | DESIGN.md §8 | MASTER §15 |
| Greeter tak punya skin CSS eksternal | DESIGN-ASSETS §3.1 | MASTER §12.1 |
| Panel `panel-<id>` class ada | DESIGN-ASSETS §3.3 | MASTER §8.4 |
| Precedence config greeter | DESIGN-ASSETS §3.2 | INTEGRATION §3.4 |
| Kanvas master 512 px | DESIGN-ASSETS §2 | ASSET-DOC §1.2 |
| Papirus 22,6 MB (paket terbesar) | DESIGN-ASSETS §4 | ASSET-DOC §11 |
| Daftar aset A1–E2 | DESIGN-ASSETS §7 | ASSET-DOC §1–9 |
| 7 keputusan implementasi terkunci | DESIGN-ASSETS §1.3 | MASTER §6, §7, §12 |

---

## 3. Klaim yang TIDAK dapat diverifikasi

Dicatat jujur. Tidak dihapus, tetapi **tidak** dipakai sebagai dasar
keputusan.

| # | Klaim | Mengapa tidak terverifikasi |
|---|---|---|
| 1 | `cancel_button` sebagai widget ID yang bisa ditata | tidak ada literal di binary; mungkin dibuat runtime. Preview GTK berhasil menatanya — bukti tidak konklusif |
| 2 | Ukuran `.deb` di DESIGN-ASSETS §4 (0,8 MB / 22,6 MB / dst) | diukur sekali 2026-11-01, tidak diukur ulang |
| 3 | "Tidak ada direktori `scalable`" di Papirus | tidak diperiksa khusus di Stage 2F-A |
| 4 | Palet ANSI lama 16/16 lolos | dihitung dengan ambang berbeda (slot 8–15 pakai 3:1); tidak diaudit ulang karena sudah superseded |
| 5 | "Papirus 22,6 MB" sebagai dampak ukuran ISO | belum dibuktikan lewat build nyata |
| 6 | Klaim "diverifikasi dari `.glade`" untuk 22 ID | 5 dari 22 tidak ada di binary — sumber desain ≠ bukti runtime |

---

## 4. Baseline Stage 0 (historis)

Dari `DESIGN.md` §6 — kondisi image sebelum pekerjaan desain. Disimpan
sebagai titik nol, **bukan** kondisi sekarang.

| Area | Kondisi aktual (ISO Phase 2, 2026-11-01) | Target saat itu |
|---|---|---|
| XFCE | 4.20 terpasang | tetap |
| XFWM4 | 4.20.0, tanpa `/etc/xdg/xfwm4/` | konfigurasi eksplisit |
| Panel | `default.xml` bawaan upstream | susunan ORACLE |
| Dock | belum ada | Panel XFCE kedua |
| Ikon | Adwaita, default, hicolor, locolor | Papirus |
| Kursor | tidak ada tema khusus | DMZ |
| GTK theme | tujuh tema bawaan | belum ditetapkan |
| Font | DejaVu saja | Inter + JetBrains Mono |
| `gtk-3.0/settings.ini` | tidak ada | ada |
| Greeter | `[greeter]` kosong | identitas ORACLE |
| Plank | tidak terpasang | tetap tidak dipakai |

**Status sekarang (2026-11-03):** aset sudah ada di repo, tetapi **belum
aktif di runtime**. Panel `default.xml` dan `terminalrc` sudah di lapisan
XDG; tema, ikon, wallpaper, colorscheme, dan greeter menunggu aktivasi
(Stage 3C+). Lihat `ASSET-DOCUMENTATION.md` kolom status.

---

## 5. Riwayat tahap

| Tahap | Hasil | Commit |
|---|---|---|
| Stage 2C | GTK theme (Arc fork, 124 PNG) | — |
| Stage 2D | XFCE panel | — |
| Stage 2E | Terminal ANSI 16-color | — |
| Stage 2F-A | Papirus recolor terbatas | — |
| Stage 2F-B | LightDM greeter | — |
| Stage 3A | merge 573 file ke repo utama | `468e3e6` |
| Stage 3B | 7 paket dependency | `662045a` |
| Stage 3B.1 | rekonsiliasi dokumentasi | (dokumen ini) |

Design repository (`~/Projects/oracle-brand-assets`) tetap menjadi arsip
lengkap termasuk generator, preview, dan dokumen audit per tahap.

---

## 6. Pelajaran yang terbawa

1. **Ukur runtime, bukan desain.** `.glade` dan sample CSS bisa berbeda dari
   binary yang berjalan.
2. **Raster ≠ vektor.** Geometri ditentukan dari spesifikasi generator, bukan
   dari piksel preview.
3. **"Bright" bergantung konteks.** Di light theme, bright = lebih pekat.
4. **Verifikasi nama, bukan asumsi nama.** `org.xfce.terminalemulator` vs
   `org.xfce.terminal` — beda satu kata, beda hasil.
5. **Klaim tanpa bukti runtime tetap klaim.** Dicatat di §3, bukan dihapus.