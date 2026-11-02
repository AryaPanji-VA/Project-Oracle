# ORACLE-OS — Terminal: Spesifikasi Visual

Stage 2E. Retro Industrial, Light-first, Flat.
Target: `xfce4-terminal 1.1.4-1` (Debian 13 Trixie).

---

## 1. Konsep

Terminal adalah tempat kerja sebenarnya di ORACLE-OS. Panel boleh tenang,
tapi terminal harus **terbaca berjam-jam**. Karena itu latar yang dipakai
Porcelain (bukan Ivory): lebih terang, memberi ruang kontras lebih besar
untuk 16 warna, dan memisahkan jendela terminal dari wallpaper.

Warna hanya dipakai kalau membawa makna: perintah, path, string, angka,
status. Tidak ada warna hiasan. Palet tetap earthy — saturasi dikunci 0.50,
jadi tidak ada yang menyala seperti terminal tema neon.

---

## 2. Dasar

| Properti | Nilai | Kontras |
|---|---|---:|
| Latar | Soft Porcelain `#F5F3EC` | — |
| Teks | Graphite `#30363B` | **11.02:1** |
| Font | JetBrains Mono 11 pt | — |
| Bold | tetap Graphite (bukan bright) | — |
| Cursor | blok, Steel `#344653`, teks Porcelain | **8.81:1** |
| Cursor blink | mati (Flat, tenang) | — |
| Selection | Steel `#344653`, teks Porcelain | **8.81:1** |
| Background vary | mati | — |
| Scrollbar | disembunyikan | — |

### Kenapa cursor Steel, bukan Graphite

Blok cursor Graphite akan menyatu dengan teks di sekitarnya. Steel memberi
blok yang jelas berbeda tanpa jadi warna baru.

### Kenapa cursor tidak berkedip

Kedipan menarik perhatian terus-menerus. "Work with clarity." lebih tenang
tanpa kedip. Ini preferensi desain yang disengaja, bukan default.

---

## 3. ANSI 16 warna

| Slot | Nama | Hex | Kontras | Peran |
|---:|---|---|---:|---|
| 0 | black | `#30363B` | 11.02:1 | teks utama, argumen |
| 1 | red | `#B4503C` | 4.55:1 | error |
| 2 | green | `#317E2A` | 4.56:1 | sukses, string |
| 3 | yellow | `#8A682E` | 4.61:1 | warning |
| 4 | blue | `#3674A1` | 4.54:1 | perintah, direktori |
| 5 | magenta | `#B83D99` | 4.54:1 | angka |
| 6 | cyan | `#2B7682` | 4.71:1 | key, branch |
| 7 | white | `#667D89` | 3.89:1 | UI saja (bukan teks) |
| 8 | bright black | `#B9C1C2` | 1.65:1 | dekor / border |
| 9 | bright red | `#C33D22` | 4.72:1 | error tegas |
| 10 | bright green | `#26801E` | 4.52:1 | sukses tegas |
| 11 | bright yellow | `#90661E` | 4.61:1 | warning tegas |
| 12 | bright blue | `#1F72AE` | 4.64:1 | perintah tegas |
| 13 | bright magenta | `#C8239F` | 4.51:1 | angka tegas |
| 14 | bright cyan | `#1B7987` | 4.58:1 | key tegas |
| 15 | bright white | `#E9E5DA` | 1.13:1 | paling terang, dekat latar |

Slot 7, 8, 15 berperan sebagai permukaan/dekor, bukan teks isi — sama seperti
konvensi light scheme Debian (`xterm`, `solarized-light`).

---

## 4. Peta peran semantik

| Peran | Slot | Warna | Kontras |
|---|---:|---|---:|
| perintah / command | 4 | `#3674A1` | 4.54:1 |
| argumen | 0 | `#30363B` | 11.02:1 |
| string | 2 | `#317E2A` | 4.56:1 |
| angka | 5 | `#B83D99` | 4.54:1 |
| direktori | 4 | `#3674A1` | 4.54:1 |
| sukses | 2 | `#317E2A` | 4.56:1 |
| warning | 3 | `#8A682E` | 4.61:1 |
| error | 1 | `#B4503C` | 4.55:1 |
| key / branch | 6 | `#2B7682` | 4.71:1 |
| komentar / dim | turunan | `#5B707B` | 4.67:1 |
| aksen prompt | brand | Brass Ink `#8C7B58` | 3.72:1 |

### Prompt

```
▏oracle@workstation:~/src$
```

| Bagian | Warna |
|---|---|
| `▏` indikator | Brass Ink `#8C7B58` — satu-satunya aksen |
| `oracle` | green, bold |
| `@` | dim |
| `workstation` | green, bold |
| `:` | dim |
| `~/src` | blue, bold |
| `$` | dim |

Tanda `▏` adalah sisa bahasa visual logo Dial: satu tick tipis di kiri,
bukan blok penuh. Brass Ink dipakai karena latar terang — Muted Brass
hanya 2.08:1 di Porcelain.

---

## 5. Contoh isi yang dipreview

| File | Isi |
|---|---|
| `terminal-main.png` | `ls -la`, `git status`, `make build` (warning + error + exit code) |
| `terminal-syntax.png` | shell script: komentar, shebang, variabel, string, angka, kondisional, status ✓ ⚠ ✗ |
| `palette-sheet.png` | 16 swatch + hex + kontras |
| `semantic-sheet.png` | peta peran → slot → warna |

Semua berlabel **MOCKUP STATIS**.

---

## 6. Yang sengaja TIDAK dipakai

| Hal | Alasan |
|---|---|
| Latar gelap | Light-first |
| Transparansi / blur | tanpa compositor |
| Cursor berkedip | "Work with clarity." — tenang |
| Bold → bright | di light theme menurunkan keterbacaan |
| Bright = lebih terang | justru menghilang di latar terang |
| Warna neon | saturasi dikunci 0.50, Retro Industrial |
| Scrollbar terlihat | Flat, ruang baca maksimal |
| `ColorBackgroundVary` | variasi latar mengganggu flat |
| Italic khusus | tidak ada hue tambahan untuk itu |

---

## 7. Cara pakai (belum diterapkan)

Tema: `cfg/oracle.theme` → salin ke
`~/.local/share/xfce4/terminal/colorschemes/oracle.theme`, lalu pilih
**ORACLE** di *Preferences → Colors*.

Key non-warna (font, cursor, scrollbar): `cfg/terminalrc.fragment` — salin
**hanya key** ke `terminalrc`, jangan menimpa file utuh.

Detail lengkap: `cfg/APPLY.md`.