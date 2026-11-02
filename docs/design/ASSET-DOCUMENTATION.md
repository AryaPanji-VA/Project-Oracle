# ORACLE-OS — Asset Documentation

Inventaris aset desain yang **ada di repository ini** setelah Stage 3A.
Status dan path diverifikasi terhadap filesystem, bukan dikarang.

Terakhir diverifikasi: 2026-11-03 (Stage 3B.1).

---

## Status yang dipakai

| Status | Arti |
|---|---|
| **APPROVED** | disetujui pemilik proyek, dipakai sebagai final |
| **IN REPO** | ada di `includes.chroot/`, belum aktif di runtime |
| **ACTIVE** | dibaca desktop saat boot (lapisan XDG) |
| **REFERENCE** | dokumentasi/spesifikasi, bukan aset runtime |
| **SUPERSEDED** | digantikan versi lain, disimpan sebagai riwayat |

**Penting:** APPROVED ≠ ACTIVE. Sebagian besar aset sudah di repo tetapi
belum diaktifkan. Aktivasi adalah Stage 3C+.

---

## 1. Brand (A1–A5)

Path: `image/config/includes.chroot/usr/share/oracle/branding/`
Status: **IN REPO** · 10 file · SVG

| ID | File | Fungsi | Status |
|---|---|---|---|
| A1 | `dial-master.svg` | Dial master, geometri acuan | APPROVED |
| A2 | `dial-optical-16.svg` | varian 16 px, tick gap lebih lebar | APPROVED |
| A3 | `wordmark.svg` | wordmark ORACLE (outline) | APPROVED |
| A4 | `lockup-horizontal.svg` | mark + wordmark | APPROVED |
| A5a | `dial-light.svg`, `lockup-light.svg` | varian latar terang | APPROVED |
| A5b | `dial-dark.svg`, `lockup-dark.svg` | varian latar gelap | APPROVED |
| A5c | `dial-mono.svg`, `lockup-mono.svg` | monokrom satu warna | APPROVED |

### 1.1 Geometri

Rasio terhadap diameter ring (Ø). Sumber: `ASSET-README.md` (spesifikasi
generator, diverifikasi `audit_assets.py`).

| Parameter | Master | Optical 16 px |
|---|---:|---:|
| stroke/Ø | 0,1250 | 0,1250 |
| slot/Ø | 0,1739 | 0,2800 |
| tick_w/Ø | 0,1087 | 0,1150 |
| tick_h/Ø | 0,3913 | 0,4100 |
| protrude/Ø | 0,0543 | 0,0770 |
| gap/Ø (mark→wordmark) | 0,4565 | — |
| cap/Ø (wordmark) | 0,5109 | — |

Aturan pakai: **master untuk 24 px ke atas, optical-16 hanya untuk ≤16 px.**
Pada 16 px master memberi celah tick kiri/kanan `(2,1)` tidak simetris;
optical memberi `(2,2)`.

### 1.2 Kanvas

Master digambar pada kanvas besar (512 px) lalu diekspor turun. Menggambar
langsung di 16 px menghilangkan stroke.

---

## 2. Wallpaper

Path: `image/config/includes.chroot/usr/share/backgrounds/oracle/`
Status: **IN REPO** · 4 file · PNG

| ID | File | Ukuran | Status |
|---|---|---|---|
| B1 | `workspace-1920x1200.png` | 1920×1200 | APPROVED |
| B2 | `workspace-1280x800.png` | 1280×800 | APPROVED |
| B3 | `minimal-1920x1200.png` | 1920×1200 | APPROVED |
| B4 | `minimal-1280x800.png` | 1280×800 | APPROVED |

Sumber SVG ada di design repository (`wallpaper/svg/`) tetapi **tidak**
disalin ke repo ini — yang dibutuhkan runtime hanya PNG.

### 2.1 Safe zone (wajib dipatuhi)

| Konstanta | Nilai | Isi |
|---|---:|---|
| `Z_TOP_PX` | 72 | panel atas 32 + margin |
| `Z_BOTTOM_PX` | 104 | panel bawah 48 + gap 16 + margin |
| `Z_ICON_PX` | 168 | kolom ikon desktop |
| `BOTTOM_GAP_PX` | 16 | jarak dock ke dasar |

Terverifikasi pada preview 1:1: panel atas mengisi baris 0–31 (**32 px**),
dock 1137–1183, gap **16 px**. Tidak ada tabrakan dengan motto atau Dial.

---

## 3. Tema GTK

Path: `image/config/includes.chroot/usr/share/themes/ORACLE/gtk-3.0/`
Status: **IN REPO** · 127 file (124 PNG + gtk.css + oracle-assets.svg + oracle-greeter.css)

| File | Fungsi |
|---|---|
| `gtk.css` | tema utama, turunan Arc light di-recolor |
| `assets/*.png` | 124 aset: checkbox, radio, switch, titlebutton |
| `assets/oracle-assets.svg` | SVG sumber hasil recolor |
| `oracle-greeter.css` | styling greeter (**belum di-@import**) |

Lisensi: `.../usr/share/doc/oracle-theme/` — `COPYING` (GPL-3 verbatim),
`NOTICE.md` (atribusi Arc + catatan perubahan), `SHA256SUMS.txt` (128 entri).

### 3.1 Verifikasi

| Pemeriksaan | Hasil |
|---|---|
| `url()` refs valid | 124/124, 0 hilang |
| Biru Arc tersisa | **0** (hex, rgb, rgba) |
| Manifest SHA256 | **128/128 cocok** |
| Parse GTK 3.24.52 | 0 error |

### 3.2 Aset yang dihapus dari Arc

`thumbnail-frame.png` tidak dapat diproduksi: tidak ada id di `assets.svg`
maupun `assets.txt`, dan ekstraksi `gtk.gresource` mismatch 82/125. Rule
`.content-view.document-page` diganti `border-color: #667D89` (border solid).
Ini satu-satunya perubahan yang **menghapus** aset Arc.

---

## 4. Panel XFCE

Path: `image/config/includes.chroot/etc/xdg/xfce4/panel/default.xml`
Status: **ACTIVE** (lapisan default XDG)

| Properti | Panel 1 (atas) | Panel 2 (bawah) |
|---|---|---|
| Posisi | `p=6` (NW) | `p=10` (SC) |
| Tinggi | 32 px | 48 px |
| Panjang | 100 % | 520 px (piksel) |
| Icon size | 18 px | 32 px |
| Latar | Steel `#344653` alpha 1.0 | Porcelain `#F5F3EC` alpha 1.0 |
| Plugin | 8 | 7 |

Spesifikasi lengkap: `.../usr/share/oracle/design/panel/SPEC-PANEL.md`.

### 4.1 Plugin — semua bawaan `xfce4-panel`

`applicationsmenu`, `launcher`, `separator`, `tasklist`, `systray`, `clock`,
`showdesktop`. **Tidak ada paket plugin tambahan** yang dibutuhkan.

---

## 5. Terminal

| File | Path | Status |
|---|---|---|
| `oracle.theme` | `.../usr/share/xfce4/terminal/colorschemes/` | **IN REPO** |
| `terminalrc` | `.../etc/xdg/xfce4/terminal/` | **ACTIVE** |
| `oracle-APPLY.md` | `.../usr/share/xfce4/terminal/colorschemes/` | REFERENCE |

Palet ANSI 16 slot: lihat `MASTER-DESIGN.md` §4.1.

Verifikasi: `.theme` parse OK, 17 key, `ColorPalette` **16 entri** valid.

---

## 6. Papirus

Path: `image/config/includes.chroot/usr/share/icons/ORACLE-Papirus/`
Status: **IN REPO** · 394 file · SVG

| Metrik | Nilai |
|---|---:|
| Nama ikon wajib | 41 |
| Ukuran | 16, 22, 24, 32, 48, 64 |
| Diubah warna | 154 |
| Symbolic (tidak diubah) | 58 |
| Disalin apa adanya | 181 |
| Biru Papirus tersisa | **0** dari 393 SVG |

`index.theme`: `Inherits=Papirus,hicolor`.

Lisensi: `.../usr/share/doc/oracle-icons/` — `NOTICE.md` (GPL-3, atribusi
Papirus/Paper/Numix), `AUDIT-PAPIRUS.md`, `manifest.txt`.

### 6.1 Dependency kritis

`ORACLE-Papirus` butuh `papirus-icon-theme` terpasang (untuk inheritance) dan
`librsvg2-common` untuk render SVG. Yang terakhir **hanya Recommends** →
wajib ditulis eksplisit di package list. Sudah dilakukan di Stage 3B.

---

## 7. LightDM Greeter

| File | Path | Status |
|---|---|---|
| `lightdm-gtk-greeter.conf` (referensi) | `.../usr/share/oracle/design/greeter/` | **REFERENCE** |
| `oracle-greeter.css` | `.../usr/share/themes/ORACLE/gtk-3.0/` | **IN REPO** |

**`/etc/lightdm/lightdm-gtk-greeter.conf` SENGAJA tidak diubah** — masih
`[greeter]` kosong. Mengaktifkannya mengubah default desktop tervalidasi.

Spesifikasi: `.../usr/share/oracle/design/greeter/`. Audit lengkap di design
repository (`greeter/docs/AUDIT-GREETER.md`).

---

## 8. Dokumentasi di repo

| File | Fungsi |
|---|---|
| `docs/design/MASTER-DESIGN.md` | keputusan & spesifikasi final |
| `docs/design/ASSET-DOCUMENTATION.md` | dokumen ini |
| `docs/design/INTEGRATION-READINESS.md` | cara pasang, dependency, test |
| `docs/design/DECISION-HISTORY.md` | keputusan superseded & riwayat |
| `docs/design/ASSET-README.md` | geometri detail A1–A5 |
| `docs/design/audit-report.txt` | keluaran audit brand |
| `docs/design/RECONCILIATION-MATRIX.md` | dasar rekonsiliasi Stage 3B.1 |
| `.../usr/share/oracle/design/README.md` | posisi aset: mana aktif |
| `.../usr/share/oracle/design/{panel,terminal,greeter}/` | spesifikasi runtime |

---

## 9. Tools

Path: `tools/design/` · 16 file

**Status: arsip referensi, bukan bagian build.** 15 dari 16 tool memakai path
absolut ke design repository dan cache scratch, sehingga **tidak** bisa
dijalankan dari repo ini tanpa penyesuaian. Detail: `tools/design/README.md`.

---

## 10. Yang TIDAK ada di repo ini

| Aset | Alasan |
|---|---|
| Wallpaper SVG | hanya PNG yang dibutuhkan runtime |
| `thumbnail-frame.png` | tidak dapat diproduksi (lihat §3.2) |
| Preview PNG (`preview/`, `*/preview/`) | artefak review, bukan runtime |
| `gtk/pilot/`, `gtk/preview/` | artefak tahap pilot |
| `.deb`, cache, `.pyc` | bukan aset |
| Design repository | tetap terpisah sebagai arsip |

Design repository (`~/Projects/oracle-brand-assets`) **sengaja
dipertahankan** sebagai sumber dan arsip — bukan duplikasi, tetapi riwayat
lengkap termasuk generator, preview, dan dokumen audit per tahap.

---

## 11. Ringkasan ukuran

| Kelompok | File | Ukuran |
|---|---:|---|
| Brand | 10 | 40 K |
| Wallpaper | 4 | 128 K |
| GTK theme | 127 | 988 K |
| Papirus | 394 | 1,9 M |
| Terminal | 3 | 12 K |
| Panel | 1 | 8 K |
| Design refs | 8 | 44 K |
| Docs | 5 | 60 K |
| Tools | 16 | 200 K |

Total aset desain: ±3,4 M dari 573 file di commit Stage 3A.