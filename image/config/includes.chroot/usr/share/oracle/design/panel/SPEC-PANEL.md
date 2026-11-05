# ORACLE-OS — XFCE Panel: Spesifikasi Visual

Stage 2D. Retro Industrial, Light-first, Classic, Flat.
Dua panel terpisah: satu di atas (status) dan satu di bawah (dock).
Bukan Plank/Cairo-Dock — keduanya adalah `xfce4-panel` dengan konfigurasi
berbeda.

---

## 1. Konsep

Panel atas adalah **instrumen** — gelap, tenang, seperti bibir alat ukur.
Panel bawah adalah **baki** — terang, mengambang, tempat alat yang sering
dipakai.

Keduanya sengaja berbeda warna. Ini konsep Classic XFCE (panel status dan
dock terpisah) yang dipakai apa adanya, bukan ditiru dari dock modern.
Pemisahan gelap/terang membuat mata langsung tahu mana yang mengontrol
seluruh layar (atas) dan mana yang berisi alat (bawah).

---

## 2. Panel atas — status bar

| Properti | Nilai | Dasar |
|---|---|---|
| Posisi | `p=6` (NW, kiri atas) | enum `SnapPosition` |
| Tinggi | **32 px** | ≤ `Z_TOP_PX` 72 wallpaper |
| Panjang | 100 % | full width |
| Icon size | 18 px | — |
| Latar | Steel `#344653`, alpha 1.0 | `background-style=1` |
| Teks | Porcelain `#F5F3EC` | 8.81:1 |
| Teks sekunder | Ivory `#E9E5DA` | 7.77:1 |
| Aksen aktif | Muted Brass `#B8A98D` | 4.24:1 |
| Border bawah | `#2A3A45` 1 px | pemisah dari wallpaper |
| Autohide | never | panel status tidak disembunyikan |
| Position locked | true | — |

### Isi, kiri ke kanan

| # | Plugin | Peran |
|---|---|---|
| 1 | `applicationsmenu` | Dial mark + label "Applications" |
| 2 | `launcher` Terminal | pintasan cepat |
| 3 | `launcher` Files | pintasan cepat |
| 4 | `separator` style 0 expand | spacer elastis |
| 5 | `tasklist` | jendela aktif, grouping=1 |
| 6 | `separator` style 0 expand | spacer elastis |
| 7 | `systray` | tray, square-icons |
| 8 | `clock` | `%H:%M`, 24 jam |

### Peran warna di panel atas

- **Steel** adalah latar. Satu-satunya bidang gelap besar di desktop.
  Ia menyeimbangkan wallpaper terang dan menandai "ini kontrol sistem".
- **Porcelain** untuk semua teks dan ikon. Kontras 8.81:1 — jauh di atas
  ambang, karena teks panel kecil (11 px) dan sering dilihat sekilas.
- **Muted Brass** hanya untuk **indikator aktif tasklist** — garis 2 px di
  bawah jendela yang sedang fokus. Ini satu-satunya tempat warna brass
  muncul di panel atas. Bukan dekorasi: ini penanda state.
- **Dusty Blue ditolak** di panel atas (2.26:1). Tidak dipakai.

### Kenapa 32 px

Wallpaper menyisakan `Z_TOP_PX = 72` px. 32 px meninggalkan 40 px ruang
napas di atas motto "Work with clarity.". Panel 40 px akan terasa berat dan
menekan motto; panel 24 px membuat target klik terlalu kecil untuk
`tasklist`. 32 px adalah titik tengah yang masih nyaman diklik.

---

## 3. Panel bawah — dock

| Properti | Nilai | Dasar |
|---|---|---|
| Posisi | `p=10` (SC, bawah tengah) | enum `SnapPosition` |
| Tinggi | **48 px** | ≤ `Z_BOTTOM_PX` 104 wallpaper |
| Panjang | **27.08%** viewport (`length` = persen 1–100, `length-adjust=true`) | 7 item; 520 px @1920 |
| Icon size | 32 px | — |
| Latar | Porcelain `#F5F3EC`, alpha 1.0 | `background-style=1` |
| Border | Dusty `#667D89` 1 px | 3.89:1 vs Porcelain |
| Ikon | Steel `#344653` | 8.81:1 |
| Aksen aktif | Brass Ink `#8C7B58` | 3.72:1 |
| Jarak dari dasar | 16 px | `BOTTOM_GAP_PX` |
| Autohide | never | dock harus selalu terjangkau |
| Position locked | true | — |

### Isi, kiri ke kanan

| # | Plugin | Peran |
|---|---|---|
| 11 | `showdesktop` | sembunyikan semua jendela |
| 12 | `separator` style 1, size 8 | garis pemisah |
| 13 | `launcher` Terminal | — |
| 14 | `launcher` Files | — |
| 15 | `launcher` Web Browser | — |
| 16 | `launcher` App Finder | — |
| 17 | `separator` style 1, size 8 | garis pemisah |

### Border wajib, bukan pilihan

Porcelain `#F5F3EC` di atas Warm Ivory `#E9E5DA` = **1.13:1**. Tanpa border,
dock akan menyatu dengan wallpaper dan batasnya tidak terbaca. Dusty Blue
memberi 3.89:1 — jelas terlihat, tapi tetap tipis 1 px sehingga tidak jadi
garis berat.

Ini satu-satunya tempat Dusty Blue muncul sebagai elemen struktural. Di
tempat lain Dusty hanya dipakai sebagai watermark (opacity 18%).

### Kenapa 48 px dan 27.08%

48 px tinggi memberi ikon 32 px dengan margin 8 px atas-bawah — cukup untuk
target klik nyaman tanpa terlihat gemuk. Panjang dinyatakan sebagai **persen**,
bukan piksel: xfce4-panel menyimpan `length` sebagai persen 1–100
(`g_param_spec_double("length", 1, 100, 10)`; setter membagi 100), lalu render
memakai `panel_width = CLAMP(natural_plugin_width, area_width × length/100, area_width)`.

`27.08% = 520/1920`, sehingga pada 1920 px hasilnya 520 px — 7 item × ~56 px
plus padding; cukup untuk 4 launcher mayor, tidak lebih. Pada 1280 px hasilnya
346 px, proporsional. Menulis nilai piksel (`520`) ke properti ini membuat nilai
ditolak dan panel jatuh ke default 10% — itu bug R2 yang diperbaiki Stage 3G.

Dock yang terlalu panjang berhenti terasa seperti baki dan mulai terasa seperti
panel kedua.

### Kenapa Brass Ink, bukan Muted Brass

Muted Brass di Porcelain hanya 2.08:1 — gagal. Brass Ink 3.72:1 — lolos.
Aturan ini sudah ditetapkan di aset brand: Muted Brass untuk latar gelap,
Brass Ink untuk latar terang. Panel mengikuti aturan yang sama.

---

## 4. Perilaku state

Tidak ada opsi xfconf untuk warna state per plugin. Sorotan tombol
mengikuti state GTK dari `gtk.css` ORACLE yang sudah disetujui:

| State | Sumber |
|---|---|
| hover | `gtk.css` — button:hover |
| active/checked | `gtk.css` — button:active |
| focus | `gtk.css` — outline Dusty |
| disabled | `gtk.css` — `#767877` |
| selected (tasklist aktif) | `gtk.css` + garis Brass dari tasklist |

Konsekuensi: tampilan tombol panel **konsisten dengan aplikasi lain** karena
berbagi tema yang sama. Ini alasan tidak perlu tema panel terpisah.

---

## 5. Yang sengaja TIDAK dipakai

| Hal | Alasan |
|---|---|
| Transparansi / blur | tanpa compositor; alpha 1.0 |
| Separator style HANDLE / DOTS | tekstur titik bertabrakan dengan garis tipis |
| Whisker Menu | bukan paket bawaan; `applicationsmenu` cukup klasik |
| `docklike` plugin | batasan desain: tidak boleh dock-like plugin |
| Autohide | panel status dan dock harus selalu terlihat |
| Tema panel terpisah | satu `gtk.css` untuk semua |
| Gradien / shadow | Flat |

---

## 6. Preview

| File | Isi |
|---|---|
| `preview/panel-on-wallpaper-1920x1200.png` | **utama** — skala 1:1 di atas wallpaper Workspace |
| `preview/panel-mockup.png` | skematis, lebar dinormalkan |
| `preview/panel-kontras.png` | contoh warna + angka kontras |
| `preview/spec.txt` | angka terukur, teks |

Semua diberi label **MOCKUP STATIS**. Ini gambar yang dibuat dari warna dan
ukuran yang sama dengan konfigurasi, **bukan** tangkapan layar XFCE.

Verifikasi terukur pada preview 1:1:
- panel atas mengisi baris 0–31 → **32 px**
- dock mengisi baris 1137–1183 → **47 px** (1 px border menyatu dengan tepi)
- jarak dock ke dasar layar → **16 px**
- tidak ada tabrakan dengan motto maupun Dial watermark