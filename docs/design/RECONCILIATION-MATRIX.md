# Reconciliation Matrix — DESIGN.md & DESIGN-ASSETS.md

Stage 3B.1, 2026-11-03. Dokumen kerja: dasar keputusan rekonsiliasi.
Sumber: `docs/DESIGN.md` (187 baris), `docs/DESIGN-ASSETS.md` (422 baris),
`docs/design/MASTER-DESIGN.md` (179 baris), `docs/design/INTEGRATION-READINESS.md`,
`docs/design/ASSET-README.md`, dan kondisi repository setelah Stage 3A/3B.

---

## Ringkasan

| Dokumen lama | Baris | Nasib | Tujuan |
|---|---:|---|---|
| `docs/DESIGN.md` | 187 | **dibubarkan** | isi → MASTER-DESIGN |
| `docs/DESIGN-ASSETS.md` | 422 | **dibubarkan** | isi → MASTER-DESIGN + ASSET-DOCUMENTATION + riwayat |

Tidak ada informasi yang dihapus tanpa jejak. Yang usang ditandai
**SUPERSEDED** beserta alasannya di `docs/design/DECISION-HISTORY.md`.

---

## A. `docs/DESIGN.md` → MASTER-DESIGN

| § | Isi lama | Status | Tindakan |
|---|---|---|---|
| 1 | Identitas: arah visual, mode, **karakter "Creative and Professional"**, nada, target pengguna, distribusi | **sebagian baru** | Karakter/target/distribusi **belum ada** di MASTER → pindahkan |
| 2 | Palet 6 warna + aturan pemakaian (paragraf) | **aturan baru** | MASTER hanya punya tabel; paragraf aturan → pindahkan |
| 2 | Kalimat "rasio kontras wajib diukur saat implementasi" | **usang** | Sudah diukur semua. Tandai SUPERSEDED → rujuk §6 MASTER |
| 3 | Tipografi: Inter, JetBrains Mono, **IBM Plex Sans Condensed (belum verifikasi)** | **usang sebagian** | IBM Plex **terbukti tidak ada di trixie** (DESIGN-ASSETS §4) → tandai SUPERSEDED |
| 3 | Aturan: Inter untuk UI, JetBrains untuk terminal + nilai teknis | **baru** | Belum ada di MASTER → pindahkan |
| 3 | "Ukuran/ketebalan diuji pada 1280×800" | **baru** | Pindahkan sebagai syarat uji |
| 4 | Desktop: XFCE 4.20, classic layout, flat, wallpaper tipografis | **sebagian** | MASTER punya layout; **alasan "dock = panel kedua"** belum ada → pindahkan |
| 4 | Definisi Classic layout (tak ada panel samping/mengambang/autohide) | **baru** | Pindahkan |
| 5.2 | **Larangan Plank** + konsekuensi diterima | **baru** | Belum ada di MASTER → pindahkan (penting: keputusan arsitektural) |
| 5.3 | Ikon Papirus, kursor DMZ + "default sistem, bukan skel" | **sebagian** | Alasan skel ada di INTEGRATION §3.5; rujuk, jangan duplikasi |
| 5.4 | LightDM: identitas ORACLE, autologin tidak berubah | **sebagian** | Detail ada di AUDIT-GREETER; ringkas + rujuk |
| 5.5 | `--apt-recommends false` → semua eksplisit | **sebagian** | Ada di INTEGRATION §0; rujuk |
| 6 | **Kondisi aktual vs target** (tabel 12 baris, Stage 0) | **historis** | Sudah tidak akurat (banyak target tercapai). Pindahkan ke DECISION-HISTORY sebagai baseline |
| 7 | **7 hal belum diputuskan** | **usang seluruhnya** | Semua sudah diputuskan. Petakan satu per satu ke keputusan final di DECISION-HISTORY |
| 8 | **Prinsip penilaian** (5 butir) | **baru** | Belum ada di MASTER → pindahkan |

### A.1 Tujuh hal "belum diputuskan" — semuanya sudah terjawab

| # | Pertanyaan lama | Jawaban final |
|---|---|---|
| 1 | Tema GTK3 dasar | **Turunan Arc** (`arc-theme`), bukan dari nol — Stage 2C |
| 2 | IBM Plex Sans Condensed | **Tidak ada di trixie**. Dicoret. Inter satu-satunya UI font |
| 3 | Susunan plugin panel | Final: 8 plugin atas, 7 plugin bawah — Stage 2D |
| 4 | Wallpaper tipografis | **Bukan tipografis**. Dial watermark + motto — Stage 2 |
| 5 | Skala tipografi | Inter 11 (UI), JetBrains Mono 11 (terminal) |
| 6 | Tata letak tombol XFWM4 | **Belum dikerjakan** — di luar scope Stage 2 |
| 7 | Muted Brass di indikator status | **Ya, di latar gelap saja** (4.24:1). Brass Ink di latar terang |

Catatan: #6 **masih terbuka** — jujur dicatat, bukan diklaim selesai.

### A.2 Konflik angka: geometri Dial

| Parameter | DESIGN-ASSETS §2 (terukur) | ASSET-README (final) | Selisih |
|---|---:|---:|---|
| stroke/Ø | 0,130 | **0,1250** | −0,005 |
| tick_h/Ø | 0,402 | **0,3913** | −0,011 |
| tick_w/Ø | 0,1087 (= 12px) | **0,1087** | sama |
| protrude/Ø | 0,065 | **0,0543** | −0,011 |
| cap/Ø | 0,511 | **0,5109** | sama |
| gap/Ø | 0,457 | **0,4565** | sama |

**Resolusi:** ASSET-README adalah **spesifikasi generator final** (dipakai
`gen_assets.py`, diverifikasi `audit_assets.py` dengan IoU). DESIGN-ASSETS
mengukur **piksel preview** yang sudah melalui rasterisasi — tepi stroke
dan anti-aliasing membuat angka pengukuran lebih besar. **Yang berlaku:
ASSET-README.** DESIGN-ASSETS §2 ditandai SUPERSEDED dengan alasan ini.

---

## B. `docs/DESIGN-ASSETS.md` → tiga tujuan

| § | Isi lama | Status | Tindakan |
|---|---|---|---|
| 1.1 | Identitas (filosofi, karakter logo, motto, guiding principle) | tercakup | MASTER §1 sudah punya |
| 1.2 | Palet 7 warna | tercakup | MASTER §2 sudah punya |
| 1.3 | 7 keputusan implementasi terkunci | **sebagian baru** | No. 2 (optical 16px), No. 3 (dua wallpaper), No. 6 (styling saja), No. 7 (anotasi tak masuk aset) → pindahkan |
| 2 | Geometri Dial terukur + tabel optical | **digantikan** | ASSET-README lebih akurat → SUPERSEDED |
| 2 | Catatan kanvas 512px | **baru** | Pindahkan (alasan teknis penting) |
| 3.1 | Greeter tak punya skin CSS eksternal | **terverifikasi ulang** | Audit Stage 2F-B mengonfirmasi. Pindahkan ke MASTER sebagai fakta kunci |
| 3.2 | **Precedence config greeter 6 lapis** | **bertentangan** | Lihat B.1 |
| 3.3 | Panel: `panel-<id>` class | **terverifikasi ulang** | Stage 2D mengonfirmasi `panel-%d` ada di source 4.20 |
| 4 | Audit paket + **IBM Plex tidak ada** | **historis penting** | Pindahkan ke DECISION-HISTORY (alasan mencoret display font) |
| 4 | Papirus 22,6 MB | **baru** | Catatan ukuran ISO → ASSET-DOCUMENTATION |
| 4 | Nama ikon Papirus terverifikasi | **sebagian usang** | Stage 2F-A menguji ulang: `org.xfce.terminalemulator` **ADA** di Papirus penuh. Koreksi |
| 5 | **Palet ANSI 16 warna lama** | **digantikan** | Stage 2E menghitung ulang dengan metode berbeda. SUPERSEDED |
| 5 | Catatan xfconf `/color-palette` string | **terverifikasi** | Dikonfirmasi Stage 2E (`ColorPalette=` di `.theme`) |
| 6 | Kontras palet merek + konflik Brass | tercakup | MASTER §2.1 sudah punya versi lebih lengkap |
| 7 | Daftar aset A1–E2 + ID | **historis sangat penting** | Pindahkan ke ASSET-DOCUMENTATION sebagai inventaris asli |
| 7 | 22 greeter ID "diverifikasi dari .glade" | **sebagian salah** | Lihat B.2 |
| 8 | 6 hal belum diputuskan | usang | Petakan di DECISION-HISTORY |
| 9 | Batasan kerja sesi | historis | Ringkas di DECISION-HISTORY |

### B.1 KONFLIK: urutan precedence greeter config

| Sumber | Klaim |
|---|---|
| DESIGN-ASSETS §3.2 | 6 lapis; **`/etc/lightdm/lightdm-gtk-greeter.conf` menang** |
| INTEGRATION-READINESS §3.4 | `/etc/lightdm/lightdm-gtk-greeter.conf` (lapisan 1) menang atas `01_debian.conf` (lapisan 3) |

**Tidak bertentangan secara substansi** — keduanya menyimpulkan file yang
sama menang. DESIGN-ASSETS lebih rinci (6 lapis, termasuk `/etc/xdg/`);
INTEGRATION lebih ringkas (3 lapis). **Resolusi:** MASTER merujuk ke
AUDIT-GREETER §4 sebagai sumber, karena itu yang memisahkan lapisan
`/etc/xdg` dengan benar.

### B.2 KONFLIK: 22 greeter widget ID

DESIGN-ASSETS §7 mengklaim 22 ID "diverifikasi dari `.glade` tag 2.0.9".
Diverifikasi ulang terhadap binary 2.0.9:

| Status | Jumlah | ID |
|---|---:|---|
| **ADA di binary** | **18** | login_window, panel_window, menubar, password_entry, username_entry, login_button, user_image, user_image_border, user_combobox, message_label, greeter_infobar, power_window, power_icon, power_title, power_text, power_ok_button, power_cancel_button, screen_overlay |
| **TIDAK ADA** | **4** | `login_box`, `cancel_button`, `power_menu`, `power_buttonbox_frame`, `power_content_frame` |

**Resolusi:** daftar lengkap 18 ID masuk MASTER (audit Stage 2F-B hanya
menguji 8 — daftar ini **memperluas**, bukan menggantikan). 5 ID yang tidak
ada dicatat di DECISION-HISTORY sebagai klaim yang tidak terbukti.

Catatan: `cancel_button` tidak muncul sebagai literal string, tetapi CSS
ORACLE memakainya dan preview GTK berhasil menatanya. Kemungkinan dibuat
runtime via kode, bukan `.glade`. **Tidak dapat dipastikan dari binary** —
dicatat sebagai belum terverifikasi.

---

## C. Informasi yang TIDAK dapat diverifikasi

| # | Klaim | Mengapa tidak bisa |
|---|---|---|
| 1 | `cancel_button` sebagai widget ID yang dapat ditata | tidak ada literal di binary; mungkin dibuat runtime |
| 2 | Ukuran `.deb` di DESIGN-ASSETS §4 (0,8 MB, 22,6 MB, dst) | diukur sekali di 2026-11-01; tidak diukur ulang |
| 3 | "Tidak ada direktori `scalable` di Papirus Debian" | tidak diperiksa ulang di Stage 2F-A |
| 4 | Angka palet ANSI lama (§5) | digantikan metode baru; tidak diaudit ulang karena sudah SUPERSEDED |
| 5 | "Papirus memakai 22,6 MB" sebagai dampak ISO | belum dibuktikan lewat build |

Semua dicatat sebagai klaim historis, bukan fakta aktif.

---

## D. Struktur dokumentasi final

| Dokumen | Fungsi | Sumber |
|---|---|---|
| `docs/design/MASTER-DESIGN.md` | keputusan & spesifikasi final | DESIGN.md + DESIGN-ASSETS §1,3 + Stage 2 |
| `docs/design/INTEGRATION-READINESS.md` | pemetaan teknis integrasi | tidak berubah |
| `docs/design/ASSET-DOCUMENTATION.md` | **baru** — inventaris aset & status | DESIGN-ASSETS §7 + kondisi repo |
| `docs/design/DECISION-HISTORY.md` | **baru** — keputusan superseded & riwayat | DESIGN.md §6,7 + DESIGN-ASSETS §2,4,5,8,9 |
| `docs/design/ASSET-README.md` | geometri brand A1–A5 | tidak berubah |
| `docs/design/audit-report.txt` | keluaran audit brand | tidak berubah |

Tidak ada duplikasi: MASTER = keputusan; INTEGRATION = cara pasang;
ASSET-DOCUMENTATION = apa yang ada; DECISION-HISTORY = apa yang berubah.