# Phase 5 — Menuju ORACLE OS yang Demo-Usable

Dokumen ini mencatat apa yang **benar-benar diverifikasi**, bukan apa yang
diasumsikan. Semua angka berasal dari eksekusi nyata di VM
`oracle-debian13` dan boot-test QEMU.

- Commit dasar: **`0a639ae`** (Stage 3H COMPLETE)
- Target: OS dapat dipakai untuk demo, bukan hanya bisa boot.

---

## 1. Temuan awal (build reproduksi dari `0a639ae`)

Build ulang dari source tanpa perubahan menghasilkan ISO 976 MB, boot
sampai `graphical.target`, LightDM hidup, dan sesi XFCE jalan. Tetapi
probe otomatis menunjukkan **28/33 lulus, 5 gagal**.

Lima kegagalan itu, setelah diselidiki satu per satu:

| # | Gejala | Akar masalah | Status |
|---|--------|--------------|--------|
| 1 | `nmcli` tidak ada | `config/profiles.conf` kosong; profil bersifat opt-in | diperbaiki |
| 2 | Tidak ada peramban | `xfce4` + Recommends dimatikan; desktop list minim | diperbaiki |
| 3 | `pactl` tidak ada | `pipewire-pulse` menyediakan server, bukan biner `pactl` | diperbaiki |
| 4 | Tidak ada polkit agent | Debian 13 tak punya agent XFCE | diperbaiki |
| 5 | `ukui-polkit` ikut masuk | Recommends menarik agent desktop lain | diperbaiki |

> **Koreksi atas analisis awal saya.** Saya sempat menyimpulkan identitas
> ORACLE dan wallpaper "gagal". Itu **salah** — keduanya sudah benar sejak
> `0a639ae`. Penyebabnya bug di skrip probe saya sendiri (membaca data
> yang sudah dikonsumsi dan parsing rapuh terhadap escape serial). Wallpaper
> juga sempat tampak hitam karena screenshot diambil sebelum autostart
> selesai. Keduanya bukan bug produk.

---

## 2. Perubahan yang dilakukan

### 2.1 Aplikasi harian di `oracle-desktop.list.chroot`

`image/auto/config` memakai `--apt-options=--no-install-recommends`.
Konsekuensinya `xfce4` hanya memasang inti desktop: menu Applications
nyaris kosong dan dock punya ikon mati.

Ditambahkan: `firefox-esr`, `thunar`, `mousepad`, `ristretto`,
`xfce4-taskmanager`, `gnome-calculator`, `file-roller`, `gvfs`,
`gvfs-backends` (mount USB/network di Thunar), `xdg-utils`,
`xfce4-appfinder`.

### 2.2 Jaringan: NetworkManager

Sebelumnya live session hanya punya DHCP sekali jalan dari
`/etc/network/interfaces`. Itu cukup untuk boot, tapi tidak untuk demo:
tidak ada applet panel, tidak bisa ganti jaringan, tidak bisa lihat status.

`network-manager` + `network-manager-gnome` masuk daftar paket, dengan
`etc/NetworkManager/conf.d/10-oracle-managed.conf` yang menegaskan
`managed=true` agar antarmuka yang sudah dikonfigurasi `ifupdown` tetap
diambil alih NetworkManager.

### 2.3 Audio

`pipewire-pulse` hanya menyediakan server kompatibel, bukan biner `pactl`.
Tanpa `pulseaudio-utils`, plugin audio panel terpasang tapi tidak bisa
menampilkan atau mengubah volume — panel tampak mati.

### 2.4 Polkit

Debian 13 tidak lagi punya `xfce-polkit` maupun `policykit-1-gnome`, dan
`task-xfce-desktop` tidak menarik agent apa pun. Tanpa agent, dialog
otentikasi tidak pernah muncul.

`mate-polkit` dipakai: agent GTK3 yang mengikuti tema GTK aktif, jadi
dialog otentikasi tampil konsisten dengan tema ORACLE. Autostart bawaan
paket **tidak** dibatasi MATE (`NotShowIn=GNOME;KDE;`), sehingga agent
otomatis jalan di sesi XFCE.

> **Koreksi.** Saya sempat menambahkan file autostart sendiri, dengan
> asumsi `mate-polkit` hanya jalan di MATE. Asumsi itu salah: saat diuji,
> muncul **dua** proses agent sekaligus — berisiko memunculkan dialog
> otentikasi ganda. File itu dihapus; autostart bawaan paket sudah cukup.

### 2.5 Bug laten: komentar inline di package-list

`live-build` membaca package-list dengan `grep -v '^#'` — hanya membuang
baris yang **diawali** `#`. Komentar di ujung baris akan terbaca sebagai
bagian nama paket dan menggagalkan build.

Tidak ada yang salah di repo saat ini, tapi tidak ada yang mencegahnya.
Ditambahkan `tests/package_list_format_test.sh` yang menolak komentar
inline, nama paket tidak valid, dan duplikat. Tes ini langsung menangkap
`polkitd` ganda yang saya tulis sendiri.

### 2.6 `nikto` tidak ada di Debian 13

Profil `web-security` mencantumkan `nikto`, yang tidak tersedia di trixie.
Kalau profil itu dipakai, build akan gagal. Diganti `wapiti` + `whatweb`
+ `skipfish`, dengan catatan di file profil.

### 2.7 Ikon dock mati

`xfce4-web-browser.desktop` tidak ada di Debian, padahal panel dock
merujuknya. Ditambahkan entri desktop yang memanggil `firefox-esr`.

### 2.8 Kontrol volume tidak ada di panel

Panel atas punya `systray`, `tasklist`, dan `clock` — tapi **tidak** punya
plugin `pulseaudio`. Akibatnya suara berjalan tanpa ada cara mengubah
volume dari panel. Untuk demo, ini detail kecil yang paling sering
membuat sistem terasa belum selesai.

Diperbaiki di `tools/design/gen_panel.py` (generator), bukan di XML hasil
generate: plugin `pulseaudio` disisipkan sebelum `clock`, sehingga clock
bergeser ke `plugin-9`. XML image diregenerasi dari generator — kalau
diedit manual, perubahan akan hilang pada regenerasi berikutnya.

---

## 3. Status verifikasi

Diverifikasi lewat boot QEMU + probe serial otomatis
(`oracle-recovery/verify-iso.py`): **40/40 cek lulus** pada ISO final
`ORACLE-OS-phase5-demo.iso`.

| Kriteria | Status |
|---|---|
| Boot ke `graphical.target` | ✅ |
| Tidak ada systemd unit gagal | ✅ |
| Tidak ada kernel panic | ✅ |
| LightDM + autologin `user` | ✅ |
| Sesi XFCE (panel, xfwm4, session) | ✅ |
| Identitas ORACLE (`/etc/oracle-release`, `os-release`) | ✅ |
| Tema, ikon, kursor, wallpaper | ✅ tampil, bukan hitam |
| CLI `oracle` jalan | ✅ |
| NetworkManager aktif + kelola antarmuka | ✅ `ens3:connected` |
| Ikon jaringan di panel (systray) | ✅ |
| Kontrol volume di panel | ✅ plugin `pulseaudio` |
| Peramban (Firefox ESR) | ✅ |
| File manager + `gvfs` (mount USB) | ✅ |
| Audio (`pactl`, `pavucontrol`) | ✅ |
| Agent polkit (dialog otentikasi) | ✅ tepat 1 proses |
| Menu aplikasi terisi | ✅ 46 entri |
| Jumlah paket | 739 |

Bukti visual: `desktop.png` dari boot-test menunjukkan panel atas
(Applications, ikon jaringan, ikon volume, jam), dock bawah, wallpaper
krem, dan ikon desktop — tanpa dialog error dan tanpa ikon rusak.

---

## 4. Reproducibility

Build dari source yang sama **tidak menghasilkan checksum identik**.
Ini bukan cacat, tetapi harus dicatat supaya tidak jadi kejutan saat
release.

Penyebabnya: repo Debian bergerak. Build `0a639ae` pada November 2026
menarik versi paket yang berbeda dari build sebelumnya — termasuk
`linux-image-6.12.115+deb13.1-amd64`.

Empat build dijalankan berurutan untuk sampai ke hasil akhir:

| Build | Perubahan | ISO | Hasil probe |
|---|---|---|---|
| 1 | tanpa perubahan (reproduksi `0a639ae`) | 976 MB | 28/33 |
| 2 | app harian, NM, audio, polkit | 1.2 GB | — (probe masih bug) |
| 3 | perbaikan autostart polkit | 1.2 GB | 37/38 |
| final | plugin audio di panel | 1.2 GB | **40/40** |

Checksum akhir:

```
d151b694efd594c6e851d302d4cb9bb89fbcba78d70d5fbf0ca81088a7cb80f2  ORACLE-OS-phase5-demo.iso
1225752576 bytes
```

Yang bisa dijamin reproducibly:

1. **Isi logis** — daftar paket dan konfigurasi berasal dari repo, bukan
   dari jaringan.
2. **Bootability** — diverifikasi dengan boot-test, bukan diasumsikan.
3. **Checksum terdokumentasi per build** — dicatat di `build/SHA256SUMS`.

Untuk reproducibility bit-untuk-bit diperlukan snapshot repo Debian
(lihat §6).

---

## 5. Cara memverifikasi ulang

```bash
# 1. Build di VM (BUKAN di host — build.sh menolak bare metal)
~/oracle-recovery/boot-vm.sh
ssh -i ~/VMs/oracle-debian13/ssh/oracle-builder_ed25519 -p 2223 oraclebuild@127.0.0.1
cd ~/oracle-phase5 && ./scripts/build.sh

# 2. Ambil ISO
scp -i ~/VMs/oracle-debian13/ssh/oracle-builder_ed25519 -P 2223 \
    oraclebuild@127.0.0.1:~/oracle-phase5/build/live-image-amd64.hybrid.iso \
    ~/VMs/oracle-debian13/phase5-out/

# 3. Uji boot + probe otomatis
~/oracle-recovery/verify-iso.py ~/VMs/oracle-debian13/phase5-out/*.iso /tmp/verify
```

---

## 6. Yang belum dikerjakan

Ini batas nyata Phase 5. Semuanya sudah diketahui, tidak ada yang tersembunyi.

1. **Installer ke disk belum ada.** ORACLE OS saat ini live image: boot
   dari ISO, jalan penuh, tapi tidak bisa dipasang permanen. Untuk demo
   ini cukup; untuk "OS usable" sehari-hari, ini blocker berikutnya.
2. **Tidak ada persistensi.** Perubahan hilang saat reboot.
3. **Belum diuji di hardware asli.** Semua verifikasi di QEMU/KVM.
4. **Snapshot repo Debian** untuk reproducibility bit-untuk-bit belum ada.
5. **`profiles.conf` masih kosong secara sengaja.** NetworkManager masuk
   lewat desktop list, bukan profil. Keputusan ini perlu ditegaskan di
   `docs/design/DECISION-HISTORY.md`.
6. **Belum ada hardening.** Tidak ada enkripsi disk, firewall, atau audit
   keamanan. Image ini fondasi, bukan produk jadi.
