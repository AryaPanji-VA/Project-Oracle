# ORACLE-OS — Master Design Document

Status: **FINAL**. Mencakup A1–A5, Wallpaper, GTK, Panel, Terminal, Papirus,
dan LightDM Greeter. Menggantikan `docs/DESIGN.md` (v0.1) dan
`docs/DESIGN-ASSETS.md` — lihat `DECISION-HISTORY.md` untuk yang berubah.

Dokumen ini adalah rujukan tunggal **keputusan desain**. Bila ada konflik
antara dokumen ini dan dokumen tahap, **dokumen ini yang berlaku**.

Dokumen pendamping:

| Dokumen | Fungsi |
|---|---|
| `ASSET-DOCUMENTATION.md` | inventaris aset, path, status |
| `INTEGRATION-READINESS.md` | cara pasang, dependency, test matrix |
| `DECISION-HISTORY.md` | keputusan superseded, riwayat, klaim tak terbukti |
| `ASSET-README.md` | geometri detail A1–A5 |

---

## 1. Identitas

| Aspek | Keputusan |
|---|---|
| Filosofi | Knowledge |
| Karakter logo | Timeless |
| Logo | Dial (ring + satu index tick) + wordmark ORACLE |
| Nama produk | ORACLE-OS |
| Arah desain | Retro Industrial |
| Tema | Light-first |
| Kedalaman | Flat |
| Layout | Classic XFCE: top panel + centered bottom panel |
| Motto | "Work with clarity." |
| Guiding principle | "Knowledge is never finished." (belum dipasang di UI) |
| Karakter | Creative and Professional |
| Nada | Elegant, restrained, functional |
| Target pengguna | Developer & Security Workstation |
| Distribusi | Community Distro |
| UI font | Inter |
| Terminal font | JetBrains Mono |

### 1.1 Apa arti Retro Industrial

Permukaan datar, tipografi tegas, aksen metalik terbatas, dan penolakan
terhadap dekorasi berlebih. Tidak ada gradien dekoratif, bayangan berlapis,
atau efek kaca.

Kesan "industri" datang dari **struktur** — garis, blok, hierarki — bukan
dari ornamen. Kalau sebuah elemen tidak membawa informasi, ia tidak ada.

### 1.2 Apa arti Light-first

Antarmuka dirancang untuk latar terang sebagai kondisi utama. Ini keputusan
sadar, bukan preferensi:

1. Sesi kerja panjang di ruangan terang tetap nyaman.
2. Dokumentasi dan tangkapan layar untuk materi komunitas konsisten.
3. Terminal bertema terang senada dengan sisa sistem.

Konsekuensi yang diterima: antarmuka ini tidak dirancang untuk ruangan gelap.
Varian gelap **tidak** disediakan.

---

## 2. Palet (terkunci)

| Nama | Hex | Peran |
|---|---|---|
| Warm Ivory | `#E9E5DA` | latar desktop, latar greeter |
| Soft Porcelain | `#F5F3EC` | permukaan, panel bawah, terminal |
| Steel Blue | `#344653` | panel atas, headerbar, aksen utama |
| Dusty Blue | `#667D89` | watermark, border, indikator |
| Muted Brass | `#B8A98D` | aksen di latar **gelap** saja |
| Graphite | `#30363B` | teks utama |
| Brass Ink | `#8C7B58` | aksen di latar **terang** saja |

### 2.1 Aturan pemakaian

- **Warm Ivory** adalah latar default. **Soft Porcelain** hanya untuk
  permukaan yang benar-benar terangkat satu tingkat (dialog, menu, kolom
  masukan, panel bawah, terminal). Jangan memakainya untuk latar halaman.
- **Steel Blue** adalah satu-satunya warna aksi utama. Satu aksen dominan per
  layar.
- **Muted Brass** adalah aksen, bukan warna fungsional. Tidak untuk teks
  panjang, tidak untuk indikator status di latar terang.
- **Graphite** untuk teks.
- **Dusty Blue** tidak dipakai sebagai warna teks utama pada latar terang.

### 2.2 Aturan Brass (terukur, tidak bisa ditukar)

| Warna | di Steel (gelap) | di Porcelain (terang) |
|---|---:|---:|
| Muted Brass `#B8A98D` | **4.24:1** ✓ | 2.08:1 ✗ |
| Brass Ink `#8C7B58` | 2.37:1 ✗ | **3.72:1** ✓ |

Muted Brass **hanya** untuk latar gelap; Brass Ink **hanya** untuk latar
terang. Ini bukan preferensi — sudah dihitung.

### 2.3 Kontras palet terhadap kedua permukaan

Diukur WCAG 2.x terhadap latar yang relevan. Angka ini yang dipakai untuk
setiap keputusan di dokumen ini.

| Pasangan | Rasio | Status |
|---|---:|---|
| Graphite di Warm Ivory | **9.72** | lolos teks normal |
| Graphite di Soft Porcelain | **11.02** | lolos teks normal |
| Steel Blue di Warm Ivory | **7.77** | lolos teks normal |
| Steel Blue di Soft Porcelain | **8.81** | lolos teks normal |
| Soft Porcelain di Steel Blue | **8.81** | lolos teks di panel atas |
| Dusty Blue di Warm Ivory | **3.43** | gagal teks normal; lolos UI 3:1 |
| Muted Brass di Warm Ivory | **1.83** | **gagal semua ambang** |
| Muted Brass di Steel Blue | **4.24** | lolos teks besar; gagal teks normal |
| Brass Ink di Warm Ivory | **3.28** | lolos teks besar; gagal teks normal |
| Ring Dusty 18% di Ivory (`#D1D3CC`) | **1.21** | dekoratif — memang benar |

**Konsekuensi:**
- **Muted Brass tidak boleh** dipakai untuk teks atau ikon fungsional di latar
  terang (1.83:1). Aman sebagai tick logo di atas Steel (4.24:1) atau elemen
  dekoratif murni.
- **Dusty Blue** hanya sah untuk teks besar atau elemen UI non-teks di latar
  terang. Untuk teks badan, pakai Steel Blue.
- **Ring wallpaper 18%** menghasilkan `#D1D3CC` — praktis tak terlihat
  (1.21:1). Itu **memang** tujuannya (watermark), tetapi berarti wallpaper
  tidak akan terbaca di proyeksi/ruangan terang.

---

## 3. Warna turunan (terdokumentasi)

Warna di luar 7 palet resmi, semuanya punya alasan terukur:

| Hex | Peran | Alasan |
|---|---|---|
| `#B9C1C2` | border GTK/Papirus/greeter | dekoratif, 1.65:1 (bukan indikator) |
| `#5E6C75` | headerbar active | state, bukan warna baru |
| `#4B5B65` | headerbar hover | state |
| `#27343E` | shadow dalam | turunan Steel |
| `#1F2A33` | shadow terdalam | turunan Steel |
| `#6B7480`, `#7A8188` | netral menengah | turunan Graphite/Dusty |
| `#E6E5E0`, `#D6D7D4` | button hover/active | turunan Ivory |
| `#F2F0E9` | row hover | turunan Ivory |
| `#D1D3CC` | blend Dial wallpaper | Dusty 18% di atas Ivory |
| `#767877` | disabled fg GTK | Graphite α0.62, 3.53:1 |
| `#5B707B` | terminal dim | Dusty L0.42, 4.67:1 |
| `#4E6069` | greeter disabled (terang) | 3.58:1 |
| `#8A9AA2` | greeter disabled (gelap) | 3.37:1 |
| `#2A3A45` | Papirus aksen gelap | turunan Steel |
| `#4E7A3A` | Papirus hijau earthy | turunan hijau terminal |

---

## 4. Warna status semantik (disepakati dipertahankan)

Palet ORACLE **tidak punya** warna status. Menggantinya akan menghapus makna
sinyal keselamatan. Karena itu warna status dipertahankan/diturunkan.

### 4.1 Terminal ANSI (16 slot)

| Slot | Hex | Kontras di Porcelain |
|---|---|---:|
| 0 black | `#30363B` | 11.02:1 |
| 1 red | `#B4503C` | 4.55:1 |
| 2 green | `#317E2A` | 4.56:1 |
| 3 yellow | `#8A682E` | 4.61:1 |
| 4 blue | `#3674A1` | 4.54:1 |
| 5 magenta | `#B83D99` | 4.54:1 |
| 6 cyan | `#2B7682` | 4.71:1 |
| 7 white | `#667D89` | 3.89:1 (UI saja) |
| 8 b.black | `#B9C1C2` | 1.65:1 (dekor) |
| 9 b.red | `#C33D22` | 4.72:1 |
| 10 b.green | `#26801E` | 4.52:1 |
| 11 b.yellow | `#90661E` | 4.61:1 |
| 12 b.blue | `#1F72AE` | 4.64:1 |
| 13 b.magenta | `#C8239F` | 4.51:1 |
| 14 b.cyan | `#1B7987` | 4.58:1 |
| 15 b.white | `#E9E5DA` | 1.13:1 (dekor) |

Metode: slot 0/7/8/15 memakai warna brand langsung. Slot hue memakai hue ANSI
standar dengan saturasi 0.50 dan lightness tertinggi yang masih lolos 4.5:1.

**"Bright" berarti lebih pekat, bukan lebih terang.** Di light theme, bright
yang lebih terang justru mendekati latar dan menghilang. BRIGHT = saturasi
+0.12…0.20, lightness −0.02.

Kebetulan yang menguntungkan: hue slot 4 (blue) = hue Steel Blue
(selisih 0.1°), slot 3 (yellow) ≈ Brass Ink (selisih 2.6°). Biru dan kuning
terminal otomatis selaras identitas.

### 4.2 GTK status (dipertahankan dari Arc)

16 warna: `#FC4138 #FD8D88 #F27835 #F7AE86 #F04A50 #F4797E #EC1B22
#F08437 #FF4D4D #FF6666 #FD716A #F75D37 #73D216 #F13039 #F46067 #F68086`

Konsekuensi: 10 rule GTK berada di 3.38–4.38:1 (bukan 4.5:1). **Ini
pengecualian yang disepakati**, bukan kelalaian. Dibanding Arc asli,
mayoritas justru membaik (`entry.warning` 1.85 → 6.61:1).

---

## 5. Tipografi

| Peran | Font | Paket Debian | Status |
|---|---|---|---|
| UI | Inter | `fonts-inter` 4.1+ds-1 | terverifikasi |
| Terminal | JetBrains Mono | `fonts-jetbrains-mono` 2.304+ds-5 | terverifikasi |
| Display | ~~IBM Plex Sans Condensed~~ | — | **dicoret** |

### 5.1 IBM Plex dicoret

`fonts-ibm-plex` **tidak ada di trixie**. Konsekuensi: display font dicoret
dari rencana, dan tata letak tidak boleh bergantung padanya. **Inter menjadi
satu-satunya font UI.**

### 5.2 Aturan

- Inter untuk seluruh teks antarmuka: panel, menu, dialog, judul jendela.
  Ukuran final: **Inter 11**.
- JetBrains Mono untuk terminal (`JetBrains Mono 11`) dan nilai teknis
  (checksum, ID perangkat).
- Ukuran, ketebalan, dan jarak huruf diuji pada **1280×800** sebelum diterima.

---

## 6. Desktop

| Aspek | Keputusan |
|---|---|
| Lingkungan | XFCE 4.20 |
| Tata letak | Classic layout |
| Panel navigasi | Panel atas (Steel, 32 px) |
| Dock aplikasi | Panel bawah terpisah (Porcelain, 48 px) |
| Kedalaman visual | Flat |
| Wallpaper | Dial watermark + motto |

### 6.1 Definisi Classic layout

Satu panel navigasi di atas dan satu dock aplikasi di bawah, dengan area kerja
bersih di antaranya. **Tidak ada** panel samping, panel mengambang, atau dock
yang menyembunyikan diri saat tidak dipakai.

### 6.2 Dock adalah panel XFCE kedua, bukan aplikasi dock

Alasan: satu komponen, satu mekanisme konfigurasi (`xfconf`), satu jalur
paket. Lapisan tambahan menambah risiko tanpa menambah kemampuan yang
dibutuhkan.

### 6.3 Larangan Plank — keputusan arsitektural

**Plank, Cairo-Dock, Docky, dan plugin dock-like tidak dipakai.** Dock
diwujudkan sebagai Panel XFCE kedua.

Konsekuensi yang diterima secara sadar:

1. Tidak ada efek zoom ikon khas dock mandiri.
2. Tidak ada penyembunyian otomatis tanpa konfigurasi tambahan.
3. Tidak ada indikator "aplikasi berjalan" bergaya dock — sorotan mengikuti
   state GTK biasa.

Ini bukan kekurangan yang belum terpecahkan. Ini harga yang dibayar untuk
satu jalur paket dan satu mekanisme konfigurasi.

### 6.4 Flat visual depth

Tidak ada bayangan berlapis, tidak ada gradien dekoratif, tidak ada
transparansi palsu. Pemisahan kedalaman dilakukan dengan **warna permukaan
dan garis satu piksel**.

Konsekuensi: panel memakai alpha 1.0 (opaque). Tidak ada ketergantungan pada
compositor — tampilan identik dengan atau tanpa compositor.

---

## 7. Wallpaper

| ID | Nama | Resolusi | Isi |
|---|---|---|---|
| B1 | Workspace | 1920×1200 | Dial Dusty 18% kanan-bawah, motto kanan-atas |
| B2 | Workspace | 1280×800 | komposisi sama |
| B3 | Minimal | 1920×1200 | Dial di lower band, tanpa motto |
| B4 | Minimal | 1280×800 | komposisi sama |

Rasio 16:10 dipilih karena 1280×800 adalah target uji QEMU; 1920×1200 rasio
sama sehingga komposisi tidak berubah antar resolusi.

**Dua wallpaper, bukan satu.** Workspace dipakai sehari-hari; Minimal untuk
konteks yang butuh lebih tenang. Minimal **bukan** versi "Workspace tanpa
motto" — Dial-nya dipindah ke lower band sebagai komposisi utama.

### 7.1 Safe zone

Konstanta piksel (bukan fraksi), karena tinggi panel sama di kedua resolusi:

```
Z_TOP_PX      = 72   (panel atas 32 px + margin)
Z_BOTTOM_PX   = 104  (panel bawah 48 px + gap 16 + margin)
Z_ICON_PX     = 168  (kolom ikon desktop)
BOTTOM_GAP_PX = 16
```

Melebihi angka ini berarti menutupi elemen wallpaper yang sudah disetujui.

### 7.2 Dial 18% — keputusan sadar

Ring Dusty pada 18% menghasilkan `#D1D3CC` (1.21:1 terhadap Ivory) — praktis
tak terlihat. **Itu memang tujuannya**: watermark, bukan konten.

Konsekuensi yang diterima: wallpaper Workspace tidak akan terbaca di
proyeksi/ruangan terang. Varian presentasi **tidak** dibuat pada v0.1.

---

## 8. Panel

### 8.1 Panel atas — status bar

| Properti | Nilai |
|---|---|
| Posisi | `p=6` (NW, kiri atas) |
| Tinggi | 32 px |
| Panjang | 100 % |
| Icon size | 18 px |
| Latar | Steel `#344653`, alpha 1.0 |
| Teks | Porcelain `#F5F3EC` (8.81:1) |
| Aksen aktif | Muted Brass `#B8A98D` (4.24:1) |
| Autohide | never |

Plugin (kiri ke kanan): `applicationsmenu`, `launcher` Terminal,
`launcher` Files, `separator` (spacer), `tasklist`, `separator` (spacer),
`systray`, `clock`.

### 8.2 Panel bawah — dock

| Properti | Nilai |
|---|---|
| Posisi | `p=10` (SC, bawah tengah) |
| Tinggi | 48 px |
| Panjang | **27.08%** viewport (`length` bertipe persen, bukan px; `length-adjust=true`) |
| Icon size | 32 px |
| Latar | Porcelain `#F5F3EC`, alpha 1.0 |
| Border | Dusty `#667D89` 1 px (3.89:1) |
| Ikon | Steel `#344653` (8.81:1) |
| Aksen aktif | Brass Ink `#8C7B58` (3.72:1) |
| Jarak dari dasar | 16 px |
| Autohide | never |

Plugin (kiri ke kanan): `showdesktop`, `separator` (garis), `launcher`
Terminal, `launcher` Files, `launcher` Web Browser, `launcher` App Finder,
`separator` (garis).

> **R2 — kenapa 27.08%, bukan 520 px (Stage 3G, 2026-11-05).**
> `xfce4-panel` menyimpan panjang panel sebagai **persen**, bukan piksel:
> `panel/panel-window.c` mendeklarasikan `g_param_spec_double("length", 1, 100, 10)`
> dan setter-nya `g_value_get_double(value) / 100`. Render memakai
> `panel_width = CLAMP(natural_plugin_width, area_width × length/100, area_width)`.
>
> Konfigurasi lama menulis `type="uint" value="520"`. Tipe dan rentangnya salah,
> nilai ditolak, panel jatuh ke default **10%** — sehingga lebar mengikuti
> konten (terukur 256 px pada layar 1280 px), bukan 520 px. Itu sebabnya dock
> tampak lebih pendek dari desain.
>
> Nilai sekarang `type="double" value="27.08"` = 520/1920. Pada 1920 px
> menghasilkan 520 px (sesuai desain); pada 1280 px menghasilkan 347 px
> (proporsional). `length-adjust=true` membuat panel melebar otomatis bila
> plugin butuh ruang lebih, sehingga ikon tidak pernah terpotong.

### 8.3 Border bawah wajib, bukan pilihan

Porcelain di atas Warm Ivory = **1.13:1**. Tanpa border, dock menyatu dengan
wallpaper dan batasnya tidak terbaca. Dusty memberi 3.89:1 — jelas terlihat,
tetap tipis 1 px.

### 8.4 Fakta teknis: warna panel lewat xfconf, bukan CSS

Panel memasang CSS inline pada `PRIORITY_APPLICATION` (600), di atas tema
(200). Prioritas menang atas spesifisitas, sehingga **warna latar panel
tidak bisa** diatur dari `gtk.css`.

Warna **wajib** lewat `background-style` + `background-rgba` per panel.
`border-color` juga dipaksa transparan secara inline.

Konsekuensi baik: tidak perlu tema panel terpisah. Satu `gtk.css` untuk semua.

### 8.5 Whisker Menu ditolak

`xfce4-whiskermenu-plugin` 2.9.2-1 tersedia di trixie, tetapi **tidak
dipakai**. Menu aplikasi memakai `applicationsmenu` bawaan `xfce4-panel`.

Alasan: `applicationsmenu` adalah plugin bawaan — tidak menambah paket, tidak
menambah dependency, dan gaya klasiknya cocok dengan Retro Industrial.
Whisker Menu adalah menu bergaya modern dengan pencarian; itu menambah satu
paket dan satu permukaan visual baru tanpa kebutuhan yang terbukti.

Konsekuensi diterima: tidak ada pencarian aplikasi di menu. Pencarian tetap
tersedia lewat `xfce4-appfinder`, yang juga dipakai sebagai launcher di dock.

---

## 9. Terminal

| Properti | Nilai |
|---|---|
| Latar | Soft Porcelain `#F5F3EC` |
| Teks | Graphite `#30363B` (11.02:1) |
| Font | JetBrains Mono 11 |
| Cursor | blok, Steel `#344653`, teks Porcelain (8.81:1) |
| Cursor blink | mati |
| Selection | Steel, teks Porcelain (8.81:1) |
| Bold | tetap Graphite (**tidak** jadi bright) |
| Background vary | mati |
| Scrollbar | disembunyikan |

Kenapa latar Porcelain dan bukan Ivory: terminal adalah permukaan baca
intensif. Porcelain lebih terang, memberi ruang kontras lebih besar untuk 16
warna, dan membedakan jendela terminal dari wallpaper.

Kenapa cursor tidak berkedip: kedipan menarik perhatian terus-menerus.
"Work with clarity." lebih tenang tanpa kedip.

### 9.1 Peta peran semantik

| Peran | Slot | Kontras |
|---|---:|---:|
| perintah / command | 4 | 4.54:1 |
| argumen | 0 | 11.02:1 |
| string | 2 | 4.56:1 |
| angka | 5 | 4.54:1 |
| direktori | 4 | 4.54:1 |
| sukses | 2 | 4.56:1 |
| warning | 3 | 4.61:1 |
| error | 1 | 4.55:1 |
| key / branch | 6 | 4.71:1 |
| komentar / dim | turunan | 4.67:1 (`#5B707B`) |
| aksen prompt | brand | Brass Ink (3.72:1) |

Slot 7 (Dusty) **tidak** dipakai untuk teks — 3.89:1, gagal ambang teks.
Slot 7 tetap Dusty untuk peran "white"/UI, mengikuti konvensi light scheme
Debian (xterm `#e5e5e5`, solarized-light `#eee8d5`).

---

## 10. Tema GTK

| Aspek | Keputusan |
|---|---|
| Basis | **Turunan Arc** (`arc-theme` 20221218-1) |
| Alasan | lebih cepat, dan lingkup perubahan bisa dibatasi pada warna |
| Metode | recolor deterministik berbasis semantic mapping |
| Aset PNG | 124, dirender ulang dari `assets.svg` Arc |
| Lisensi | **GPL-3+** |

Kenapa turunan dan bukan dari nol: menulis tema GTK3 dari nol berarti
mendefinisikan ulang seluruh state widget (checkbox, switch, titlebutton,
menu, treeview, scrollbar) untuk GTK 3.24. Turunan Arc membawa perilaku yang
sudah matang; perubahan dibatasi pada warna.

### 10.1 Kontras

| Konteks | fg / bg | Kontras |
|---|---|---:|
| teks window | Graphite / Ivory | 9.72:1 |
| headerbar | Porcelain / Steel | 8.81:1 |
| selection | Porcelain / Steel | 8.81:1 |
| disabled | `#767877` / Ivory | 3.53:1 |
| scroll slider | Dusty / Ivory | 3.43:1 |

Disabled final `#767877` (Graphite α0.62). Alpha 0.55 gagal 3:1 di Ivory
(2.95:1); di atas 0.65 disabled mulai mirip teks aktif. 0.62 satu-satunya
nilai yang lolos 3:1 di kedua surface dan masih jelas pudar (36% dari normal).

---

## 11. Ikon

| Aspek | Keputusan |
|---|---|
| Basis | **Papirus penuh** (`papirus-icon-theme` 20250501-1) |
| Tema turunan | `ORACLE-Papirus`, `Inherits=Papirus,hicolor` |
| Recolor | terbatas pada aksen; bentuk dipertahankan |
| Lisensi | **GPL-3** |

### 11.1 Kenapa Papirus penuh, bukan Papirus-Light

Diuji terhadap 20 ikon XFCE yang dipakai `.desktop` di image:

| | Papirus-Light | Papirus penuh |
|---|---:|---:|
| Ikon XFCE tersedia | **0 dari 20** | **20 dari 20** |
| `folder`, `user-home`, `edit-copy` | tidak ada | ada |

`Papirus-Light` ber-`Inherits=breeze,hicolor` — **bukan** Papirus. Ikon yang
hilang jatuh ke hicolor, bukan ke Papirus.

### 11.2 Dua jenis ikon

| Ukuran | Jenis | Warna |
|---|---|---|
| 16×16 | symbolic | `fill:currentColor` — ikut warna teks GTK |
| 22px+ | berwarna | hex langsung |

Ikon 16×16 **tidak** di-recolor: warnanya mengikuti konteks (terang di panel
gelap, gelap di permukaan terang). Ini perilaku benar, bukan cacat.

---

## 12. LightDM Greeter

| Properti | Nilai |
|---|---|
| Latar layar | Warm Ivory `#E9E5DA` (warna solid) |
| Panel atas | Steel, teks Porcelain |
| Kotak login | Porcelain, border `#B9C1C2`, radius 4 px |
| Font | Inter 11 |
| Tombol login | Steel, teks Porcelain (8.81:1) |
| Tombol cancel | Porcelain, teks Graphite (11.02:1) |
| Error | Porcelain + garis merah `#B4503C` 3 px di tepi kiri |

### 12.1 Fakta teknis: greeter tidak punya opsi CSS

31 `CONFIG_KEY_*` di source 2.0.9 — **tidak satu pun untuk CSS**. CSS
dikompilasi ke binary pada `PRIORITY_APPLICATION` (600).

Styling hanya lewat `theme-name` + named widget yang ditargetkan dari tema
GTK. Ini mekanisme resmi, didokumentasikan di sample CSS upstream.

### 12.2 Konfigurasi: file mana yang menang

`/etc/lightdm/lightdm-gtk-greeter.conf` (lapisan 1) menang atas
`/usr/share/lightdm/lightdm-gtk-greeter.conf.d/01_debian.conf` (lapisan 3).
`01_debian.conf` **tidak perlu dihapus**.

### 12.3 Widget ID yang terverifikasi ada di binary 2.0.9

**18 ID:**

```
login_window      panel_window    menubar          password_entry
username_entry    login_button    user_image       user_image_border
user_combobox     message_label   greeter_infobar  power_window
power_icon        power_title     power_text       power_ok_button
power_cancel_button               screen_overlay
```

Tidak ada di binary (jangan dipakai sebagai selector):
`login_box`, `cancel_button`, `power_menu`, `power_buttonbox_frame`,
`power_content_frame`.

### 12.4 Autologin

Live image memakai `autologin-user=user`. Greeter **mungkin tidak pernah
tampil** pada boot normal. Styling tetap penting untuk logout manual atau
bila autologin dimatikan.

---

## 13. Pengecualian yang disengaja (jujur, tidak disembunyikan)

| # | Pengecualian | Alasan | Dampak |
|---|---|---|---|
| 1 | 10 rule GTK status di 3.38–4.38:1 | palet tanpa warna status | teks status sedikit di bawah AA |
| 2 | `thumbnail-frame.png` dihapus, diganti border solid | aset tidak dapat diproduksi (tidak ada id di assets.svg) | sudut thumbnail dokumen jadi garis |
| 3 | Slot ANSI 7/8/15 di bawah 4.5:1 | peran latar/dekor, konvensi light scheme Debian | tidak untuk teks isi |
| 4 | Ikon Papirus symbolic tidak di-recolor | `currentColor` mengikuti tema GTK | warna ikut konteks (benar) |
| 5 | Border `#B9C1C2` 1.65:1 | dekoratif, bukan indikator fungsional | tidak tunduk WCAG 1.4.11 |
| 6 | Panel bawah vs wallpaper 1.13:1 | Light-first, tenang | **wajib** border Dusty 3.89:1 |
| 7 | Greeter mungkin tidak tampil saat boot | autologin aktif di live image | relevan hanya saat logout |
| 8 | Wallpaper Dial 18% = 1.21:1 | watermark, bukan konten | tak terbaca di proyeksi |
| 9 | Tidak ada varian gelap | Light-first | tidak untuk ruangan gelap |

---

## 14. Lisensi & atribusi

| Aset | Lisensi | Kewajiban |
|---|---|---|
| A1–A5, wallpaper, panel, terminal, greeter | karya ORACLE | — |
| GTK theme | **GPL-3+** (turunan Arc) | sertakan source + COPYING + NOTICE |
| Papirus | **GPL-3** (turunan Papirus) | sertakan source + NOTICE |

Lokasi di repo: `image/config/includes.chroot/usr/share/doc/oracle-theme/`
dan `.../usr/share/doc/oracle-icons/`.

---

## 15. Prinsip penilaian

Sebuah keputusan visual diterima bila memenuhi **semua** ini:

1. Konsisten dengan Retro Industrial dan Light-first.
2. Dapat diwujudkan dengan paket yang sudah terbukti tersedia di trixie.
3. Tidak menambah lapisan komponen yang tidak dibutuhkan.
4. Tidak menurunkan keterbacaan atau aksesibilitas.
5. Dapat diverifikasi dari tangkapan layar QEMU, bukan dari deskripsi.

**Klaim visual yang tidak disertai bukti runtime adalah klaim yang belum
selesai.**

---

## 16. Yang masih terbuka

Dicatat jujur. Tidak boleh diisi diam-diam saat implementasi.

| # | Hal | Alasan masih terbuka |
|---|---|---|
| 1 | Tata letak tombol jendela XFWM4 | di luar scope Stage 2; belum ada keputusan |
| 2 | Tema `xfwm4` | belum diproduksi |
| 3 | Apakah ring 18% dinaikkan untuk presentasi | ditunda; v0.1 tetap 18% |
| 4 | Ukuran/tipografi final yang lolos uji 1280×800 | menunggu build nyata |

selain itu, semua keputusan desain sudah final.