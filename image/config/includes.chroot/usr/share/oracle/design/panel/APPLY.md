# ORACLE-OS — Cara Memasang Konfigurasi Panel

**Status: BELUM DITERAPKAN.** Dokumen ini instruksi untuk nanti, saat tahap
integrasi ISO. Jangan jalankan sekarang — batasan Stage 2D melarang
integrasi ke XFCE.

File: `panel/cfg/xfce4-panel.xml`
Target: `xfce4-panel 4.20.4-1` (Debian 13 Trixie), XFCE 4.20, X11.

---

## 1. Pemasangan sebagai default sistem (untuk live image)

Salin ke lapisan default XDG, **bukan** `/etc/skel`:

```sh
install -Dm644 panel/cfg/xfce4-panel.xml \
  /etc/xdg/xfce4/panel/default.xml
```

Alasan: `/etc/xdg` dibaca semua akun dan merupakan lapisan default resmi.
`/etc/skel` hanya menyemai home baru dan mudah tertimpa oleh apa yang
ditulis sesi setelahnya.

Bila `xfce4-panel` sudah berjalan, konfigurasi default baru hanya dipakai
saat belum ada `~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml`
milik user.

---

## 2. Pemasangan untuk satu user (uji manual)

```sh
mkdir -p ~/.config/xfce4/xfconf/xfce-perchannel-xml
install -m644 panel/cfg/xfce4-panel.xml \
  ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml
xfce4-panel --quit
xfce4-panel &
```

**Peringatan:** perintah di atas menimpa konfigurasi panel milik user yang
sedang login. Backup dulu:

```sh
cp -n ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml \
      ~/.config/xfce4/xfconf/xfce4-panel.xml.bak
```

---

## 3. Verifikasi setelah dipasang

```sh
xfconf-query -c xfce4-panel -p /panels -l          # daftar properti
xfconf-query -c xfce4-panel -p /panels/panel-1/size             # harus 32
xfconf-query -c xfce4-panel -p /panels/panel-2/size             # harus 48
xfconf-query -c xfce4-panel -p /panels/panel-1/background-style # harus 1
xfconf-query -c xfce4-panel -p /panels/panel-2/background-style # harus 1
```

`background-rgba` disimpan sebagai array double 0..1:

```sh
xfconf-query -c xfce4-panel -p /panels/panel-1/background-rgba
# diharapkan: 0.203922 0.274510 0.325490 1
```

---

## 4. Hal yang WAJIB diketahui saat integrasi

### 4.1 Warna panel tidak datang dari tema GTK

Panel memasang CSS inline pada `GTK_STYLE_PROVIDER_PRIORITY_APPLICATION`
(600), di atas tema (200). Karena itu `gtk.css` ORACLE **tidak** bisa
mewarnai latar panel. Warna **harus** lewat `background-style` +
`background-rgba`. Bukti: `panel/docs/AUDIT-PANEL.md` §3.1.

`border-color` juga dipaksa `transparent` secara inline. Border panel
datang dari style property `borders` (xfconf `border-width`), bukan CSS.

### 4.2 Tidak ada compositor

Desain memakai alpha 1.0 (opaque). Bila kelak compositor diaktifkan,
tampilan tidak berubah — alpha 1.0 tidak tembus pandang. Ini disengaja:
tidak ada ketergantungan pada compositor yang tidak dijalankan.

### 4.3 Ikon panel butuh tema ikon

`icon-size` hanya mengatur ukuran; ikonnya sendiri datang dari tema ikon
aktif. Tahap icon styling (Papirus) **belum** dikerjakan. Sebelum tahap itu,
panel akan memakai ikon tema bawaan.

Bila tema ikon diganti, cache ikon harus dibangun ulang (`gtk-update-icon-cache`)
— setelah paket terpasang, bukan sebelum.

### 4.4 Panjang dock dalam piksel

`panel-2` memakai `length-adjust=true` dan `length=520` (piksel tetap).
Menambah launcher akan memotong isi. Bila launcher bertambah, naikkan
`length` atau kembalikan ke persen (`length-adjust=false`, `length=30`).

### 4.5 Urutan pemasangan disarankan

1. Tema GTK ORACLE → `~/.themes/ORACLE` atau `/usr/share/themes/ORACLE`
2. Set `gtk-theme-name=ORACLE` di channel `xsettings`
3. Panel: `default.xml` (dokumen ini)
4. Tema ikon (tahap terpisah, belum ada)
5. Wallpaper Workspace (sudah ada)

Panel sebelum tema = panel memakai warna GTK default untuk tombol dan teks
di dalamnya, walau latar panel sudah benar.

---

## 5. Yang TIDAK diatur file ini

| Hal | Alasan |
|---|---|
| Tema ikon | tahap icon styling, belum dikerjakan |
| Wallpaper | sudah jadi aset terpisah, diatur `xfdesktop` |
| Font | channel `xsettings`, di luar panel |
| Tema GTK | `gtk/ORACLE`, sudah disetujui |
| Compositor | tidak dipakai |
| Whisker menu | tidak dipakai; `applicationsmenu` bawaan cukup |