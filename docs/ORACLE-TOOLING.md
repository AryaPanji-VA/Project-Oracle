# ORACLE Tooling — `status`, `doctor`, `lab`

Dokumen ini menjelaskan tiga perintah ORACLE yang memberi sistem **perilaku**,
bukan sekadar tampilan. Sebelum ini, dari 565 berkas di `includes.chroot` hanya
dua yang executable (`oracle` dan `oracle-wallpaper`); sisanya aset visual.

Semua kode ditulis **POSIX sh** (`#!/bin/sh`, `set -eu`) dan dijalankan dengan
`dash` di Debian. Tidak ada bashism.

---

## 1. `oracle status` — dashboard sistem

Menampilkan keadaan mesin dalam satu layar: kernel, uptime, beban, memori,
disk, antarmuka jaringan, unit systemd yang gagal, dan postur keamanan
(firewall, SSH, akun tanpa password).

```console
$ oracle status
```

Tidak butuh root. Perintah ini **tidak mengubah apa pun** — hanya membaca.

Yang membuatnya jujur: kalau NetworkManager tidak ada, ia melaporkan
"NetworkManager tidak ada", bukan menampilkan bagian kosong atau error.
Ini penting karena ORACLE dibangun di atas Debian minimal; banyak hal yang
dianggap "pasti ada" di distro lain tidak ada di sini.

---

## 2. `oracle doctor` — pemeriksaan mandiri

Memeriksa apakah sistem memenuhi yang diklaimnya, lalu memberi saran
perbaikan konkret.

```console
$ oracle doctor
```

Yang diperiksa:

| Bagian | Isi |
| --- | --- |
| Identitas | `/etc/oracle-release`, `/etc/os-release`, hostname |
| Integritas dasar | root filesystem read-only?, ruang disk |
| Jaringan | antarmuka aktif, DNS, konektivitas |
| Keamanan | firewall, SSH root login, akun tanpa password |
| Tooling | `iproute2`, alat lab |

**Pelajaran penting:** deteksi root filesystem read-only TIDAK boleh memakai
`[ -w / ]`. Untuk pengguna biasa, tes itu selalu false meski filesystem
writable, sehingga `doctor` melaporkan masalah yang tidak ada. Yang benar
adalah memeriksa **opsi mount** di `/proc/mounts`.

Pelajaran kedua: `doctor` memeriksa **keberadaan alat lab** dan memberi tahu
cara memasangnya (`sudo oracle profile install networking`) alih-alih gagal
misterius saat `lab` dijalankan.

---

## 3. `oracle lab` — security lab terisolasi

Membuat dua network namespace yang terhubung tanpa jalan keluar:

```console
$ sudo oracle lab start      # siapkan lab
$ sudo oracle lab status     # lihat keadaan + verifikasi isolasi
$ sudo oracle lab shell      # masuk sebagai attacker
$ sudo oracle lab target     # masuk sebagai target (terminal lain)
$ sudo oracle lab stop       # bersihkan
```

Topologi:

```
  attacker 10.66.0.1  ──veth──  target 10.66.0.2
     (oracle-lab-atk)              (oracle-lab-tgt)
            │                             │
            └──────── tidak ada rute ─────┘
```

Tidak ada default route, tidak ada NAT. Verifikasi dilakukan **secara
struktural** (tabel rute kosong), bukan hanya dengan mencoba koneksi.

### Kenapa butuh root

Lab memakai network namespace **root**, bukan `unshare -rn` (rootless).
Alasannya ditemukan lewat pengujian: rootless membocorkan DNS melalui socket
Unix `/run/systemd/resolve/io.systemd.Resolve` yang mode-nya `srw-rw-rw-`.
Proses rootless tidak bisa me-mount `/run` atau menulis `/etc/resolv.conf`,
jadi tidak ada cara menutup jalur itu. Dengan netns root, jalur DNS ditutup
dengan mount di dalam namespace pribadi panggilan itu.

### Jebakan yang sudah dilewati

**`unshare --net=FILE` TIDAK bisa dipakai untuk masuk namespace.** Di
util-linux, sintaks itu berarti "buat namespace baru, lalu bind-mount ke
berkas ini" — bukan "masuk ke namespace yang sudah ada". Akibatnya lab
hancur: namespace hanya berisi `lo` dalam keadaan DOWN dan koneksi ke target
gagal dengan "Network is unreachable". Cara yang benar adalah
**`ip netns exec` + mount penutup DNS dalam SATU invocation**, karena
`ip netns exec` membuat mount namespace baru setiap kali dipanggil.

**`/dev/tcp` adalah bashism.** Versi awal probe memakai `exec 3<>/dev/tcp/...`
di bawah `#!/bin/sh` (= `dash`), sehingga SEMUA hasil "TCP terblokir" itu
palsu — perintahnya memang tidak pernah jalan. Probe sekarang memakai
`python3`.

**Listener harus `setsid`.** Tanpa itu, listener mati saat shell induknya
keluar, dan lab tampak "tidak menerima koneksi" padahal topologinya benar.

**Namespace mati meninggalkan berkas yatim.** `ip netns del` tidak menghapus
`/var/run/netns/<nama>` bila namespace sudah mati; `ip netns add` berikutnya
gagal dengan "File exists". Cleanup menghapus veth lebih dulu, lalu melepas
mount berulang (mount bisa bertumpuk) sebelum menghapus berkas.

**`ip netns exec true` sukses di namespace kosong.** Jadi keberhasilan
perintah itu bukan penanda namespace sehat; `is_running` harus memeriksa
antarmuka.

### Alat

Lab mengandalkan profil `networking` (`nmap`, `netcat-openbsd`, `tcpdump`,
`curl`). Profil ini **opt-in** dan tidak ikut image default, sesuai keputusan
v0.1 "image tetap ringan". Karena itu `lab start` dan `lab status` melaporkan
alat yang belum ada beserta perintah pemasangannya — bukan diam.

---

## Struktur kode

```
usr/local/bin/oracle              # CLI utama: dispatch ke modul
usr/local/lib/oracle/oracle-status
usr/local/lib/oracle/oracle-doctor
usr/local/lib/oracle/oracle-lab
```

Modul dipanggil dengan `exec`, bukan di-`source`, supaya tiap modul punya
`set -eu` sendiri dan bisa dikembangkan terpisah. Resolusi path modul relatif
terhadap lokasi CLI, sehingga `ORACLE_LIB` bisa di-override saat pengujian.

## Pengujian

`tests/oracle_cli_modules_test.sh` — 29 pemeriksaan statis: POSIX-legal,
tidak ada bashism, pola berbahaya tidak kembali (mis. `unshare --net=FILE`,
`[ -w / ]`), dispatch terdaftar, dan `run_all.sh` memuat tes ini.

Tes sengaja memindai **kode saja**, bukan komentar. Versi pertama memindai
seluruh berkas dan menandai dokumentasi bug sebagai bug — false positive yang
membuat orang mematikan tes. Komentar dibuang lebih dulu; pemeriksaan literal
`[[` memakai `grep -F` karena di ERE `[[` adalah awal bracket expression,
bukan teks.

Tes itu juga dibuktikan **bisa gagal**: bug sengaja disuntikkan
(`unshare --net=` dan `[ -w / ]` dikembalikan), tes menangkap keduanya, lalu
kode dipulihkan. Tes yang tidak pernah merah tidak membuktikan apa pun.

`tests/run_all.sh` — **10/10 suite, 246 assertion**.

### Verifikasi di ISO yang hidup

`verify-tooling.py` mem-boot ISO, login sebagai live user, lalu menjalankan
ketiga perintah di sistem ORACLE sungguhan (dash, filesystem read-only,
paket yang benar-benar terpasang). Hasil: **22/22**.

Yang dibuktikan: `oracle status` 852 byte output nyata, `oracle doctor`
1.874 byte dengan kesimpulan, `oracle lab start` membuat namespace
`10.66.0.1`/`10.66.0.2`, isolasi terverifikasi, `lab stop` bersih tanpa
namespace tersisa, dan 0 systemd unit gagal.

Dua bug ditemukan justru oleh verifikasi ini, bukan oleh tes statis:
`-monitor none` membuat `sendkey ret` mustahil sehingga boot berhenti di menu
GRUB, dan escape bracketed-paste (`ESC[?2004l`) menempel pada output sehingga
`"0"` terbaca sebagai `"\x1b[?2004l0"`.