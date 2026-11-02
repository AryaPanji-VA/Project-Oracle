# ORACLE-OS — Master Design Document

Status: **FINAL untuk Stage 2** (A1–A5, Wallpaper, GTK, Panel, Terminal,
Papirus, Greeter). Menunggu persetujuan sebelum Stage 3.

Dokumen ini adalah rujukan tunggal keputusan desain. Bila ada konflik antara
dokumen ini dan dokumen tahap, **dokumen ini yang berlaku**.

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
| UI font | Inter |
| Terminal font | JetBrains Mono |

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

### 2.1 Aturan Brass (terukur, tidak bisa ditukar)

| Warna | di Steel (gelap) | di Porcelain (terang) |
|---|---:|---:|
| Muted Brass `#B8A98D` | **4.24:1** ✓ | 2.08:1 ✗ |
| Brass Ink `#8C7B58` | 2.37:1 ✗ | **3.72:1** ✓ |

Muted Brass **hanya** untuk latar gelap; Brass Ink **hanya** untuk latar
terang. Ini bukan preferensi — sudah dihitung.

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
sinyal keselamatan. Karena itu warna status dipertahankan/diturunkan:

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

### 4.2 GTK status (dipertahankan dari Arc)

16 warna: `#FC4138 #FD8D88 #F27835 #F7AE86 #F04A50 #F4797E #EC1B22
#F08437 #FF4D4D #FF6666 #FD716A #F75D37 #73D216 #F13039 #F46067 #F68086`

Konsekuensi: 10 rule GTK berada di 3.38–4.38:1 (bukan 4.5:1). **Ini
pengecualian yang disepakati**, bukan kelalaian. Dibanding Arc asli,
mayoritas justru membaik (`entry.warning` 1.85 → 6.61:1).

---

## 5. Aset per tahap

| Tahap | Aset | Status | Lokasi |
|---|---|---|---|
| A1–A5 | Dial master, optical 16px, wordmark, lockup, 3 varian | APPROVED | `svg/` |
| Stage 2 | Workspace + Minimal wallpaper (1920×1200, 1280×800) | APPROVED | `wallpaper/` |
| 2C | GTK theme (Arc fork, 124 PNG) | APPROVED | `gtk/ORACLE/` |
| 2D | XFCE panel (2 panel, xfconf) | APPROVED | `panel/` |
| 2E | Terminal ANSI 16-color | APPROVED | `terminal/` |
| 2F-A | Papirus icon theme (recolor terbatas) | BARU | `papirus/` |
| 2F-B | LightDM greeter | BARU | `greeter/` |

---

## 6. Kontras kunci lintas aset

| Konteks | fg / bg | Kontras |
|---|---|---:|
| GTK teks window | Graphite / Ivory | 9.72:1 |
| GTK headerbar | Porcelain / Steel | 8.81:1 |
| Panel atas | Porcelain / Steel | 8.81:1 |
| Panel bawah | Graphite / Porcelain | 11.02:1 |
| Terminal teks | Graphite / Porcelain | 11.02:1 |
| Greeter panel | Porcelain / Steel | 8.81:1 |
| Greeter login | Graphite / Porcelain | 11.02:1 |

---

## 7. Pengecualian yang disengaja (jujur, tidak disembunyikan)

| # | Pengecualian | Alasan | Dampak |
|---|---|---|---|
| 1 | 10 rule GTK status di 3.38–4.38:1 | palet tanpa warna status | teks status sedikit di bawah AA |
| 2 | `thumbnail-frame.png` dihapus, diganti border solid | aset tidak dapat diproduksi (tidak ada id di assets.svg) | sudut thumbnail dokumen jadi garis |
| 3 | Slot ANSI 7/8/15 di bawah 4.5:1 | peran latar/dekor, konvensi light scheme Debian | tidak untuk teks isi |
| 4 | Ikon Papirus symbolic tidak di-recolor | `currentColor` mengikuti tema GTK | warna ikut konteks (benar) |
| 5 | Border `#B9C1C2` 1.65:1 | dekoratif, bukan indikator fungsional | tidak tunduk WCAG 1.4.11 |
| 6 | Panel bawah vs wallpaper 1.13:1 | Light-first, tenang | **wajib** border Dusty 3.89:1 |
| 7 | Greeter mungkin tidak tampil saat boot | autologin aktif di live image | relevan hanya saat logout |

---

## 8. Lisensi & atribusi

| Aset | Lisensi | Kewajiban |
|---|---|---|
| A1–A5, wallpaper, panel, terminal, greeter | karya ORACLE | — |
| GTK theme | **GPL-3+** (turunan Arc) | sertakan source + COPYING + NOTICE |
| Papirus | **GPL-3** (turunan Papirus) | sertakan source + NOTICE |

Dokumen lengkap: `gtk/ORACLE/NOTICE.md`, `papirus/docs/NOTICE.md`.

---

## 9. Prinsip yang dipegang

1. **Bukti di atas klaim.** Setiap angka kontras dihitung, setiap key
   konfigurasi diverifikasi ada di binary.
2. **Fail-closed.** Validator mengembalikan exit code; tidak ada "dianggap
   lulus".
3. **Pengecualian dicatat.** Tidak ada kegagalan kontras yang disembunyikan.
4. **Aset pihak ketiga dihormati.** Papirus dan Arc di-recolor terbatas,
   bentuk aslinya dipertahankan.
5. **Tidak mengarang.** Tidak ada key konfigurasi, nama ikon, atau path yang
   tidak terverifikasi.