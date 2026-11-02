# ORACLE-OS — Papirus Icon Theme: Audit

Stage 2F-A. Target: **papirus-icon-theme 20250501-1** (Debian 13 Trixie).

---

## 1. Versi dan metadata paket

Dari `ar x papirus.deb` → `control`:

```
Package: papirus-icon-theme
Version: 20250501-1
Depends: hicolor-icon-theme
Recommends: librsvg2-common
Section: x11
Homepage: https://github.com/PapirusDevelopmentTeam/papirus-icon-theme
```

**Catatan penting:** `librsvg2-common` hanya **Recommends**. Karena build
memakai `--apt-recommends false`, paket itu **tidak akan terpasang otomatis**.
Tanpa `librsvg2-common`, SVG tidak bisa dirender oleh GTK dan ikon akan
tampil kosong. Ini harus ditambahkan eksplisit ke package list.

---

## 2. Struktur tema

Paket berisi **tiga** tema:

| Tema | File | Symlink | Total entri | Inherits |
|---|---:|---:|---:|---|
| Papirus | 43.444 | — | — | `breeze,hicolor` |
| Papirus-Light | 3.470 | 3.801 | 7.280 | `breeze,hicolor` |
| Papirus-Dark | 3.955 | — | — | `breeze-dark,hicolor` |

Ukuran yang tersedia (ketiganya): `8x8 16x16 18x18 22x22 24x24 32x32 42x42
48x48 64x64 84x84 96x96 128x128` + varian `@2x`.

Kategori per ukuran: `actions apps categories devices emblems emotes
mimetypes panel places status symbolic`.

---

## 3. TEMUAN KRITIS — Papirus-Light tidak layak dipakai

Dugaan awal: karena ORACLE light-first, pakai `Papirus-Light`. **Salah.**

Diuji terhadap 20 nama ikon yang benar-benar dipakai `.desktop` paket XFCE
di image:

| Diperiksa | Papirus-Light | Papirus (penuh) |
|---|---:|---:|
| Ikon XFCE tersedia | **0 dari 20** | **20 dari 20** |
| `folder` | tidak ada | ada |
| `user-home` | tidak ada | ada |
| `edit-copy`, `view-refresh` | tidak ada | ada |
| `system-shutdown` | tidak ada | ada |

Daftar 20 ikon yang **hilang seluruhnya** di Papirus-Light:

```
application-x-executable   org.xfce.filemanager      org.xfce.mailreader
org.xfce.panel             org.xfce.session           org.xfce.settings.accessibility
org.xfce.settings.appearance  org.xfce.settings.color  org.xfce.settings.default-applications
org.xfce.settings.display  org.xfce.settings.editor   org.xfce.settings.keyboard
org.xfce.settings.manager  org.xfce.settings.mouse    org.xfce.terminal
org.xfce.terminal-settings org.xfce.terminalemulator  org.xfce.webbrowser
org.xfce.xfdesktop         xfsm-logout
```

**Sebabnya:** `Papirus-Light/index.theme` berisi `Inherits=breeze,hicolor` —
**bukan** `Papirus`. Jadi ikon yang tidak ada di Papirus-Light jatuh ke
`hicolor` (ikon generik), bukan ke Papirus. Papirus-Light memang hanya berisi
ikon panel/status yang perlu versi terang, bukan tema lengkap.

**Keputusan:** pakai **Papirus penuh** + `Inherits=Papirus,hicolor`.

---

## 4. Dua jenis ikon: symbolic vs berwarna

Ini menentukan cara recolor. Diverifikasi dari isi file:

### 4.1 16×16 — symbolic

```xml
<svg width="16" height="16">
 <defs>
  <style id="current-color-scheme" type="text/css">
   .ColorScheme-Text { color:#444444; }
   .ColorScheme-Highlight { color:#4285f4; }
   ...
  </style>
 </defs>
 <path style="fill:currentColor" class="ColorScheme-Text" d="..."/>
</svg>
```

Warna datang dari `currentColor` → mengikuti warna teks GTK. **Recolor hex
tidak berpengaruh.** Ini benar secara desain: symbolic harus menyesuaikan
konteks (terang di panel gelap, gelap di permukaan terang).

### 4.2 22px ke atas — berwarna

```xml
<rect style="fill:#5294e2" .../>
<path style="fill:#4877b1" .../>
```

Hex langsung. Inilah yang di-recolor.

### 4.3 Konsekuensi untuk preview

Preview **wajib** merender ukuran 48×48, bukan 16×16. Render 16×16 akan
tampil abu-abu (`#444444`) dan menyesatkan — terlihat seperti recolor gagal
padahal ikon itu memang symbolic.

Kesalahan ini sempat terjadi dan diperbaiki: `pick()` sekarang memilih
ukuran berwarna terbesar.

---

## 5. Warna aksen Papirus

Dari sampel nyata (`48x48/places/folder.svg`, `apps/*.svg`):

| Warna | Muncul di | Peran |
|---|---|---|
| `#5294E2` | folder, user-home, filemanager | aksen utama |
| `#4877B1` | folder (bayangan) | aksen gelap |
| `#1D344F` | user-home | aksen sangat gelap |
| `#3EA0F4` | webbrowser | aksen terang |
| `#0090EF` | appfinder | aksen terang |
| `#4354CB` | webbrowser | aksen ungu-biru |
| `#89E058` | filemanager | hijau |
| `#FFCD54` | filemanager | kuning |

`#5294E2` **sama persis** dengan biru aksen Arc yang dipakai tema GTK.
Pemetaan ke Steel Blue karena itu konsisten lintas aset.

---

## 6. Kompatibilitas XFCE 4.20

| Aspek | Status |
|---|---|
| Format | SVG + PNG, dibaca GTK3 |
| Ukuran panel | 16/22/24/32/48 tersedia |
| `FollowsColorScheme=true` | didukung GTK3 |
| Ikon panel (`panel/` subdir) | 2.344 ikon di 16×16 |
| Ikon status | tersedia (`battery-*`, `network-*`, `audio-*`) |
| Ikon XFCE | lengkap di Papirus penuh |

Tidak ada ketergantungan pada GTK4 atau mekanisme yang tidak ada di XFCE 4.20.

---

## 7. Lisensi

GPL-3. Detail lengkap di `docs/NOTICE.md`.

---

## 8. Keterbatasan

1. **Tidak bisa memverifikasi render di XFCE sungguhan** — integrasi dilarang.
   Preview dirender dengan `rsvg-convert`, bukan GTK.
2. **`librsvg2-common` wajib ditambahkan manual** karena `--apt-recommends
   false`. Tanpa itu ikon SVG tidak tampil.
3. **Subset, bukan tema penuh.** Hanya 41 nama ikon wajib × 6 ukuran.
   Ikon lain jatuh ke Papirus lewat `Inherits`.
4. **Cache ikon harus dibangun** setelah paket terpasang
   (`gtk-update-icon-cache`), bukan sebelum.
5. **Ikon symbolic tidak di-recolor** — warnanya mengikuti tema GTK. Bila
   tema GTK berganti, warna symbolic ikut berubah. Ini perilaku yang benar,
   bukan cacat.
6. **Tidak semua aplikasi punya ikon di Papirus.** Aplikasi di luar subset
   akan memakai ikon generik dari `hicolor`.