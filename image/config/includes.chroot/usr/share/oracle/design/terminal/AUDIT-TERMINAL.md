# ORACLE-OS — Terminal: Audit ANSI 16-Color

Stage 2E. Target: **xfce4-terminal 1.1.4-1** (Debian 13 Trixie), VTE 0.61.91+.

---

## 0. Status palette lama

**Tidak ada palette ANSI lama yang bisa diaudit.** Pencarian menyeluruh:

| Lokasi diperiksa | Hasil |
|---|---|
| `~/Projects/oracle-brand-assets/` (grep ansi/terminal/palette) | 0 file palette |
| Riwayat sesi (`session_search`) | hanya *rencana* "lengkapi ANSI 16-color", tanpa nilai |
| Git history repo desain | 1 commit, tanpa direktori terminal |

Karena itu palette **dihitung ulang dari nol** dengan derivasi eksplisit di
bawah. Tidak ada nilai lama yang diwarisi tanpa bukti.

---

## 1. Bukti teknis dari paket Debian

### 1.1 Versi

```
Package: xfce4-terminal
Version: 1.1.4-1
libvte-2.91-0 (>= 0.61.91)   libgtk-3-0t64 (>= 3.21.6)
```

### 1.2 Key warna yang benar-benar dibaca

Dari `strings usr/bin/xfce4-terminal`:

```
ColorForeground        ColorBackground        ColorBackgroundVary
ColorCursor            ColorCursorForeground  ColorCursorUseDefault
ColorSelection         ColorSelectionBackground  ColorSelectionUseDefault
ColorBold              ColorBoldUseDefault    ColorBoldIsBright
ColorPalette           ColorUseTheme          TabActivityColor
```

Semua key di atas dipakai di file `.theme` ORACLE. Tidak ada key karangan.

### 1.3 Format colorscheme

Dari 8 scheme bawaan Debian (`usr/share/xfce4/terminal/colorschemes/*.theme`):

```ini
[Scheme]
Name=ORACLE
Name[id]=ORACLE
ColorForeground=#30363B
ColorBackground=#F5F3EC
ColorPalette=#30363B;#B4503C;...   ← 16 hex, dipisah ';'
```

`Name[id]` **valid** — dipakai di kedelapan scheme bawaan (locale `id`).
`ColorPalette` wajib tepat 16 entri.

### 1.4 Konvensi light scheme di Debian

Diperiksa `solarized-light.theme` dan `xterm.theme`:

| Scheme | ColorForeground | ColorBackground | slot 7 | slot 15 |
|---|---|---|---|---|
| xterm | `#000000` | `#ffffff` | `#e5e5e5` | `#ffffff` |
| solarized-light | `#073642` | `#fdf6e3` | `#eee8d5` | `#fdf6e3` |

**Temuan:** pada light scheme, slot 7 dan 15 mendekati warna latar, bukan
putih murni. Ini disengaja: di latar terang, "putih" yang benar-benar putih
tidak terlihat. ORACLE mengikuti konvensi ini.

---

## 2. Derivasi palette

### 2.1 Latar dan teks

| Peran | Warna | Kontras |
|---|---|---:|
| Latar | Soft Porcelain `#F5F3EC` | — |
| Teks utama | Graphite `#30363B` | **11.02:1** |

Latar Porcelain (bukan Ivory) dipilih karena terminal adalah permukaan
baca intensif: Porcelain lebih terang, memberi ruang kontras lebih besar
untuk 16 warna, dan membedakan jendela terminal dari wallpaper Ivory.

### 2.2 Slot yang memakai warna brand langsung

| Slot | Nama ANSI | Warna | Alasan |
|---:|---|---|---|
| 0 | black | Graphite `#30363B` | teks utama brand |
| 7 | white | Dusty Blue `#667D89` | "putih" light theme = abu kebiruan |
| 8 | bright black | `#B9C1C2` | border GTK theme, peran "dim" |
| 15 | bright white | Warm Ivory `#E9E5DA` | paling terang, dekat latar |

### 2.3 Slot hue — metode

Palet ORACLE **tidak punya** hue merah, hijau, kuning, magenta, atau cyan.
ANSI mewajibkan keenamnya. Metode yang dipakai, bukan mengarang:

1. **Hue** diambil dari standar ANSI (xterm): red 10°, green 115°, yellow 38°,
   blue 205°, magenta 315°, cyan 188°.
2. **Saturasi dikunci 0.50** — cukup untuk membedakan hue, tidak sampai
   menyala. Menjaga karakter Retro Industrial yang tenang.
3. **Lightness** = nilai **tertinggi** yang masih lolos kontras ≥ 4.5:1
   terhadap Porcelain. Ini memaksimalkan keterbacaan sekaligus menjaga warna
   tetap seringan mungkin.

Hasil:

| Slot | Hue | Sat | L | Hex | Kontras |
|---:|---:|---:|---:|---|---:|
| 1 red | 10° | 0.50 | 0.47 | `#B4503C` | 4.55:1 |
| 2 green | 115° | 0.50 | 0.33 | `#317E2A` | 4.56:1 |
| 3 yellow | 38° | 0.50 | 0.36 | `#8A682E` | 4.61:1 |
| 4 blue | 205° | 0.50 | 0.42 | `#3674A1` | 4.54:1 |
| 5 magenta | 315° | 0.50 | 0.48 | `#B83D99` | 4.54:1 |
| 6 cyan | 188° | 0.50 | 0.34 | `#2B7682` | 4.71:1 |

### 2.4 Keselarasan hue dengan brand

| Slot | Hue ORACLE | Hue brand | Selisih |
|---|---:|---:|---:|
| 4 blue | 205.2° | Steel Blue 205.2° | **0.1°** |
| 3 yellow | 37.8° | Brass Ink 40.4° | **2.6°** |

Kebetulan yang menguntungkan: hue ANSI blue hampir identik dengan Steel Blue,
dan hue ANSI yellow dekat dengan Brass. Artinya slot biru dan kuning terminal
**otomatis selaras** dengan identitas tanpa perlu dipaksa.

### 2.5 "Bright" — definisi ulang untuk light theme

Pada dark theme, bright = lebih terang. Pada **light theme itu salah**: bright
yang lebih terang justru mendekati latar dan menghilang.

**Definisi ORACLE: bright = lebih pekat.** Saturasi +0.12…+0.20, lightness
−0.02. Hasilnya warna lebih tegas, kontras tetap ≥ 4.5:1.

| Slot | Normal | Bright | Δ saturasi | Δ lightness | Kontras bright |
|---|---|---|---:|---:|---:|
| 9 red | `#B4503C` | `#C33D22` | +0.20 | −0.022 | 4.72:1 |
| 10 green | `#317E2A` | `#26801E` | +0.12 | −0.020 | 4.52:1 |
| 11 yellow | `#8A682E` | `#90661E` | +0.16 | −0.020 | 4.61:1 |
| 12 blue | `#3674A1` | `#1F72AE` | +0.20 | −0.020 | 4.64:1 |
| 13 magenta | `#B83D99` | `#C8239F` | +0.20 | −0.020 | 4.51:1 |
| 14 cyan | `#2B7682` | `#1B7987` | +0.16 | −0.022 | 4.58:1 |

---

## 3. Audit kontras

Ambang: **4.5:1** teks normal (WCAG AA), **3:1** indikator UI.

### 3.1 Foreground / background

| Pasangan | Kontras | Status |
|---|---:|---|
| Graphite / Porcelain | **11.02:1** | PASS |
| Porcelain / Ivory (tepi jendela) | 1.13:1 | butuh border — lihat §5 |

### 3.2 Normal vs bright

Semua 6 pasang lolos ≥ 4.5:1, dengan jarak RGB 24–60 (cukup terbedakan).

### 3.3 Cursor

| Pasangan | Kontras | Status |
|---|---:|---|
| Blok Steel `#344653` / latar Porcelain | **8.81:1** | PASS (≥3) |
| Teks Porcelain / blok Steel | **8.81:1** | PASS (≥4.5) |

Cursor memakai Steel, bukan Graphite: blok Graphite akan menyatu dengan teks
utama. Steel memberi blok yang jelas berbeda dari teks.

### 3.4 Selection

| Pasangan | Kontras | Status |
|---|---:|---|
| Teks Porcelain / bg Steel | **8.81:1** | PASS |

Selection memakai Steel penuh (bukan alpha), konsisten dengan selection GTK
theme yang sudah disetujui.

### 3.5 Peran semantik

| Peran | Slot | Warna | Kontras | Status |
|---|---:|---|---:|---|
| perintah / command | 4 | `#3674A1` | 4.54:1 | PASS |
| argumen | 0 | `#30363B` | 11.02:1 | PASS |
| string | 2 | `#317E2A` | 4.56:1 | PASS |
| angka | 5 | `#B83D99` | 4.54:1 | PASS |
| direktori | 4 | `#3674A1` | 4.54:1 | PASS |
| sukses | 2 | `#317E2A` | 4.56:1 | PASS |
| warning | 3 | `#8A682E` | 4.61:1 | PASS |
| error | 1 | `#B4503C` | 4.55:1 | PASS |
| key / branch | 6 | `#2B7682` | 4.71:1 | PASS |
| komentar / dim | — | `#5B707B` | **4.67:1** | PASS |

### 3.6 Temuan: slot 7 tidak boleh dipakai untuk teks

Dusty Blue `#667D89` di Porcelain hanya **3.89:1** — gagal ambang teks 4.5.

Keputusan:

- **Slot 7 tetap Dusty** — perannya "white"/UI, mengikuti konvensi light
  scheme Debian (xterm `#e5e5e5`, solarized `#eee8d5`). Slot ini bukan untuk
  teks isi.
- **Teks dim memakai turunan Dusty** `#5B707B`: hue 200.6° dan saturasi 0.146
  **identik** dengan Dusty, hanya lightness 0.469 → 0.42. Hasil 4.67:1.

Ini satu-satunya warna di luar 16 slot, dan hanya untuk peran komentar.
Tidak masuk `ColorPalette` karena bukan slot ANSI.

---

## 4. Bold

`ColorBold=#30363B` dengan `ColorBoldUseDefault=FALSE` dan
`ColorBoldIsBright=FALSE`.

Alasan: bila bold dipetakan ke bright, teks tebal akan berubah warna — di
light theme perubahan itu justru menurunkan keterbacaan. Bold sebaiknya
hanya menebalkan, bukan mengubah hue.

---

## 5. Tepi jendela

Porcelain `#F5F3EC` di atas wallpaper Ivory `#E9E5DA` = **1.13:1**. Jendela
terminal akan menyatu dengan wallpaper tanpa batas.

Solusi: border jendela datang dari **GTK theme ORACLE** yang sudah disetujui
(`#B9C1C2`, 1.65:1 terhadap Porcelain) — bukan dari palette terminal. Ini
konsisten dengan panel: warna permukaan diatur di lapisan yang tepat.

---

## 6. Keterbatasan

1. **Tidak bisa memverifikasi render VTE sungguhan.** Batasan melarang
   integrasi ke terminal host. Preview adalah mockup berlabel.
2. **`ColorPalette` tidak bisa diuji dengan `xfce4-terminal --color-table`**
   tanpa menjalankan terminal. Format diverifikasi lewat parser + perbandingan
   dengan 8 scheme bawaan Debian.
3. **Font JetBrains Mono tersedia di host** (4 varian Nerd Font), tetapi
   ketersediaan di image target bergantung paket `fonts-jetbrains-mono` —
   di luar cakupan tahap ini.
4. **Inter tidak terpasang di host.** Untuk preview dipakai Inter dari cache
   `.deb` Debian; di image target perlu paket `fonts-inter`.
5. **Tidak ada hue brand untuk merah/hijau/magenta/cyan.** Warna tersebut
   diturunkan dari hue ANSI, bukan dari identitas. Ini keterbatasan palet
   ORACLE yang disengaja (palet tidak punya warna status).
6. **`ColorBackgroundVary=FALSE`** — variasi latar dimatikan agar flat.
   Tidak diuji dengan nilai TRUE.

---

## 7. Ringkasan keputusan

| Pertanyaan | Jawaban |
|---|---|
| Palette lama dipakai? | Tidak — tidak ada, dihitung ulang |
| Warna baru ditambah? | Ya, 12 hue turunan + 1 turunan Dusty untuk dim — terdokumentasi |
| Semua slot teks ≥ 4.5:1? | Ya, terendah 4.51:1 |
| Bright lebih terang? | Tidak — lebih pekat (light theme) |
| Slot 7 untuk teks? | Tidak — 3.89:1, hanya peran UI |
| Bold jadi bright? | Tidak |
| Cursor & selection? | Steel, 8.81:1 |