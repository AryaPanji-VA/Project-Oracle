# ORACLE GTK Theme — Asal-usul, Lisensi, dan Atribusi

Dokumen ini wajib ikut terdistribusi bersama tema ORACLE (Stage 2C).
Tema ORACLE adalah **karya turunan** (derivative work) dari tema Arc.

---

## 1. Karya asli

| Field | Nilai |
|---|---|
| Nama | Arc Theme |
| Versi yang dipakai | `20221218-1` (Debian `arc-theme`) |
| Upstream | https://github.com/jnsh/arc-theme |
| Tag upstream | `20221218` |
| Desainer asli | horst3180 — https://github.com/horst3180/arc-theme |
| Pemelihara fork | jnsh (dan kontributor) |
| Lisensi | **GNU General Public License v3.0 or later (GPL-3+)** |
| Maintainer paket Debian | David Mohammed `<fossfreedom@ubuntu.com>` |
| Homepage paket | https://github.com/jnsh/arc-theme |
| Section / Priority | misc / optional |

Catatan sejarah: Arc dirancang dan dikembangkan oleh **horst3180**; proyek
tersebut tidak dirawat sejak Mei 2017. Fork **jnsh/arc-theme** melanjutkan
pemeliharaan tanpa mengubah desain visual aslinya.

### Sumber yang dipakai untuk menghasilkan tema ini

| Bahan | Path / asal | Peran |
|---|---|---|
| CSS Arc light | `arc-gtk-main.css` (hasil build dari source `20221218`) | dasar `gtk.css` |
| Aset SVG | `common/gtk-3.0/assets/assets.svg` (source tarball upstream) | sumber render 124 PNG |
| Teks lisensi | `COPYING` (source tarball upstream) | GPL-3, disalin apa adanya |

SHA-256 berkas `COPYING` upstream:
```
3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986
```

---

## 2. Kewajiban GPL-3+ atas karya turunan

Karena ORACLE GTK Theme mendistribusikan karya turunan Arc, maka:

1. **Sumber lengkap wajib tersedia.** Yang harus disertakan: `gtk.css`
   hasil recolor, seluruh `assets/*.png`, skrip generator
   (`tools/gtk_recolor.py`), serta berkas `assets/oracle-assets.svg`
   (SVG terecolor yang menjadi sumber render aset).
2. **Lisensi tidak boleh diperketat.** Tema ORACLE tetap GPL-3+; tidak boleh
   didistribusikan di bawah lisensi yang lebih restriktif.
3. **Atribusi dipertahankan.** Nama Arc, horst3180, dan jnsh/arc-theme harus
   tetap disebut; dokumen ini dan `COPYING` wajib ikut dalam distribusi.
4. **Perubahan harus dinyatakan.** Bagian 3 di bawah adalah catatan perubahan
   (state the changes), sesuai GPL-3 §5(a).
5. **Tanpa garansi.** Distribusi tanpa jaminan apa pun, sesuai GPL-3 §15–16.

### Yang TIDAK boleh dilakukan
- Menjual tema ORACLE tanpa menyertakan source dan lisensi.
- Mengganti lisensi menjadi proprietary atau menambahkan larangan tambahan.
- Menghapus atribusi Arc dari dokumentasi distribusi.

---

## 3. Catatan perubahan terhadap Arc (GPL-3 §5(a))

Perubahan dilakukan **hanya pada warna** (recolor), bukan pada struktur atau
perilaku CSS. Tidak ada selector, ukuran, radius, animasi, atau logika state
Arc yang diubah.

### 3.1 Perubahan warna CSS

Recolor dilakukan **deterministik** lewat `tools/gtk_recolor.py` dengan tiga
lapis pemetaan:

1. **GLOBAL_MAP** — hex → palet ORACLE berdasarkan peran semantik.
2. **RGBA_MAP** — triple `rgba(r,g,b,a)` → palet ORACLE, alpha dipertahankan.
3. **SPECIAL_RULES** — koreksi untuk selector yang warnanya berperan ganda.
4. **`_fix_fg_contrast`** — pass terakhir: jika `color:` tidak mencapai
   kontras 4.4:1 terhadap `background-color` eksplisit pada rule yang sama,
   warna teks diganti ke kandidat terbaik di antara `Porcelain` dan `Graphite`.

### 3.2 Pemetaan semantik utama

| Peran Arc | Warna Arc | Warna ORACLE |
|---|---|---|
| Aksen / biru interaktif | `#5294E2` | Steel Blue `#344653` |
| Permukaan base / putih | `#FFFFFF` | Soft Porcelain `#F5F3EC` |
| Latar window | `#F5F6F7` | Warm Ivory `#E9E5DA` |
| Headerbar / titlebar | `#E7E8EB` | Steel Blue `#344653` |
| Teks gelap | `#5C616C`, `#2D323D` | Graphite `#30363B` |
| Abu netral terang | `#CFD6E6`, `#D4D5DB` | `#B9C1C2` |
| Headerbar aktif | `#5E6C75` | `#5E6C75` (dipertahankan) |
| Teks disabled | `#AAABA9` | `#929494` |

### 3.3 Pengecualian yang disengaja — warna status

Palet ORACLE **tidak mendefinisikan warna status**. Mengganti warna
error/warning/success/destructive dengan warna palet akan menghilangkan
makna sinyal keselamatan (mis. tombol destruktif tidak lagi terlihat
berbahaya). Karena itu 16 warna status Arc **dipertahankan apa adanya**:

```
error       #FC4138  #FD8D88  #EEA279  #F4807B
warning     #F27835  #F7AE86  #F08437
destructive #F04A50  #F4797E  #EC1B22
lain        #FF4D4D  #FF6666  #FD716A  #F75D37  #73D216
wm close    #F13039  #F46067  #F68086
```

Konsekuensi terukur: pada 10 rule status, kontras teks berada di 3.38–4.38:1
(bukan 4.5:1). Ini **batas palet**, bukan kelalaian — dan dibandingkan Arc
asli, mayoritas justru membaik:

| Rule | Arc asli (putih) | ORACLE |
|---|---:|---:|
| `entry.warning` | 1.85:1 | 6.61:1 |
| `entry.warning:focus` | 2.79:1 | 4.38:1 |
| `entry.error` | 2.25:1 | 5.44:1 |
| `entry.error:focus` | 3.53:1 | 3.47:1 |
| `button.destructive-action` | 3.62:1 | 3.38:1 |
| `.conflict-row` | 3.53:1 | 3.47:1 |

### 3.4 Perubahan yang menghapus satu aset

Rule `.content-view.document-page` di Arc memakai
`border-image: url("assets/thumbnail-frame.png")`. Aset ini **tidak dapat
diproduksi ulang**: tidak ada id `thumbnail-frame` di `assets.svg` maupun
`assets.txt` upstream (terverifikasi), dan ekstraksi dari `gtk.gresource`
tidak dapat diandalkan (pemetaan nama→blob mismatch 82/125).

Keputusan: `border-image` diganti **`border-color: #667D89`** (border solid
Dusty Blue). Ini menjaga seluruh referensi aset valid tanpa mengarang aset.
Perubahan visual: sudut thumbnail dokumen tidak lagi memakai frame
bergambar, melainkan garis solid.

### 3.5 Perubahan warna aset PNG

- 124 PNG di-render ulang dari `assets.svg` yang telah di-recolor.
- Warna aset dipetakan memakai `ASSET_MAP` + `GLOBAL_MAP`.
- Alpha, dimensi, dan bentuk dipertahankan; **tidak ada** aset yang digambar
  ulang atau di-resize manual.
- Verifikasi: 0 piksel biru Arc `#5294E2` tersisa; 97,9% piksel opaque tepat
  pada warna palet, sisa 2,1% adalah gradien anti-aliasing.

---

## 4. Cara menyertakan dokumen ini dalam distribusi

Struktur distribusi minimal:

```
ORACLE/
├── COPYING                  # GPL-3, salinan utuh dari Arc upstream
├── NOTICE.md                # dokumen ini
├── SHA256SUMS.txt           # manifest integritas
└── gtk-3.0/
    ├── gtk.css
    └── assets/  (124 PNG + oracle-assets.svg)
```

`COPYING` disalin **verbatim** dari source tarball Arc; jangan diedit.