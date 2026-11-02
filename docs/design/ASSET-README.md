# ORACLE-OS — Aset Brand Tahap 1 (Dial, Wordmark, Lockup)

> **Status:** Selesai, menunggu review Arya.
> **Lokasi:** `~/Projects/oracle-brand-assets/` — **di luar** source sistem
> ORACLE (repo `~/Projects/Oracle-OS` tidak tersentuh).
> **Tanggal:** 2026-11-02 · **Identitas:** Knowledge · Timeless · Retro Industrial · Light-first.
>
> Semua angka di dokumen ini **terukur**, bukan diperkirakan. Asal angka:
> pengukuran piksel dari brand guide yang disepakati (Sesi desain) dan
> pembacaan atribut secara langsung dari berkas SVG, serta penghitungan kontras
> WCAG dari nilai hex. Metode lengkap ada di `tools/audit_assets.py`.

---

## 1. Inventaris file

### Peran aset vs varian

`dial-master.svg` (dan `lockup-horizontal.svg` yang mewarisi geometrinya)
adalah **sumber geometri/master** — tempat geometri kanonik didefinisikan,
dipakai sebagai acuan generasi dan audit. Ia memakai warna default
(Steel Blue + Muted Brass) yang **tidak** dijamin aman di semua latar.

Untuk penggunaan sesuai latar, pilih varian:

- `variants/*-light.svg` → latar terang (Warm Ivory / Soft Porcelain)
- `variants/*-dark.svg`  → latar gelap (Steel Blue / Graphite)
- `variants/*-mono.svg`  → satu tinta (dokumen/cetak B/W)

Jangan memakai `dial-master.svg` langsung sebagai logo di latar terang;
gunakan varian light agar kontras tick terpenuhi (lihat §5).

### Struktur file

```
oracle-brand-assets/
├── svg/
│   ├── dial-master.svg            # A1  Dial master (ring + slot + tick)
│   ├── dial-optical-16.svg        # A2  Varian optical untuk ukuran ≤ 16 px
│   ├── wordmark.svg               # A3  Wordmark ORACLE (outline vektor)
│   ├── lockup-horizontal.svg      # A4  Lockup: mark + wordmark
│   └── variants/
│       ├── dial-light.svg         # A5  Dial, latar terang
│       ├── dial-dark.svg          # A5  Dial, latar gelap
│       ├── dial-mono.svg          # A5  Dial, satu tinta
│       ├── lockup-light.svg       # A5  Lockup, latar terang
│       ├── lockup-dark.svg        # A5  Lockup, latar gelap
│       └── lockup-mono.svg        # A5  Lockup, satu tinta
├── preview/
│   ├── dial-master-{16,24,32,48}px.png      # preview per ukuran
│   ├── dial-optical16-{16,24,32,48}px.png   # preview per ukuran
│   └── preview-sheet.png                    # lembar review gabungan
├── tools/
│   ├── gen_assets.py             # generator (satu-satunya sumber geometri)
│   ├── audit_assets.py           # audit: verifikasi angka dari berkas
│   └── make_preview_sheet.py     # lembar review
└── docs/
    ├── README.md                 # dokumen ini
    └── audit-report.txt          # keluaran audit terakhir
```

**Jumlah: 10 SVG, 9 PNG preview, 3 tool.** Semua SVG murni vektor (tidak ada
`<image>` atau data URI tertanam — diverifikasi oleh audit).

---

## 2. Geometri Dial — nilai yang dipakai

Rasio dinyatakan terhadap **diameter lingkaran luar ring (Ø)**.

| Parameter | Simbol | Master | Optical 16 px | Asal angka |
|---|---|---|---|---|
| Stroke ring | `stroke/Ø` | **0,1250** | 0,1250 (sama) | terukur: 11,5/92 dari brand guide |
| Lebar slot (celah puncak) | `slot/Ø` | **0,1739** | **0,2800** | master: 16/92; optical: diset agar simetris di 16 px |
| Lebar tick | `tick_w/Ø` | **0,1087** | **0,1150** | master: 10/92 |
| Tinggi tick | `tick_h/Ø` | **0,3913** | 0,4100 | master: 36/92 |
| Menonjol melewati ring | `protrude/Ø` | **0,0543** | 0,0770 | master: 5/92 |
| Jarak mark → wordmark | `gap/Ø` | **0,4565** | — | 42/92 |
| Cap-height wordmark | `cap/Ø` | **0,5109** | — | 47/92 |

**Bentuk mark:** ring digambar sebagai **satu busur terbuka**; celah (slot) ada
di 12 o'clock; **tick adalah bar tegak di dalam slot itu**, selebar sedikit
lebih sempit dari slot, menonjol ke atas melewati tepi luar ring, dan
menurun melewati tepi dalam ring. Tick **bukan** elemen yang menempel di luar
ring.

### 2.1 Kenapa optical 16 px berbeda

Pada ukuran kecil (16 px), proporsi master membuat tick terbaca **menempel ke
salah satu sisi** (celah kiri dan kanan tidak sama). Varian optical melebarkan
slot supaya celah kiri dan kanan tick **sama** di 16 px — terbukti dengan
pengukuran simetri, bukan dengan perasaan:

| Varian | Celah kiri | Celah kanan | Simetris |
|---|---|---|---|
| master | 2 px | 1 px | ❌ |
| **optical-16** | **2 px** | **2 px** | ✅ |

Aturan pakai: **master di 24 px ke atas; optical-16 hanya untuk ≤ 16 px.**

---

## 3. Clear space

Uang aman minimum di sekeliling aset:

| Aset | Clear space minimum |
|---|---|
| Dial (stand-alone) | **0,25 × Ø** di semua sisi (termasuk di atas tick yang menonjol) |
| Wordmark | **0,25 × cap-height** di semua sisi |
| Lockup | **0,25 × Ø** (diukur dari Ø ring) di semua sisi |

Alasan: 0,25 × Ø dipilih karena ini separuh dari jarak mark→wordmark yang
sudah ditetapkan (0,4565 × Ø), jadi tidak menimbulkan "jarak baru" yang aneh,
dan tetap memberi ruang napas saat dipakai berdampingan dengan elemen lain.

---

## 4. Ukuran minimum

| Aset | Minimum | Catatan |
|---|---|---|
| Dial | Ø **16 px** | wajib pakai `dial-optical-16.svg`; di bawah 16 px, bentuk tidak lagi terbaca |
| Lockup | Ø ring **48 px** (≈ 242 px lebar keseluruhan) | lebih kecil dari ini, cap-height wordmark turun di bawah 8 px |
| Wordmark | cap-height **10 px** | tidak disarankan di bawah ini pada media cetak |

Aturan turunan: **jangan pernah menurunkan skala secara otomatis tanpa
mengganti varian** — turunkan dari master dengan SVG (vektor, aman), atau
pakai PNG preview yang sudah disediakan pada ukuran tepat.

---

## 5. Varian warna dan aturan penggunaan

| Varian | Ring | Tick | Wordmark | Dipakai pada |
|---|---|---|---|---|
| **Light** | Steel Blue `#344653` | **Brass Ink** `#8C7B58` | Steel Blue | Latar Warm Ivory / Soft Porcelain |
| **Dark** | Soft Porcelain `#F5F3EC` | Muted Brass `#B8A98D` | Soft Porcelain | Latar Steel Blue / Graphite |
| **Monochrome** | Graphite `#30363B` | Graphite (sama dengan ring) | Graphite | Dokumen satu warna, cetak hitam-putih, stempel |

Aturan yang **terverifikasi angka** (bukan selera):

1. **Muted Brass TIDAK boleh** menjadi tick di latar terang: kontras 2,08:1
   terhadap Warm Ivory — gagal ambang 3:1 untuk grafis. Varian light memakai
   **Brass Ink** (3,72:1 ✓).
2. **Muted Brass sah** di latar gelap: 4,24:1 terhadap Steel Blue ✓.
3. Varian **monochrome** memakai **satu tinta** (`#30363B`); tick digambar
   dengan warna yang sama dengan ring, bukan dua warna yang kebetulan mirip.
   Hasil diukur: tepat 1 warna unik di dalam SVG.

### 5.1 Palet merek

| Nama | Hex | Peran |
|---|---|---|
| Warm Ivory | `#E9E5DA` | Latar utama |
| Soft Porcelain | `#F5F3EC` | Permukaan terangkat |
| Steel Blue | `#344653` | Aksen utama, teks terang, ring light |
| Dusty Blue | `#667D89` | Aksen sekunder, ring wallpaper (18%) |
| Muted Brass | `#B8A98D` | Aksen metalik — **hanya di atas bidang gelap** |
| Graphite | `#30363B` | Teks utama, monokrom |
| Brass Ink | `#8C7B58` | Tick varian light saja |

---

## 6. Wordmark

- Font: **Inter SemiBold** (keluarga `fonts-inter` di Debian 13/trixie).
- Bentuk: **outline vektor** (path dari `fontTools`), bukan `<text>` — jadi
  konsisten di semua perender tanpa bergantung font terpasang.
- Cap height: 119 unit pada kanvas master.
- Tracking: **0,2500 em** (spasi huruf yang dipakai di brand guide).
- Verifikasi: render SVG dibandingkan dengan render font asli pada ukuran sama
  → **IoU 0,902** (kemiripan bentuk ≥ 90%).

---

## 7. Cara regenerasi

```sh
# di direktori aset
~/.hermes/profiles/doraemon/cache/scratch/oracle-design/.venv/bin/python tools/gen_assets.py
~/.hermes/profiles/doraemon/cache/scratch/oracle-design/.venv/bin/python tools/audit_assets.py
~/.hermes/profiles/doraemon/cache/scratch/oracle-design/.venv/bin/python tools/make_preview_sheet.py
```

Ketergantungan: `fontTools` + `Pillow` + `numpy` (venv lokal di scratch, bukan
paket sistem), `rsvg-convert`, `xmllint`. **Tidak ada paket Debian yang
dipasang ke host.**

---

## 8. Batas audit ini (harus dibaca sebelum menyimpulkan)

1. Kecocokan bentuk diukur dari **raster rsvg**, bukan dari sesi XFCE/QEMU
   yang sebenarnya. Tahap bukti visual sesungguhnya ada di tahap tema/kustomisasi.
2. Preview 16/24/32/48 px adalah **ukuran render diameter ring**, bukan ukuran
   kanvas. SVG tetap vektor penuh.
3. Kontras dihitung dari **nilai hex**, bukan diukur dari layar fisik.
4. Angka IoU terhadap brand guide terbatas resolusi (ikon di guide diskalakan
   2×). Angka yang dipakai untuk keputusan adalah **rasio geometris** — yang
   dibaca eksak dari atribut SVG.

---

## 9. Yang belum dikerjakan (di luar Tahap 1)

- Wallpaper (Workspace & Minimal) — **Tahap 2**.
- Tema GTK3 (basis Arc, dimodifikasi minimal) — **Tahap 3**.
- Konfigurasi panel, greeter, terminal — **Tahap 4**.
- Aset ini **belum** digabungkan ke repo ORACLE (`~/Projects/Oracle-OS`).