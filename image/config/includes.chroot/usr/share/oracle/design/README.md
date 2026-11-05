# Design assets — posisi di repo ini

Direktori ini berisi **aset desain** dan **dokumentasi desain** yang sudah
disetujui. Isinya dipindahkan dari design repository
(`oracle-brand-assets`) pada Stage 3A.

---

## Status: ASET, BUKAN KONFIGURASI AKTIF

| Lokasi | Isi | Aktif? |
|---|---|---|
| `usr/share/themes/ORACLE/` | tema GTK3 | **belum** — belum ada di `xsettings` |
| `usr/share/icons/ORACLE-Papirus/` | tema ikon | **belum** — belum dipilih |
| `usr/share/backgrounds/oracle/` | wallpaper | **belum** — belum diset |
| `usr/share/oracle/branding/` | Dial, wordmark, lockup | referensi |
| `usr/share/xfce4/terminal/colorschemes/oracle.theme` | palette ANSI | **belum** — belum dipilih |
| `etc/xdg/xfce4/terminal/terminalrc` | font, cursor | **belum** — lihat catatan |
| `etc/xdg/xfce4/panel/default.xml` | layout 2 panel | **sudah** aktif (file default XDG) |
| `usr/share/oracle/design/` | spesifikasi, audit, referensi | dokumentasi |

### Dua yang sudah aktif

- `etc/xdg/xfce4/panel/default.xml` — lapisan default XDG, dibaca semua akun.
- `etc/xdg/xfce4/terminal/terminalrc` — idem.

Sisanya menunggu tahap implementasi: memilih tema lewat `xsettings`,
menyetel wallpaper lewat `xfce4-desktop`, memilih colorscheme terminal.

### LightDM greeter: SENGAJA belum aktif

`etc/lightdm/lightdm-gtk-greeter.conf` di repo ini **tidak diubah**. Isinya
masih `[greeter]` kosong seperti sebelumnya.

Konfigurasi greeter ORACLE disimpan sebagai **referensi** di
`usr/share/oracle/design/greeter/lightdm-gtk-greeter.conf`. Alasannya:
mengaktifkannya berarti mengubah default desktop yang sudah tervalidasi
(Phase 2 build), dan Stage 3A melarang itu.

---

## Catatan path absolut

`usr/share/oracle/design/terminal/AUDIT-TERMINAL.md` menyebut
`~/Projects/oracle-brand-assets/` **di dalam tabel audit** — itu catatan
historis tentang di mana palette lama dicari, bukan konfigurasi runtime.

Tidak ada konfigurasi runtime di direktori ini yang memakai path absolut
home directory. Semua path di file konfigurasi menunjuk ke filesystem
target (`/usr/share/...`, `/etc/...`).

---

## Kebutuhan paket

Dokumen lengkap: `docs/design/INTEGRATION-READINESS.md` §2.

Ringkas — paket yang **belum** ada di package list dan wajib ditambah:

| Paket | Alasan |
|---|---|
| `librsvg2-common` | tanpa ini ikon SVG **tidak tampil** (hanya Recommends) |
| `papirus-icon-theme` | `ORACLE-Papirus` Inherits=Papirus |
| `arc-theme` | basis tema GTK ORACLE |
| `fonts-inter` | `font-name=Inter 11` |
| `fonts-jetbrains-mono` | `FontName=JetBrains Mono 11` |
| `dmz-cursor-theme` | paket kursor; memasang theme `DMZ-Black` dan `DMZ-White` (runtime memakai `DMZ-Black`) |
| `hicolor-icon-theme` | fallback ikon |

Semua terverifikasi ada di Debian 13 Trixie `main`.