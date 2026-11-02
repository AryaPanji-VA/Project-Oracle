# ORACLE-OS — Integration Readiness

Stage 2H. Dokumen ini **tidak** melakukan integrasi. Ini peta untuk Stage 3.

Semua path target mengikuti struktur repo `~/Projects/Oracle-OS` yang
**sudah ada** (dibaca, tidak diubah).

---

## 0. Mekanisme live-build yang terverifikasi

Dari `scripts/build.sh` dan `image/auto/config`:

| Mekanisme | Path | Bukti |
|---|---|---|
| Konfigurasi `lb config` | `image/auto/config` | satu-satunya pemilik flag |
| File masuk chroot | `image/config/includes.chroot/` | `build.sh:215` `cp -a` |
| Package list | `image/config/package-lists/*.list.chroot` | `build.sh:221` |
| Hook chroot | `image/config/hooks/live/*.hook.chroot` | `build.sh:241` |
| Identitas | `config/oracle.conf` → `/etc/oracle/oracle.conf` | `build.sh:231` |

**Penting:** `--apt-recommends false` aktif (`image/auto/config`). Setiap
dependency opsional harus ditulis eksplisit di package list.

---

## 1. Asset integration map

| Design asset | Target path di OS repo | Fungsi | Dependency |
|---|---|---|---|
| `svg/dial-master.svg`, `wordmark.svg`, `lockup-*.svg` | `image/config/includes.chroot/usr/share/oracle/branding/` | identitas, dipakai greeter/about | — |
| `wallpaper/png/workspace-1920x1200.png` | `.../usr/share/backgrounds/oracle/workspace-1920x1200.png` | wallpaper default | `xfdesktop4` |
| `wallpaper/png/workspace-1280x800.png` | `.../usr/share/backgrounds/oracle/workspace-1280x800.png` | wallpaper resolusi kecil | `xfdesktop4` |
| `wallpaper/png/minimal-*.png` | `.../usr/share/backgrounds/oracle/minimal-*.png` | varian tenang | `xfdesktop4` |
| `gtk/ORACLE/` (seluruh) | `.../usr/share/themes/ORACLE/` | tema GTK3 | `gtk2-engines-murrine` (GTK2 apps) |
| `gtk/ORACLE/COPYING` | `.../usr/share/doc/oracle-theme/COPYING` | kewajiban GPL-3 | — |
| `gtk/ORACLE/NOTICE.md` | `.../usr/share/doc/oracle-theme/NOTICE.md` | atribusi Arc | — |
| `panel/cfg/xfce4-panel.xml` | `.../etc/xdg/xfce4/panel/default.xml` | layout 2 panel | `xfce4-panel` |
| `terminal/cfg/oracle.theme` | `.../usr/share/xfce4/terminal/colorschemes/oracle.theme` | palette ANSI | `xfce4-terminal` |
| `terminal/cfg/terminalrc.fragment` | `.../etc/xdg/xfce4/terminal/terminalrc` (key saja) | font, cursor | `xfce4-terminal` |
| `papirus/theme/ORACLE-Papirus/` | `.../usr/share/icons/ORACLE-Papirus/` | ikon | `papirus-icon-theme`, `librsvg2-common` |
| `papirus/docs/NOTICE.md` | `.../usr/share/doc/oracle-icons/NOTICE.md` | atribusi Papirus | — |
| `greeter/cfg/lightdm-gtk-greeter.conf` | `.../etc/lightdm/lightdm-gtk-greeter.conf` | konfigurasi greeter | `lightdm-gtk-greeter` |
| `greeter/cfg/oracle-greeter.css` | digabung ke `gtk/ORACLE/gtk-3.0/gtk.css` | styling greeter | — |
| `docs/MASTER-DESIGN.md` | `docs/DESIGN.md` (repo) | rujukan desain | — |

### 1.1 Catatan path

- `includes.chroot/` **adalah** root filesystem image. Path di dalamnya
  menjadi path absolut di image.
- Tema GTK **wajib** punya `gtk-3.0/` di dalamnya, kalau tidak XFCE 4.20
  mengabaikannya.
- `oracle-greeter.css` **tidak** disalin terpisah: ia di-`@import` dari
  `gtk.css` tema ORACLE, karena greeter memakai `theme-name=ORACLE`.

---

## 2. Debian package dependency map

Semua versi dari `Packages.gz` Debian 13 Trixie (main), diverifikasi.

### 2.1 Sudah ada di package list

| Paket | Versi | Section | Fungsi | Wajib |
|---|---|---|---|---|
| `xfce4` | 4.20.1 | xfce | metapackage desktop | ya |
| `xfce4-terminal` | 1.1.4-1 | xfce | terminal | ya |
| `lightdm` | 1.32.0-6+b2 | x11 | display manager | ya |
| `lightdm-gtk-greeter` | 2.0.9-1 | x11 | greeter | ya |
| `xserver-xorg-core` | 2:21.1.16-1.3+deb13u3 | x11 | X server | ya |
| `xserver-xorg-input-all` | 1:7.7+24+deb13u1 | x11 | input driver | ya |
| `xserver-xorg-video-all` | 1:7.7+24+deb13u1 | x11 | video driver | ya |
| `dbus-x11` | 1.16.2-2 | x11 | session bus | ya |
| `polkitd` | 126-2 | admin | policy | ya |
| `pkexec` | 126-2 | admin | privilege | ya |

### 2.2 PERLU DITAMBAH (belum ada di package list)

| Paket | Versi | Section | Fungsi | Wajib | Alasan |
|---|---|---|---|---|---|
| `arc-theme` | 20221218-1 | misc | **basis** tema ORACLE | **ya** | `gtk.css` adalah turunan Arc; tanpa ini tidak ada fallback GTK2 |
| `papirus-icon-theme` | 20250501-1 | x11 | ikon | **ya** | `ORACLE-Papirus` Inherits=Papirus |
| `librsvg2-common` | 2.60.0+dfsg-1 | libs | render SVG | **ya** | hanya Recommends Papirus; `--apt-recommends false` mematikan |
| `hicolor-icon-theme` | 0.18-2 | misc | fallback ikon | **ya** | Depends Papirus |
| `fonts-inter` | 4.1+ds-1 | fonts | UI font | **ya** | `font-name=Inter 11` |
| `fonts-jetbrains-mono` | 2.304+ds-5 | fonts | terminal font | **ya** | `FontName=JetBrains Mono 11` |
| `dmz-cursor-theme` | 0.4.5.2 | gnome | kursor | **ya** | `cursor-theme-name=dmz-cursor-theme` |
| `gtk2-engines-murrine` | 0.98.2-4+b1 | x11 | GTK2 engine | opsional | hanya bila ada app GTK2 |

### 2.3 Catatan dependency

- **`librsvg2-common` adalah temuan penting.** Papirus hanya
  *Recommends*-nya. Dengan `--apt-recommends false`, tanpa paket ini ikon
  SVG **tidak akan tampil** — panel dan file manager akan kosong.
- `arc-theme` wajib karena `gtk.css` ORACLE adalah turunan Arc. Tanpa
  paket ini, aplikasi GTK2 tidak punya engine yang cocok.
- `fonts-inter` dan `fonts-jetbrains-mono` wajib: tanpa keduanya, XFCE dan
  terminal jatuh ke font default dan metrik berubah.

---

## 3. Configuration integration map

### 3.1 GTK theme selection

**Target:** `.../etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xsettings.xml`

```xml
<channel name="xsettings" version="1.0">
  <property name="Net" type="empty">
    <property name="ThemeName" type="string" value="ORACLE"/>
    <property name="IconThemeName" type="string" value="ORACLE-Papirus"/>
  </property>
  <property name="Gtk" type="empty">
    <property name="CursorThemeName" type="string" value="dmz-cursor-theme"/>
    <property name="CursorThemeSize" type="int" value="24"/>
    <property name="FontName" type="string" value="Inter 11"/>
  </property>
</channel>
```

**Tambahan wajib:** `.../etc/gtk-3.0/settings.ini` — channel xsettings XFCE
tidak mencakup semua aplikasi GTK3.

```ini
[Settings]
gtk-theme-name=ORACLE
gtk-icon-theme-name=ORACLE-Papirus
gtk-font-name=Inter 11
gtk-cursor-theme-name=dmz-cursor-theme
```

### 3.2 XFCE xfconf defaults

| Channel | File | Isi |
|---|---|---|
| `xfce4-panel` | `.../etc/xdg/xfce4/panel/default.xml` | 2 panel (dari `panel/cfg/`) |
| `xsettings` | `.../etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xsettings.xml` | tema, ikon, font |
| `xfwm4` | `.../etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfwm4.xml` | WM (belum dibuat) |
| `xfce4-desktop` | `.../etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml` | wallpaper |
| `xfce4-terminal` | `.../etc/xdg/xfce4/terminal/terminalrc` | font, cursor |

### 3.3 Wallpaper

**Target:** `.../etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml`

```xml
<property name="backdrop" type="empty">
  <property name="screen0" type="empty">
    <property name="monitor0" type="empty">
      <property name="workspace0" type="empty">
        <property name="image-path" type="string"
                  value="/usr/share/backgrounds/oracle/workspace-1920x1200.png"/>
        <property name="image-style" type="int" value="5"/>
      </property>
    </property>
  </property>
</property>
```

`image-style=5` = zoomed. Wallpaper 1920×1200 di-scale ke resolusi layar.

### 3.4 LightDM GTK Greeter

**Target:** `.../etc/lightdm/lightdm-gtk-greeter.conf` (sudah ada, isinya
`[greeter]` kosong — akan diganti).

**Precedence:** `/etc/lightdm/lightdm-gtk-greeter.conf` (lapisan 1) menang
atas `/usr/share/lightdm/lightdm-gtk-greeter.conf.d/01_debian.conf`
(lapisan 3). Jadi `01_debian.conf` **tidak perlu dihapus**.

### 3.5 Interaksi dengan live user creation — RISIKO UTAMA

Ini bagian yang paling mudah salah. Fakta:

1. `live-config` + `user-setup` membuat user `user` **saat boot**, bukan
   saat build.
2. `/etc/skel` hanya menyemai home **baru**. File di `/etc/skel` bisa
   tertimpa oleh apa yang ditulis sesi setelahnya.
3. `/etc/xdg` dibaca **semua** akun dan merupakan lapisan default resmi.

**Keputusan: semua default di `/etc/xdg`, BUKAN `/etc/skel`.**

| Konfigurasi | Lokasi | Alasan |
|---|---|---|
| Panel | `/etc/xdg/xfce4/panel/default.xml` | dibaca sebelum user punya config |
| xsettings | `/etc/xdg/xfce4/xfconf/xfce-perchannel-xml/` | idem |
| Terminal | `/etc/xdg/xfce4/terminal/terminalrc` | idem |
| GTK3 apps | `/etc/gtk-3.0/settings.ini` | tidak dicakup xsettings |
| Greeter | `/etc/lightdm/` | dibaca sebelum user login |

**Yang TIDAK dijamin:** bila user sudah punya
`~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml`, file itu
**menang** atas `/etc/xdg`. Di live image hal ini tidak terjadi karena home
dibuat baru setiap boot.

### 3.6 Autologin

`.../etc/lightdm/lightdm.conf.d/50-oracle-live.conf` sudah berisi:

```ini
[Seat:*]
greeter-session=lightdm-gtk-greeter
user-session=xfce
autologin-user=user
autologin-user-timeout=0
```

**Konsekuensi:** greeter **mungkin tidak pernah tampil** pada boot normal.
Styling greeter tetap dipasang, tetapi hanya terlihat saat logout manual
atau bila autologin dimatikan.

### 3.7 live-config dan live-boot

| Aspek | Perilaku |
|---|---|
| `live-config` | menjalankan hook saat boot; **tidak** menyentuh `/etc/xdg` |
| `live-boot` | menyiapkan overlay; perubahan user tidak persisten |
| `user-setup` | membuat user `user` + autologin |
| `/etc/skel` | disalin ke home baru; **hindari** menaruh config di sini |

---

## 4. Build integration plan

| # | Fase | Aksi | Rollback |
|---|---|---|---|
| 1 | Baseline | `git status`, catat HEAD, hash ISO lama | — |
| 2 | Paket | tambah 7 paket ke `oracle-desktop.list.chroot` | `git checkout` file list |
| 3 | Aset | salin ke `includes.chroot/` | hapus direktori yang ditambah |
| 4 | Konfigurasi | tulis xfconf XML, settings.ini, greeter conf | `git checkout` |
| 5 | Build | `scripts/build.sh` di VM disposable | buang `build/` |
| 6 | Boot | QEMU, cek sampai desktop | — |
| 7 | Login | cek autologin; logout → greeter | — |
| 8 | XFCE visual | panel atas/bawah, wallpaper, tema | — |
| 9 | Terminal | `xfce4-terminal --color-table` | — |
| 10 | Panel & ikon | ikon tampil, tidak kosong | — |
| 11 | Greeter | logout, cek tampilan login | — |
| 12 | Regresi | `tests/run_all.sh` | — |
| 13 | Checksum | `sha256sum` ISO final | simpan ISO lama |

**Titik rollback kritis:** fase 2–4 semuanya di Git, jadi `git checkout`
cukup. Fase 5 ke atas butuh VM disposable.

---

## 5. Test matrix

| # | Uji | Cara | Lulus bila |
|---|---|---|---|
| 1 | ISO boot | QEMU `-vga std` | sampai desktop tanpa error |
| 2 | Live user | `id`, `whoami` | user `user` ada, home dibuat |
| 3 | Autologin | boot tanpa interaksi | langsung ke XFCE |
| 4 | Greeter manual | logout dari sesi | greeter ORACLE tampil |
| 5 | Wallpaper 1920×1200 | QEMU resolusi itu | wallpaper penuh, tidak pecah |
| 6 | Wallpaper 1280×800 | QEMU resolusi itu | idem |
| 7 | GTK widgets | buka Thunar, Settings | warna ORACLE, teks terbaca |
| 8 | Panel atas | lihat layar | Steel, 32 px, ikon tampil |
| 9 | Panel bawah | lihat layar | Porcelain, border, 48 px |
| 10 | Ikon | buka file manager | ikon Papirus, **bukan** kotak kosong |
| 11 | Terminal ANSI | `xfce4-terminal --color-table` | 16 warna ORACLE |
| 12 | Font | `fc-list \| grep -i inter` | Inter + JetBrains Mono ada |
| 13 | Logout/reboot | logout lalu login | tidak ada error |
| 14 | Display scaling | ganti resolusi | panel & wallpaper menyesuaikan |
| 15 | Missing asset | `find /usr/share/themes/ORACLE -name '*.png' \| wc -l` | 124 |
| 16 | Dependency | `dpkg -l \| grep -E 'arc-theme\|papirus\|librsvg'` | semua terpasang |

### 5.1 Uji yang paling mungkin gagal

| Risiko | Gejala | Penyebab |
|---|---|---|
| Ikon kosong | panel & file manager tanpa ikon | `librsvg2-common` tidak terpasang |
| Font salah | teks lebar/jelek | `fonts-inter` tidak terpasang |
| Panel default | panel 1 tunggal, bukan 2 | `default.xml` tidak terbaca |
| Greeter generik | login tampak Adwaita | `theme-name` tidak berlaku |
| Wallpaper hitam | latar polos | `xfce4-desktop.xml` salah path |

---

## 6. Yang TIDAK dilakukan dokumen ini

- Tidak menyalin aset ke repo.
- Tidak mengubah package list.
- Tidak menulis konfigurasi ke sistem.
- Tidak build ISO.
- Tidak commit/push.

Semua di atas adalah Stage 3, setelah persetujuan.