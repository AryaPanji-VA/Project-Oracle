# ORACLE OS 0.1.0 — Runbook Demo

Panduan menjalankan ORACLE OS untuk demo. Semua perintah di sini sudah
diuji, bukan contoh teoretis.

---

## 1. Menjalankan dari ISO (cara tercepat untuk demo)

Demo langsung dari ISO tidak mengubah apa pun di komputer yang dipakai.

```bash
qemu-system-x86_64 \
  -enable-kvm -cpu host -m 4096 -smp 4 \
  -cdrom ~/VMs/oracle-debian13/phase5-out/ORACLE-OS-phase5-final.iso \
  -boot d \
  -netdev user,id=n0 -device virtio-net-pci,netdev=n0 \
  -display gtk
```

**Catatan penting:**

- `-enable-kvm` wajib. Tanpa itu boot bisa 10x lebih lambat dan demo
  terasa rusak.
- `-m 4096` minimal. Dengan 2 GB, Firefox berat dan panel bisa tersendat.
- Setelah menu GRUB muncul, tekan **Enter**. Menu tidak auto-boot.
- Login otomatis sebagai `user`; kalau diminta password, isinya `live`.

---

## 2. Urutan demo yang meyakinkan

Urutan ini disusun supaya hal yang paling mengesankan muncul lebih dulu,
dan setiap langkah punya bukti visual.

### 2.1 Identitas — 10 detik

Buka terminal (`Ctrl+Alt+T`), lalu:

```bash
oracle
cat /etc/oracle-release
```

Yang terlihat: CLI ORACLE menyebut dirinya sendiri, dan sistem
mengidentifikasi diri sebagai **ORACLE OS 0.1.0**, bukan Debian.

### 2.2 Desktop — 30 detik

Tunjukkan tanpa menjelaskan berlebihan:

- Panel atas dengan dock aplikasi
- Wallpaper ORACLE (krem, bukan hitam)
- Menu aplikasi berisi 46 entri — bukan kosong
- Notifikasi, jam, indikator jaringan, dan kontrol volume di panel

Klik indikator jaringan: NetworkManager menampilkan daftar jaringan.
Ini yang membedakan image "bisa boot" dengan image "bisa dipakai".

Klik ikon volume: slider muncul dan mengubah volume sungguhan. Panel yang
tidak punya kontrol volume adalah detail kecil yang paling sering membuat
demo terasa belum jadi.

### 2.3 Aplikasi nyata — 60 detik

1. **Firefox** — buka satu situs. Membuktikan jaringan + render berjalan.
2. **Thunar** — colok USB, muncul di sidebar. Ini memakai `gvfs`, yang
   biasanya lupa dipasang pada image live-build.
3. **Terminal** — jalankan `pactl info`, tunjukkan server audio hidup.

### 2.4 Profil ORACLE — 45 detik

```bash
oracle profile list
```

Menunjukkan profil keamanan tersedia (networking, web-security).
Jelaskan bahwa profil bersifat **opt-in**: image dasar sengaja bersih,
profil ditambahkan saat build.

### 2.5 Bukti kualitas — 30 detik

```bash
sudo -n true && echo "sudo siap"
ls /usr/share/applications/*.desktop | wc -l
```

Audiens teknis biasanya menghargai ini lebih dari animasi.

---

## 3. Yang TIDAK boleh diklaim saat demo

Batasan ini nyata dan sudah diverifikasi. Melebih-lebihkan akan
ketahuan dalam hitungan detik.

| Jangan klaim | Kenyataan |
|---|---|
| "Sistem sudah bisa diinstal ke disk" | Installer belum ada; ini live image |
| "Pengaturan tersimpan setelah reboot" | Live session tidak persisten |
| "Build-nya reproducible bit-for-bit" | Isi logis reproducible; checksum berubah karena repo Debian bergerak |
| "Sudah diuji di hardware asli" | Baru diuji di QEMU/KVM |
| "Aman untuk data sensitif" | Belum ada hardening, enkripsi, atau audit keamanan |

Kalau ditanya soal keamanan, jawaban jujurnya: **ini fondasi, bukan
produk jadi.** Yang sudah ada: identitas, desktop, aplikasi, jaringan,
dan alur build yang bisa diulang.

---

## 4. Kalau ada yang tidak jalan

| Gejala | Penyebab umum | Tindakan |
|---|---|---|
| Desktop hitam | Screenshot diambil sebelum autostart selesai | Tunggu 5 detik lagi |
| Tidak ada jaringan | QEMU tanpa `-netdev` | Tambahkan `-netdev user,id=n0 -device virtio-net-pci,netdev=n0` |
| Boot sangat lambat | `-enable-kvm` tidak aktif | Cek `/dev/kvm` dan grup `kvm` |
| Layar kecil / terpotong | Resolusi QEMU default | Tambahkan `-device virtio-vga -vga std` atau ubah ukuran window |
| Firefox tidak mau buka situs | DNS di QEMU user-mode | `ping 10.0.2.2`, lalu coba `ping 1.1.1.1`; kalau IP jalan tapi nama tidak, itu DNS |

---

## 5. Membangun ulang ISO

Di **dalam VM**, bukan di host — `build.sh` menolak bare metal.

```bash
~/oracle-recovery/boot-vm.sh
ssh -i ~/VMs/oracle-debian13/ssh/oracle-builder_ed25519 -p 2223 oraclebuild@127.0.0.1
cd ~/oracle-phase5
./tests/run_all.sh          # 9/9, 217 assertion
./scripts/build.sh          # ~35 menit
```

Ambil hasilnya:

```bash
scp -i ~/VMs/oracle-debian13/ssh/oracle-builder_ed25519 -P 2223 \
    oraclebuild@127.0.0.1:~/oracle-phase5/build/live-image-amd64.hybrid.iso \
    ~/VMs/oracle-debian13/phase5-out/ORACLE-OS-phase5-final.iso
```

Verifikasi otomatis (boot + 38 cek):

```bash
~/oracle-recovery/verify-iso.py \
    ~/VMs/oracle-debian13/phase5-out/ORACLE-OS-phase5-final.iso \
    /tmp/verify
```