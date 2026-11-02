# ORACLE-Papirus — Asal-usul, Lisensi, Atribusi

Dokumen ini wajib ikut terdistribusi bersama tema ikon ORACLE-Papirus.

---

## 1. Karya asli

| Field | Nilai |
|---|---|
| Nama | Papirus Icon Theme |
| Versi dipakai | `20250501-1` (Debian `papirus-icon-theme`) |
| Upstream | https://github.com/PapirusDevelopmentTeam/papirus-icon-theme |
| Lisensi | **GPL-3** |
| Section | x11 |
| Depends | `hicolor-icon-theme` |
| Recommends | `librsvg2-common` |

### Kredit upstream (dari `usr/share/doc/papirus-icon-theme/copyright`)

```
Copyright: 2016-2017 Alexey Varfolomeev <varlesh@gmail.com>
           2016-2017 Sergei Eremenko <finalitik@gmail.com>
           2016-2017 Papirus Development Team
License: GPL-3
```

Asal-usul yang dicatat upstream:

- **Paper Icon Theme** — Sam Hewitt (https://samuelhewitt.com), LGPL-3
- **Numix icon theme** — Numix Project, GPL-3

---

## 2. Kewajiban GPL-3

ORACLE-Papirus adalah karya turunan Papirus. Karena itu:

1. **Sumber lengkap wajib tersedia** — `theme/ORACLE-Papirus/` (SVG hasil
   recolor), `manifest.txt`, dan skrip generator `tools/gen_papirus.py`.
2. **Lisensi tetap GPL-3** — tidak boleh diperketat.
3. **Atribusi dipertahankan** — Papirus, Alexey Varfolomeev, Sergei Eremenko,
   Papirus Development Team, Paper, dan Numix harus tetap disebut.
4. **Perubahan dinyatakan** — bagian 3 di bawah.
5. **Tanpa garansi.**

---

## 3. Catatan perubahan terhadap Papirus

### 3.1 Strategi: Papirus penuh, bukan Papirus-Light

**Bukti yang menentukan** (lihat `docs/AUDIT-PAPIRUS.md` §3):

- Papirus-Light **tidak memiliki satu pun** dari 20 ikon XFCE yang dipakai
  `.desktop` di image (`org.xfce.terminalemulator`, `org.xfce.filemanager`,
  `org.xfce.panel`, `xfsm-logout`, dan seterusnya).
- Papirus-Light juga tidak punya `folder`, `user-home`, `edit-copy`,
  `view-refresh`.
- `Papirus-Light/index.theme` berisi `Inherits=breeze,hicolor` — **bukan**
  Papirus. Jadi ikon yang hilang jatuh ke `hicolor`, bukan ke Papirus.
- Papirus penuh punya **semua** ikon tersebut (0 hilang dari 20).

Karena itu ORACLE-Papirus dibangun dari **Papirus penuh**, dengan
`Inherits=Papirus,hicolor` agar ikon di luar subset tetap tersedia.

### 3.2 Recolor terbatas — hanya aksen

Yang diubah **hanya warna aksen**. Bentuk, geometri, path, dan detail visual
Papirus dipertahankan apa adanya. Tidak ada ikon yang digambar ulang.

| Warna Papirus | Menjadi | Peran |
|---|---|---|
| `#5294E2` | Steel Blue `#344653` | aksen utama |
| `#4877B1` | `#2A3A45` | aksen gelap (bayangan folder) |
| `#1D344F` | `#1F2A33` | aksen sangat gelap |
| `#3EA0F4` | Dusty Blue `#667D89` | aksen terang (browser) |
| `#0090EF` | Dusty Blue `#667D89` | aksen terang (appfinder) |
| `#4354CB` | Steel Blue `#344653` | aksen ungu-biru (browser) |
| `#89E058` | `#4E7A3A` | hijau filemanager → hijau earthy |
| `#FFCD54` | Brass Ink `#8C7B58` | kuning filemanager → brass |

Catatan: `#5294E2` adalah biru aksen Papirus yang **kebetulan sama** dengan
biru aksen Arc. Pemetaan ke Steel konsisten dengan keputusan GTK theme.

### 3.3 Ikon symbolic TIDAK di-recolor

Papirus punya dua jenis ikon yang berbeda secara struktural:

| Ukuran | Jenis | Warna |
|---|---|---|
| 16×16 | symbolic | `fill:currentColor` + class `ColorScheme-*` |
| 22px ke atas | berwarna | hex langsung (`#5294e2` dsb) |

Ikon 16×16 memakai `currentColor`, sehingga warnanya **mengikuti warna teks
GTK** dari tema ORACLE — bukan hex tetap. Recolor hex tidak berpengaruh dan
tidak dilakukan. Ini disengaja: symbolic harus tetap mengikuti konteks
(terang di panel gelap, gelap di permukaan terang).

Jumlah: 58 file symbolic disalin apa adanya.

### 3.4 Cakupan

| Kategori | Jumlah file |
|---|---:|
| Diubah warna | 56 |
| Symbolic (tidak diubah) | 58 |
| Disalin apa adanya | 279 |
| **Total** | **393** |

41 nama ikon wajib, tersedia di 6 ukuran (16, 22, 24, 32, 48, 64).

---

## 4. Struktur distribusi

```
ORACLE-Papirus/
├── index.theme          Inherits=Papirus,hicolor
├── 16x16/ 22x22/ 24x24/ 32x32/ 48x48/ 64x64/
└── (subset ikon wajib)
```

`index.theme` menyatakan `Inherits=Papirus,hicolor`, jadi tema ini **butuh
paket `papirus-icon-theme` terpasang**. Tanpa itu, ikon di luar subset akan
jatuh ke `hicolor` dan tampil generik.

---

## 5. Yang TIDAK boleh dilakukan

- Menjual tema tanpa menyertakan source dan lisensi.
- Mengganti lisensi menjadi proprietary.
- Menghapus atribusi Papirus.
- Mengklaim ikon ini karya orisinal.
