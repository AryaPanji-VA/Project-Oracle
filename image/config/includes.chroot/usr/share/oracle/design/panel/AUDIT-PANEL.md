# ORACLE-OS — XFCE Panel 4.20: Audit Teknis

Stage 2D. Semua klaim di bawah diturunkan dari **paket Debian 13 Trixie
`xfce4-panel` 4.20.4-1** dan source upstream 4.20.x. Tidak ada properti
yang dikarang.

Sumber bukti:

| Bukti | Cara diperoleh |
|---|---|
| Versi paket | `ar x xfce4-panel.deb` → `control` → `Version: 4.20.4-1` |
| Properti xfconf | `strings usr/bin/xfce4-panel` |
| Default layout | `etc/xdg/xfce4/panel/default.xml` (dari `.deb`) |
| Class CSS per panel | `panel-window.c` `panel_window_constructed()` |
| Prioritas provider CSS | `panel-base-window.c` `GTK_STYLE_PROVIDER_PRIORITY_APPLICATION` |
| Nilai enum | `panel-base-window.h`, `panel-window.c`, `separator.c` |

---

## 1. Versi dan dependensi

```
Package: xfce4-panel
Version: 4.20.4-1
libgtk-3-0t64 (>= 3.22.29)   libxfce4panel-2.0-4 (>= 4.20.3)
libxfce4windowing-0-0 (>= 4.20.1)   libwnck-3-0 (>= 43.0)
```

GTK3 (bukan GTK4). Tema GTK3 ORACLE yang sudah disetujui berlaku untuk panel.

---

## 2. Properti xfconf yang tersedia (terverifikasi di binary)

Semua nama di bawah muncul sebagai string literal di `usr/bin/xfce4-panel`:

```
/panels/panel-%d                       (root per panel)
  position            (string)  "p=%d;x=%d;y=%d"
  length              (uint)    persen atau piksel
  length-adjust       (bool)    false = persen, true = piksel
  size                (uint)    tinggi panel dalam piksel
  icon-size           (uint)    0 = otomatis
  nrows               (uint)    1..6
  mode                (uint)    orientasi
  autohide-behavior   (uint)    0 never, 1 intelligently, 2 always
  enter-opacity       (uint)
  leave-opacity       (uint)
  position-locked     (bool)
  disable-struts      (bool)
  span-monitors       (bool)
  output-name         (string)
  background-style    (uint)    lihat §3
  background-rgba     (rgba)    hanya bila style = COLOR
  background-image    (string)  hanya bila style = IMAGE
  dark-mode           (bool)
```

Batasan nilai terverifikasi dari header upstream:

| Konstanta | Nilai |
|---|---|
| `MIN_SIZE` / `MAX_SIZE` / `DEFAULT_SIZE` | 16 / 128 / 48 |
| `MIN_ICON_SIZE` / `MAX_ICON_SIZE` / `DEFAULT_ICON_SIZE` | 0 / 256 / 0 |
| `MIN_NROWS` / `MAX_NROWS` / `DEFAULT_NROWS` | 1 / 6 / 1 |
| `DEFAULT_DARK_MODE` | FALSE |

### 2.1 Nilai enum posisi (`p=`)

Dari `enum _SnapPosition` (`panel-window.c`):

| Nilai | Arti | Catatan |
|---:|---|---|
| 0 | NONE | melayang |
| 1 | E | kanan |
| 2 | NE | kanan atas |
| 3 | EC | kanan tengah |
| 4 | SE | kanan bawah |
| 5 | W | kiri |
| **6** | **NW** | **kiri atas — dipakai default.xml untuk panel atas** |
| 7 | WC | kiri tengah |
| 8 | SW | kiri bawah |
| 9 | NC | atas tengah |
| **10** | **SC** | **bawah tengah — dipakai default.xml untuk panel bawah** |
| 11 | N | atas |
| 12 | S | bawah |

Terverifikasi: `p=6` pada `default.xml` panel-1 (top) dan `p=10` pada
panel-2 (bottom) konsisten dengan enum ini.

---

## 3. Latar panel: tiga mode, dan siapa yang menang

Dari `enum _PanelBgStyle` (`panel-base-window.h`):

```
PANEL_BG_STYLE_NONE    = 0   "None (use system style)"
PANEL_BG_STYLE_COLOR   = 1   "Solid color"
PANEL_BG_STYLE_IMAGE   = 2   "Transparent"  ← lihat catatan di bawah
```

Label combo terverifikasi di binary: `None (use system style)`, `Solid color`,
`Transparent`. `IMAGE` memakai `background-image` (radio/gradient), bukan
alpha; "Transparent" dicapai dengan `rgba()` alpha < 1 pada mode COLOR.

### 3.1 TEMUAN PENTING — CSS tema tidak bisa menimpa warna panel

Panel menyuntik CSS sendiri saat runtime (`panel-base-window.c`):

```c
css_string = g_strdup_printf (".xfce4-panel.background { background: %s; "
                              "border-color: transparent; } %s",
                              str, PANEL_BASE_CSS);
```

dan provider dipasang dengan:

```c
gtk_style_context_add_provider_for_screen (screen, provider,
                                           GTK_STYLE_PROVIDER_PRIORITY_APPLICATION);
```

`PRIORITY_APPLICATION` = **600**; tema (termasuk `gtk.css` ORACLE) dipasang di
`PRIORITY_THEME` = **200**. Prioritas menang atas spesifisitas, sehingga:

> **Warna latar panel WAJIB ditetapkan lewat xfconf
> (`background-style` + `background-rgba`), bukan lewat `gtk.css`.**

`border-color: transparent` juga dipaksa inline, jadi border panel juga tidak
bisa datang dari tema; ia datang dari `border-width` xfconf (style property
`borders`).

Konsekuensi desain: ORACLE **tidak** memerlukan tema GTK khusus panel. Cukup
`gtk.css` yang sudah disetujui + xfconf. Ini juga berarti warna panel tidak
bisa "bocor" ke aplikasi lain.

### 3.2 Class CSS yang benar-benar ada

Dari source (`panel_window_constructed`, `panel_window_update_autohide_window`):

| Class | Dipasang pada | Kapan |
|---|---|---|
| `XfcePanelWindow` | GtkWindow panel | selalu (nama widget) |
| `xfce4-panel` | PanelBaseWindow | selalu |
| `background` | PanelBaseWindow | selalu |
| `panel-<id>` | PanelBaseWindow | selalu, `id` = nomor panel |
| `panel-<id>-hidden` | window autohide | hanya bila ada autohide |

**Koreksi terhadap asumsi lama sesi:** class `panel-<id>` **ada** dan
terverifikasi di `panel_window_constructed()`:

```c
style_class = g_strdup_printf ("%s-%d", "panel", window->id);
gtk_style_context_add_class (context, style_class);
```

Selector `.panel-1` dan `.panel-2` **valid** untuk menata isi panel
(ikon, tombol, spacing) — tetapi **bukan** untuk latar panel itu sendiri,
karena latar dipaksa inline oleh aplikasi (lihat §3.1).

---

## 4. Plugin yang tersedia di paket Debian

`usr/lib/x86_64-linux-gnu/xfce4/panel/plugins/` berisi 11 plugin bawaan:

```
libactions.so  libapplicationsmenu.so  libclock.so  libdirectorymenu.so
liblauncher.so  libpager.so  libseparator.so  libshowdesktop.so
libsystray.so  libtasklist.so  libwindowmenu.so
```

**Tidak termasuk** `whiskermenu`, `pulseaudio`, `docklike`, `weather`.
Paket terpisah bila dibutuhkan. Untuk ORACLE, plugin bawaan sudah cukup:
tidak ada kebutuhan dock-like — panel bawah memakai `launcher` biasa.

### 4.1 Separator — 4 style terverifikasi

`enum _SeparatorPluginStyle` (`separator.c`):

| Nilai | Nama | Visual |
|---:|---|---|
| 0 | TRANSPARENT | kosong (spacer) |
| 1 | SEPARATOR | garis tunggal |
| 2 | HANDLE | pegangan titik-titik |
| 3 | DOTS | titik-titik |
| 4 | WRAP | tidak dipakai sejak 4.10 (pakai `nrows`) |

Properti: `style` (uint), `expand` (bool), `size` (uint).

Untuk ORACLE: spacer pakai style 0 `expand=true`, pemisah visual pakai
style 1 (garis) dengan `size` kecil. Style 2/3 ditolak — tekstur titik
bertabrakan dengan garis tipis Retro Industrial.

---

## 5. Dukungan transparansi

| Kondisi | Perilaku |
|---|---|
| Compositor aktif | `background-rgba` alpha < 1 benar-benar tembus pandang |
| Tanpa compositor | alpha diabaikan; panel tampak solid |

Bukti: `panel_base_window_is_composited()` ada di binary. XFCE di target
ORACLE **tidak menjalankan compositor** (keputusan desain: Flat, tanpa
compositor). Karena itu:

> Desain ORACLE memakai panel **opaque** (alpha 1.0). Transparansi tidak
> diandalkan, sehingga tampilan identik dengan atau tanpa compositor.

Ini bukan keterbatasan tersembunyi — ini keputusan yang menghindari
ketergantungan pada compositor yang tidak akan ada.

---

## 6. `dark-mode` dan risiko tema

`dark-mode` (bool, default FALSE) memanggil
`gtk-application-prefer-dark-theme`. Bila TRUE, GTK memilih varian gelap
tema — untuk ORACLE (light-first, tanpa tema gelap) hasilnya tidak
terdefinisi dan bergantung pada tema fallback.

**Keputusan:** `dark-mode = false` eksplisit pada kedua panel.

---

## 7. Keterbatasan yang diakui

1. **Tidak bisa memverifikasi hasil render panel tanpa menjalankan XFCE.**
   Batasan kerja melarang integrasi ke XFCE. Preview dibuat sebagai mockup
   statis berlabel, dibangun dari warna/ukuran yang sama dengan konfigurasi.
2. **`background-image` (style IMAGE) tidak diuji.** Tidak dipakai di desain
   ORACLE, jadi tidak relevan.
3. **Tinggi panel dalam piksel, bukan DPI-independent.** `size` adalah uint
   piksel; pada layar HiDPI panel tidak otomatis membesar. XFCE 4.20 punya
   pengaturan skala terpisah di luar cakupan panel.
4. **Jumlah ikon tasklist memengaruhi lebar.** `length` diatur piksel tetap
   untuk panel bawah (dock); bila jumlah launcher bertambah, isi bisa
   terpotong — perlu `length-adjust=true` dan penambahan manual.
5. **Brass tidak boleh jadi indikator fungsional di Porcelain** (2.08:1).
   Terukur, bukan perkiraan — lihat §8.
6. **Panel tidak punya "active indicator" bawaan untuk launcher.** Sorotan
   tombol mengikuti state GTK dari `gtk.css` (hover/active). Tidak ada opsi
   xfconf untuk warna indikator khusus per plugin.

---

## 8. Kontras terukur untuk palet panel

Dihitung dengan rumus WCAG 2.x relatif luminans.

### Panel atas — latar Steel `#344653`

| Peran | Warna | Kontras | Status |
|---|---|---:|---|
| Teks/ikon utama | Porcelain `#F5F3EC` | 8.81:1 | lolos 4.5 |
| Teks sekunder | Ivory `#E9E5DA` | 7.77:1 | lolos 4.5 |
| Aksen Brass (indikator) | Muted Brass `#B8A98D` | 4.24:1 | lolos 3.0 |
| Dusty Blue | `#667D89` | 2.26:1 | **ditolak** |
| Brass Ink | `#8C7B58` | 2.37:1 | **ditolak** |

### Panel bawah — latar Porcelain `#F5F3EC`

| Peran | Warna | Kontras | Status |
|---|---|---:|---|
| Teks/ikon utama | Graphite `#30363B` | 11.02:1 | lolos 4.5 |
| Teks/ikon alternatif | Steel `#344653` | 8.81:1 | lolos 4.5 |
| Ikon sekunder | Dusty Blue `#667D89` | 3.89:1 | lolos 3.0 |
| Aksen Brass (indikator) | Brass Ink `#8C7B58` | 3.72:1 | lolos 3.0 |
| Muted Brass | `#B8A98D` | 2.08:1 | **ditolak** |

### Konsekuensi aturan Brass

Muted Brass dan Brass Ink **tidak dapat dipertukarkan**:

- Di latar gelap (Steel): Muted Brass 4.24:1 ✓, Brass Ink 2.37:1 ✗
- Di latar terang (Porcelain): Brass Ink 3.72:1 ✓, Muted Brass 2.08:1 ✗

Aturan ini sudah berlaku di aset brand (A1–A5) dan tetap berlaku di panel.

### Panel bawah vs wallpaper

Porcelain `#F5F3EC` di atas Warm Ivory `#E9E5DA` = **1.13:1**. Panel bawah
hampir menyatu dengan wallpaper. Ini disengaja (Light-first, tenang), tetapi
membuat **border wajib** agar batas panel terbaca. Border memakai Dusty Blue
3.89:1 terhadap Porcelain — jelas terlihat tanpa jadi garis berat.

---

## 9. Safe zone wallpaper vs tinggi panel

Wallpaper yang sudah disetujui menyisakan ruang dengan konstanta piksel:

```
Z_TOP_PX    = 72     (tools/wallpaper_workspace.py)
Z_BOTTOM_PX = 104
BOTTOM_GAP_PX = 16
```

Rencana ukuran panel harus masuk ke zona tersebut:

| Panel | Tinggi | Sisa zona | Kesimpulan |
|---|---:|---:|---|
| Atas | 32 px | 72 px | muat, sisa 40 px |
| Bawah | 48 px | 104 px | muat, sisa 56 px |

Rekomendasi kuat: **jangan melebihi 32 px (atas) dan 48 px (bawah)**.
Melebihi akan menutupi elemen wallpaper (Dial watermark / motto) yang sudah
disetujui. Ini alasan angka tersebut dipilih, bukan preferensi.

---

## 10. Ringkasan keputusan teknis

| Pertanyaan | Jawaban berbasis bukti |
|---|---|
| Latar panel diatur dari mana? | xfconf `background-style=1` + `background-rgba`, **bukan** CSS tema |
| Bisa beda warna atas/bawah? | Ya — properti per panel (`/panels/panel-1`, `panel-2`) |
| Bisa atur isi panel per panel? | Ya — class `.panel-1`, `.panel-2` (terverifikasi di source) |
| Perlu compositor? | Tidak — desain opaque |
| Perlu plugin tambahan? | Tidak — 11 plugin bawaan cukup |
| Perlu tema panel terpisah? | Tidak — `gtk.css` ORACLE berlaku |
| Risiko utama | tinggi panel melebihi safe zone wallpaper |