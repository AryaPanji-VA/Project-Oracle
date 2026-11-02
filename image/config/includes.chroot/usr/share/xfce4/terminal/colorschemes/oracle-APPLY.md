# ORACLE-OS — Cara Memasang Tema Terminal

**Status: BELUM DITERAPKAN.** Dokumen ini instruksi untuk nanti.
Batasan Stage 2E melarang integrasi ke terminal host.

Target: `xfce4-terminal 1.1.4-1`, VTE 0.61.91+, X11.

---

## 1. Pasang colorscheme

Colorscheme adalah file tunggal — aman, tidak menimpa apa pun.

### Per user

```sh
mkdir -p ~/.local/share/xfce4/terminal/colorschemes
install -m644 terminal/cfg/oracle.theme \
  ~/.local/share/xfce4/terminal/colorschemes/oracle.theme
```

### Default sistem (untuk live image)

```sh
install -Dm644 terminal/cfg/oracle.theme \
  /usr/share/xfce4/terminal/colorschemes/oracle.theme
```

Lalu pilih **ORACLE** di *Edit → Preferences → Colors → Presets*.
Atau set langsung agar panel memakainya:

```sh
xfconf-query -c xfce4-terminal -p /color-preset -n -t string -s ORACLE
```

Cek hasil:

```sh
xfce4-terminal --color-table      # jendela 16 warna dari scheme aktif
```

---

## 2. Pasang key non-warna (font, cursor, scrollbar)

`cfg/terminalrc.fragment` **bukan** file utuh. Ia hanya berisi key yang kita
tetapkan. **Jangan** menyalin seluruhnya menimpa `terminalrc` — file itu
berisi key lain milik user.

Cara aman, per key:

```sh
C=xfce4-terminal
xfconf-query -c $C -p /font-name        -n -t string -s "JetBrains Mono 11"
xfconf-query -c $C -p /font-use-system  -n -t bool   -s false
xfconf-query -c $C -p /misc-cursor-shape -n -t string -s TERMINAL_CURSOR_SHAPE_BLOCK
xfconf-query -c $C -p /misc-cursor-blinks -n -t bool  -s false
xfconf-query -c $C -p /scrolling-bar     -n -t string -s TERMINAL_SCROLLBAR_NONE
xfconf-query -c $C -p /background-mode   -n -t string -s TERMINAL_BACKGROUND_SOLID
```

Catatan: nama properti di xfconf memakai huruf kecil dan tanda hubung
(`/font-name`), sementara di `terminalrc` memakai CamelCase (`FontName=`).
Keduanya merujuk key yang sama.

Backup dulu:

```sh
cp -n ~/.config/xfce4/terminal/terminalrc \
      ~/.config/xfce4/terminal/terminalrc.bak
```

---

## 3. Verifikasi

```sh
xfconf-query -c xfce4-terminal -p /color-preset
xfconf-query -c xfce4-terminal -p /color-foreground
xfconf-query -c xfce4-terminal -p /color-background
xfconf-query -c xfce4-terminal -p /color-palette | head -c 120
```

`--color-table` menampilkan 16 warna + teks contoh; itulah cara tercepat
memastikan palette terbaca dan tidak ada slot yang menyatu dengan latar.

---

## 4. Hal yang perlu diketahui saat integrasi

### 4.1 Font harus tersedia di image

`JetBrains Mono 11` hanya berlaku bila font-nya terpasang. Nama paket
kandidat di Debian: `fonts-jetbrains-mono`. Bila tidak ada, VTE akan
jatuh ke font sistem dan lebar kolom berubah.

Cek di image target:

```sh
fc-list | grep -i jetbrains
```

### 4.2 Inter untuk aplikasi GTK, bukan terminal

Inter dipakai UI aplikasi (sudah ditetapkan di tahap GTK), bukan di dalam
terminal. Terminal memakai JetBrains Mono. Keduanya terpisah.

### 4.3 Keterkaitan dengan GTK theme

`ColorUseTheme=FALSE` membuat terminal **tidak** mengambil warna dari
`gtk-theme-name`. Ini disengaja: tema ORACLE tidak boleh menimpa palette
ANSI, dan palette tidak bergantung pada tema.

Border jendela tetap dari GTK theme (`#B9C1C2`), jadi jendela terminal
tetap terbaca di atas wallpaper Ivory.

### 4.4 Urutan pemasangan

1. GTK theme ORACLE
2. Tema terminal (dokumen ini)
3. Panel
4. Tema ikon (belum ada)

Bila tema terminal dipasang sebelum font ada, font akan jatuh ke default
sampai font terpasang dan terminal dijalankan ulang.

---

## 5. Yang TIDAK diatur file ini

| Hal | Alasan |
|---|---|
| Shell prompt (PS1) | milik shell, bukan terminal |
| Syntax highlight `ls` | milik `dircolors`, di luar cakupan |
| Tab title | dinamis |
| Scrollback size | kebijakan user |
| Keybinding | kebijakan user |