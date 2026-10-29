# ORACLE OS — Status

> Living document. Perbarui setiap sesi kerja.
> Terakhir diperbarui: 2026-10-29 (remediasi review final: alur `noauto`,
> pemulihan package-lists, guard config, runner tes terpadu)

## Kondisi repo

| Item | Kondisi |
|---|---|
| Branch | `main` |
| Working tree | bersih setelah commit terakhir |
| Podman | **belum terpasang** di host |
| QEMU | **belum terpasang** di host |
| Disk kosong | 135 GB |
| ISO terbangun | **belum ada — belum pernah sekali pun** |

## Temuan audit (Prioritas A)

### B-1 — BLOCKER (sudah diperbaiki): hook gagal di dalam chroot

Hook `0100-oracle-identity` membaca `${ORACLE_ROOT}/config/oracle.conf`.
Hook berjalan di dalam chroot image, tempat `ORACLE_ROOT` tidak ada. Dengan
`set -eu`, build berhenti dengan `ORACLE_ROOT: unbound variable`.

Dibuktikan: `env -u ORACLE_ROOT sh hook` → exit 1.

**Perbaikan:** `scripts/build.sh` menyalin `config/oracle.conf` ke
`build/config/includes.chroot/etc/oracle/oracle.conf`. Hook membaca path itu
dan tidak lagi bergantung pada variabel host.

### B-2 — (sudah diperbaiki) `--privileged` + `--userns=keep-id` saling mengganggu

Kombinasi ini membuat `mount` gagal di container rootless; podman melaporkan
EUID 1000 (podman issue #6735). `lb build` memakai mount loop/bind, jadi
`--userns=keep-id` dihapus.

### B-3 — (sudah diperbaiki) `--privileged` rootless tidak cukup

`lb build` butuh `CAP_SYS_ADMIN`. Di podman rootless, `--privileged` hanya
memberi `SYS_ADMIN` ke UID 0 di dalam container (podman issue #13449), dan
pemetaan UID rootless tetap menghalangi bind mount.

**Perbaikan:** build lewat podman **rootful** (`sudo podman`) dengan
`--userns=host`. Konsekuensi: isi `build/` milik root, jadi pembersihan
workspace juga memakai `sudo`.

### B-4 — (sudah diperbaiki) hitungan paket profile kurang satu

`wc -l` melaporkan 9 untuk file berisi 10 paket bila file tidak diakhiri
newline. Diganti `grep -c .`.

## Yang sudah jadi

| Komponen | Status | Bukti |
|---|---|---|
| Identitas di image (hostname, os-release, oracle-release) | jalan | 2x run hook, entri `127.0.1.1` tidak duplikat |
| CLI `oracle` — identity/version/profile list/check/install | jalan | `tests/cli_test.sh` 17/17 lulus |
| Validasi input CLI (anti command injection) | jalan | 6 nama berbahaya ditolak |
| Profile networking (10 paket) & web-security (5 paket) | terdefinisi | satu sumber, dipakai build + runtime |
| Generator package-list profile (build-time) | jalan | profile kosong → tanpa file; valid → 15 paket, duplikat dibuang; hilang/berbahaya → exit 1 |
| Staging build (`image/` → `build/`) | jalan | `image/` berisi 7 file saat ini; seluruhnya disalin, executable bit utuh |
| Preflight & pesan error `build.sh` | jalan | tanpa podman: exit 1 + pesan jelas. `--check` **belum pernah lolos** karena podman belum terpasang |
| Uji QEMU (`--test`) | terpasang di script | **belum pernah dijalankan** — belum ada ISO |

## Perubahan terakhir — utang teknis hook 0200 (2026-10-29)

Hook `.chroot` `0200-oracle-profiles` **dihapus**. Alasannya: hook itu memasang
paket profile lewat `apt-get` di dalam chroot, **setelah** live-build selesai
memasang paket inti. Satu image dibangun lewat dua jalur pemasangan berbeda.

Pengganti: `scripts/gen-profile-list.sh`, dipanggil `scripts/build.sh`
**sebelum** `lb build`. Skrip ini merakit
`build/config/package-lists/oracle-profiles.list.chroot` dari file profile,
sehingga live-build memasang paket inti dan paket profile lewat satu jalur.

Single source of truth tetap sama dan tetap satu:

```
image/config/includes.chroot/usr/share/oracle/profiles/<nama>.list
        │
        ├── build-time : scripts/gen-profile-list.sh  → package-list → lb build
        └── runtime    : `oracle profile install`     → apt-get
```

Tidak ada daftar paket kedua. Menambah paket = mengubah satu file profile.

Perilaku yang dijaga:

- Profile kosong / hanya komentar → **tidak** membuat file package-list.
  File kosong membuat live-build menganggap ada paket yang hilang.
- Paket duplikat antar profile dibuang, urutan kemunculan pertama dipertahankan.
- Nama profile divalidasi lawan `^[a-z0-9][a-z0-9-]{0,31}$` **sebelum**
  dipakai menyusun path (mencegah path traversal).
- Nama paket divalidasi lawan `^[a-z0-9][a-z0-9+.-]*$`.
- Input dibaca **per baris**, bukan per kata. Dulu `for x in $selected` memecah
  `net working` menjadi dua nama yang tampak sah.
- Spasi di tengah nama **tidak** di-strip. Bug lama: `net working` dirapikan
  menjadi `networking`, sehingga salah tulis di konfigurasi lolos diam-diam.
  Perbaikan ini juga diterapkan di CLI `oracle`.

Runtime install lewat CLI **tidak berubah**: `sudo oracle profile install <nama>`.

## Perintah tes — hasil LAMA (sebelum remediasi review)

> Dipertahankan sebagai jejak, **bukan** hasil terkini. Hasil terbaru ada di
> bagian "Hasil tes terkini" di bawah.

```
sh -n  image/config/hooks/live/*.chroot                    # OK
sh -n  image/config/includes.chroot/usr/local/bin/oracle   # OK
sh -n  scripts/gen-profile-list.sh                         # OK
bash -n scripts/build.sh                                   # OK
bash -n tests/cli_test.sh                                  # OK
bash -n tests/profile_list_test.sh                         # OK
./tests/cli_test.sh                                        # 17 lulus, 0 gagal
./tests/profile_list_test.sh                               # 25 lulus, 0 gagal
```

Cakupan `tests/profile_list_test.sh`: profile kosong, konfirmasi 0 byte,
profile valid, dua profile dengan paket beririsan, mode stdout, profile tidak
ada, `PROFILE_DIR` tidak ada, `PROFILES_CONF` tidak ada, nama paket berbahaya,
enam nama profile berbahaya (termasuk `net working`, `../../etc/passwd`,
`x;rm -rf /`), path traversal, ketiadaan direktori liar di repo, dan
idempoten saat dijalankan dua kali.

Uji hook dan generator dilakukan dengan menyalin berkas ke direktori sementara
dan mengalihkan `/etc`, `/usr/share`, `PROFILES_CONF`, `PROFILE_DIR`, `OUT`.
Semua uji berjalan di host. Tidak ada apt, tidak ada `lb build`, tidak ada ISO.

## Perbaikan F-1 .. F-4 (2026-10-29)

Empat temuan review ditutup. **F-5 sengaja tidak diubah** — lihat bagian
Keputusan desain tertunda.

### F-2 — `${ID^^}` bashism (KRITIS, selesai)

`image/auto/config` ber-shebang `#!/bin/sh` tetapi memakai `${ID^^}`.
Di Debian `/bin/sh` adalah dash, yang menolak bentuk itu dengan
`Bad substitution`. Diganti:

```sh
ISO_VOLUME="$(printf '%s' "${ID}" | tr 'a-z' 'A-Z')"
```

Ditambah validasi `ID` (`^[a-z0-9][a-z0-9-]*$`) sebelum dipakai sebagai nama
volume ISO9660.

### F-1 + F-8 — urutan `lb config` (KRITIS, selesai)

`scripts/build.sh` sebelumnya hanya menjalankan `lb build`. Tanpa `lb config`,
live-build berhenti dengan `E: the following stage is required to be done first: config`.

Alur sekarang tiga tahap, dan urutannya penting:

1. bersihkan `build/`, salin `image/` → `build/`, siapkan builder image
2. **`lb config`**
3. **baru** pulihkan aset proyek: seluruh `includes.chroot`, `etc/oracle/*`,
   `config/hooks`, lalu package-list hasil generator
4. `lb build`

Tahap 3 harus setelah tahap 2 karena `lb config` mempopulasi `config/`
dan dapat membuang isi `includes.chroot` serta `package-lists`. Ini bukan
dugaan: tes `tests/build_order_test.sh` memasang tiruan `lb config` yang
sengaja menghapus `includes.chroot`, dan sebelum perbaikan tes itu gagal
(aset proyek hilang).

`build.sh` juga menolak melanjutkan kalau `config/` tidak terbentuk setelah
`lb config`.

### F-3 + F-4 — parser & validasi paket CLI (TINGGI, selesai)

`oracle` sebelumnya memakai `sed -e 's/[[:space:]]//g'`, yang menghapus spasi
**di tengah**: `ip route2` → `iproute2`, ` bad name ` → `badname`. Salah tulis
menjadi nama paket sah, tanpa peringatan. Nama paket juga tidak divalidasi
sebelum `apt-get` dipanggil.

Sekarang aturannya identik dengan `scripts/gen-profile-list.sh`:

- dibaca per baris (`while IFS= read -r`), bukan per kata
- hanya spasi di ujung yang dibuang
- tiap entri divalidasi `^[a-z0-9][a-z0-9+.-]*$`
- `check` dan `install` sama-sama menolak sebelum `apt-get` dipanggil

## Keputusan desain tertunda

### F-5 — `oracle profile list` tidak menampilkan status terpasang

**Perilaku saat ini DIPERTAHANKAN, bukan bug yang belum diperbaiki.**

`list` membaca `PROFILE_DIR` dan menampilkan semua profile yang **tersedia**.
`install` hanya menjalankan `apt-get` dan tidak menulis state apa pun. Jadi
setelah `sudo oracle profile install networking`, keluaran `list` tidak
berubah, dan tidak ada perintah untuk memeriksa profile mana yang sudah
terpasang.

Belum diputuskan apakah:
1. `list` menandai status terpasang (butuh state file + penanganan kegagalan
   sebagian), atau
2. ditambah subperintah `oracle profile status`, atau
3. perilaku sekarang dibiarkan dan status diperiksa lewat `dpkg -l`.

Keputusan ini menunggu, karena setiap pilihan menambah state yang harus
dijaga konsisten dengan apt.

## Hasil tes terkini (pasca remediasi review)

Satu perintah menjalankan semuanya:

```
./tests/run_all.sh
```

| Tes | Hasil |
|---|---|
| `tests/posix_test.sh` | 14 lulus, 0 gagal |
| `tests/profile_list_test.sh` | 25 lulus, 0 gagal |
| `tests/cli_test.sh` | 17 lulus, 0 gagal |
| `tests/cli_packages_test.sh` | 45 lulus, 0 gagal |
| `tests/lb_config_flow_test.sh` | 17 lulus, 0 gagal |
| `tests/build_order_test.sh` | 33 lulus, 0 gagal |
| **Total** | **151 assertion, 6/6 tes lulus** |

Validasi sintaks:

```
bash -n scripts/build.sh scripts/gen-profile-list.sh
bash -n tests/{run_all,cli,profile_list,posix,build_order,cli_packages,lb_config_flow}_test.sh
sh   -n image/auto/config
sh   -n image/config/hooks/live/0100-oracle-identity.hook.chroot
sh   -n image/config/includes.chroot/usr/local/bin/oracle
```

`./scripts/build.sh --check` → **exit 1**, pesan: `podman belum terpasang`.
Ini perilaku yang benar, bukan kegagalan tes. (Catatan lama "`--check` lolos"
sudah tidak berlaku: podman belum terpasang di mesin ini.)

### Keterbatasan pengujian — baca sebelum mengklaim apa pun

Batas tegas antara **tiruan** dan **live-build asli**:

| Yang diuji | Dengan apa | Kekuatan bukti |
|---|---|---|
| Urutan `lb config` → `lb build`, staging, pemulihan aset | podman + `lb` **tiruan** | Konsistensi terhadap semantik yang didokumentasikan. Bukan perilaku live-build asli. |
| Tidak ada rekursi `auto/config` | `lb` **tiruan** semantik manual §6.1.1–6.1.2 | Sama seperti di atas. |
| Logika parser, validasi nama, pesan error | fungsi asli, fixture di TMP | Kuat — kode produksi yang dijalankan. |
| Kompatibilitas dash | pemindai **statis** | Lemah — pola dicari, dash tidak dijalankan. |
| Pemasangan profile | `apt-get` **palsu** | Lemah — tidak ada paket yang benar-benar dipasang. |

1. **dash tidak dieksekusi.** `/bin/sh` di host Omarchy adalah symlink ke
   bash. dash dan busybox tidak terpasang; memasangnya butuh sudo. Lulus
   `posix_test.sh` berarti "tidak ada pola bashism yang dikenal", **bukan**
   "sudah terbukti jalan di dash".
2. **live-build tidak pernah dijalankan.** `lb config` dan `lb build` tidak
   ada di mesin ini. Semua tes alur memakai tiruan. Perilaku `lb config` yang
   sebenarnya — termasuk apakah ia benar-benar menghapus `includes.chroot` dan
   `package-lists` — **belum terverifikasi**.
3. **podman tidak pernah dijalankan.** Tidak ada container yang dibuat.
4. **`apt-get` selalu palsu.** Tidak ada paket dipasang di host.
5. **Tidak ada ISO.** Tidak ada klaim build berhasil, tidak ada klaim boot.

### Verifikasi bahwa tes benar-benar bisa gagal

Tes yang selalu hijau tidak membuktikan apa pun. Yang sudah dibuktikan bisa
gagal:

- `${ID^^}` disisipkan kembali ke **salinan** repo → `posix_test.sh` 2 FAIL.
- Satu tes dirusak di **salinan** repo → `run_all.sh` melaporkan `GAGAL`,
  ringkasan menyebut file yang gagal, exit code 1. Dengan `--stop`, berhenti
  pada kegagalan pertama, exit 1.

Repo asli tidak disentuh pada kedua percobaan.

## Remediasi review final (2026-10-29, sesi lanjutan)

### K-1 + K-2 — alur konfigurasi live-build (KRITIS, selesai)

**Masalah:** `auto/config` memanggil `lb config` tanpa `noauto`. Karena
`lb config` menjalankan `auto/config` secara otomatis, setiap pemanggilan
memicu pemanggilan berikutnya. Manual Debian Live §6.1.2 menyebut `noauto`
wajib untuk mencegah rekursi.

**Alur yang dipilih — satu pemilik konfigurasi:**

```
scripts/build.sh  →  lb config                    (tanpa argumen)
                        ↓ live-build menjalankan auto/config otomatis
image/auto/config →  lb config noauto <flag> "${@}"
                        ↓ noauto menghentikan rekursi
                     konfigurasi tertulis sekali
```

- `auto/config` adalah **pemilik tunggal** seluruh flag (distribusi,
  arsitektur, area arsip, iso-*). Tidak ada tempat lain yang menetapkan opsi.
- `build.sh` memanggil `lb config` **polos**, tanpa flag, supaya tidak ada
  dua pemilik konfigurasi.
- `"${@}"` diteruskan, sehingga `lb config --verbose` dari luar tidak hilang.
- Satu konfigurasi efektif per build. Tidak ada pemanggilan ganda.

**Bukti:** `tests/lb_config_flow_test.sh` — tiruan `lb` sesuai semantik manual,
dengan batas keras 50 panggilan. Hasil: tepat 1 panggilan saat `auto/config`
dijalankan langsung, tepat 2 saat lewat `lb config` (luar tanpa `noauto`,
dalam dengan `noauto`). Sebelum perbaikan, simulasi yang sama mencapai 1150
panggilan dalam 6 detik lalu hang.

### T-1 — package-list preservation (TINGGI, selesai)

`build.sh` sekarang memulihkan **seluruh** `config/package-lists/` dari
`image/`, bukan hanya file hasil generator. Ditambah guard: kalau
`oracle-core.list.chroot` hilang atau kosong setelah `lb config`, build
dihentikan — tanpa paket inti, image tidak akan punya `live-boot` atau kernel.

**Bukti:** tiruan `lb config` di `tests/build_order_test.sh` diperkuat sehingga
menghapus **seluruh** `package-lists/` termasuk `oracle-core`. Hasil: 35 paket
inti dipulihkan, `live-boot` ada, package-list bawaan live-build tetap utuh.

### T-2 — build guard (TINGGI, selesai)

Guard lama `[ -d build/config ]` selalu benar, karena `cp -a image/. build/`
sudah menyalin `image/config` sebelum `lb config`. Diganti dengan pemeriksaan
`config/binary` — berkas yang menurut `lb_config(1)` dihasilkan oleh
`lb config` bersama `config/{bootstrap,chroot,common,source}`.

`.build/` **tidak** dijadikan syarat gagal. Keberadaan direktori itu asumsi
(direktori internal live-build, tidak dijamin manpage); menjadikannya syarat
bisa menghentikan build yang sebenarnya benar. Kalau ada, dicatat di log;
kalau tidak, hanya informasi.

**Bukti:** tiruan podman yang "sukses" tanpa menghasilkan `config/binary`
membuat `build.sh` exit 1 dengan pesan yang menyebut penyebab yang mungkin,
dan `lb build` tidak dipanggil.

### T-3 — dokumentasi CLI (SEDANG, selesai)

Header `oracle` sekarang menyatakan berkas ini **alat runtime saja**;
build-time ditangani `scripts/gen-profile-list.sh`. Keduanya membaca file
profile yang sama, dengan aturan validasi identik.

### R-2 — pra-cek CLI redundan (RENDAH, selesai)

Pra-cek `case` di `valid_name()` dihapus. Pra-cek itu tidak membatasi panjang
nama, sehingga nama 33+ karakter lolos pra-cek lalu ditolak regex — dua aturan
untuk satu hal, dan yang lebih longgar sempat menang. Sekarang regex adalah
satu-satunya sumber kebenaran, identik dengan generator.

### R-1 — runner tes terpadu (RENDAH, selesai)

`tests/run_all.sh` menjalankan keenam tes, melaporkan tiap hasil, menyebut file
yang gagal, dan mengembalikan exit 1 bila ada kegagalan. Opsi `--stop`
(berhenti pada kegagalan pertama) dan `--quiet`.

**Bukti bahwa runner bisa gagal:** pada salinan repo dengan satu tes dirusak,
runner melaporkan `GAGAL`, ringkasan menyebut file, exit 1; dengan `--stop`
berhenti setelah tes yang gagal. Repo asli tidak disentuh.

### R-3 — `auto/build` dan `auto/clean` (RENDAH, KEPUTUSAN TERTUNDA)

Belum ditambahkan. Alasan:

- **`auto/clean`** tidak diperlukan: `build.sh` sudah menghapus seluruh `build/`
  dengan `sudo rm -rf` pada setiap run, jadi variabel konfigurasi lama tidak
  pernah bertahan.
- **`auto/build`** hanya menghasilkan `build.log` otomatis (Manual §6.1.1).
  Berguna, tetapi belum wajib, dan menambah satu berkas yang harus dipelihara.
  Dicatat sebagai kandidat bila nanti build sudah benar-benar berjalan dan
  log persisten dibutuhkan untuk diagnosis.

## Blocker yang belum terselesaikan

1. **Podman belum terpasang.** Butuh `sudo pacman -S podman` oleh pemilik mesin.
2. **QEMU belum terpasang.** Butuh `sudo pacman -S qemu-base` sebelum uji boot.
3. **ISO belum pernah dibangun.** Setiap klaim "build berhasil" belum punya bukti.
4. **Perilaku live-build asli belum terverifikasi.** Alur `noauto` mengikuti
   Manual Debian Live §6.1.1–6.1.2 dan diuji melawan tiruan semantik, tetapi
   `lb config`/`lb build` belum pernah dijalankan di mesin ini. Secara khusus
   BELUM terbukti apakah `lb config` benar-benar menghapus `includes.chroot`
   dan `package-lists`; build.sh memulihkan keduanya sebagai tindakan preventif
   terhadap kemungkinan itu, bukan karena sudah dibuktikan.
5. **F-9 belum terverifikasi:** apakah `build/` menjadi milik root karena
   `--privileged` + `userns=host`. `build.sh` sudah memakai `sudo rm -rf`.

## Utang teknis (bukan blocker)

- Desktop environment, firewall default, dan hardening belum ditentukan
  (ARCHITECTURE §5 dan §6 masih TBD).
- ARCHITECTURE §8 belum menyebut pemisahan profile build-time vs runtime
  secara eksplisit; perlu disesuaikan saat berikutnya menyentuh dokumen itu.
- F-9 (`build/` bisa jadi milik root karena `--privileged` + `userns=host`)
  belum terverifikasi. `build.sh` sudah memakai `sudo rm -rf` untuk berjaga.
- F-10 (executable bit CLI di dalam image) dijaga manual lewat `chmod +x`
  di `build.sh`; belum ada mekanisme struktural.

## Langkah berikutnya

```bash
cd ~/Projects/Oracle-OS
sudo pacman -S podman qemu-base   # butuh izin pemilik mesin
./scripts/build.sh --check
./scripts/build.sh                # build ISO pertama
./scripts/build.sh --test         # boot di QEMU setelah ISO ada
```

Yang harus diverifikasi di dalam QEMU setelah ISO ada:

```bash
cat /etc/oracle-release      # ORACLE OS 0.1.0 (debian trixie)
hostname                     # oracle
cat /etc/os-release          # PRETTY_NAME="ORACLE OS 0.1.0"
oracle identity
oracle profile list
ip addr                      # jaringan dasar
```

## Melanjutkan setelah sesi AI berakhir

1. `git log --oneline -3` — lihat posisi terakhir.
2. Baca file ini.
3. Jalankan `./tests/cli_test.sh` — kalau lulus, dasar CLI masih utuh.
4. Lanjut ke blocker nomor 1: pasang podman, lalu build.