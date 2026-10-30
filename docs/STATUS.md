# ORACLE OS — Status

> Living document. Perbarui setiap sesi kerja.
> Terakhir diperbarui: 2026-10-30.

## Kondisi terkini

| Item | Kondisi |
|---|---|
| Branch | `main`; commit lokal belum dipush |
| Working tree | Ada perubahan dokumentasi Phase 0; periksa `git status` sebelum commit |
| Podman | 6.1.4 terpasang; paket Podman terkait sudah dipasang ulang |
| Rootful bridge | Gagal DNS dan TCP egress; network `podman` tercatat `dns_enabled=false` |
| Jalur build | `--network=host` lolos tes; script mewajibkan VM sebelum build privileged |
| VM build | Belum dibuat atau diuji; jalankan build hanya di VM NAT tanpa disk/folder host |
| ISO/build/boot | Belum dibangun atau diuji |

## Verifikasi dokumentasi dan repo (2026-10-30)

- Spesifikasi proyek ditulis di `docs/SPECIFICATION.md` dan workflow di
  `docs/DEVELOPMENT.md`; daftar identitas, konfigurasi image, paket inti,
  profile, dan direktori sumber telah dicocokkan dengan repo.
- Pemeriksaan sintaks shell lulus untuk skrip Bash dan skrip POSIX shell.
- `./tests/run_all.sh --quiet`: **7/7 test, 180 assertion lulus**.
- `git diff --check` lulus.
- Tidak dijalankan build ISO maupun boot; hasil test otomatis memakai mock
  untuk alur Podman/live-build.

`--network=host` melewati bridge untuk build. Di VM, builder berbagi jaringan
dan perangkat VM; jangan pass-through disk host atau share checkout asli.

## Kondisi repo

| Item | Kondisi |
|---|---|
| Branch | `main` |
| Working tree | (lihat kondisi terkini di atas) |
| Podman | (lihat kondisi terkini di atas) |
| QEMU | belum diverifikasi saat audit terakhir |
| Disk kosong | belum diverifikasi saat audit terakhir |
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
| Preflight & pesan error `build.sh` | implementasi ada | `--check` hanya memeriksa prasyarat dasar; tidak memverifikasi build live |
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

Catatan historis: `./scripts/build.sh --check` pernah exit 1 saat Podman belum
terpasang. Kondisi itu sudah berubah; jangan gunakan hasil lama sebagai status
host terkini.

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

## Catatan historis — blocker sebelum setup host terbaru

Daftar ini menggambarkan snapshot sebelum Podman dipasang dan dites pada
2026-10-30. Jangan gunakan sebagai status terkini; lihat tabel di bagian atas.

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
3. Jalankan `./tests/run_all.sh` — kalau lulus, dasar kode masih utuh.
4. Lanjut ke blocker nomor 1: pasang podman, lalu build.

## C + E — dokumentasi rootful & hardening mount (2026-10-30)

### C — koreksi klaim rootless/rootful

`ARCHITECTURE.md` §8, §14, dan `ROADMAP.md` masih menyebut build berjalan di
container **rootless** dan "tidak butuh grup container istimewa". Itu
bertentangan dengan `scripts/build.sh:37` (`PODMAN="sudo podman"`) dan dengan
B-2/B-3 di dokumen ini. Klaim lama sudah dikoreksi menjadi **rootful**,
lengkap dengan alasan teknis dan rujukan dokumentasi.

Isi baru di `ARCHITECTURE.md`:

- Alasan rootful: `live-build(7)` punya helper `lb chroot_proc`,
  `lb chroot_sysfs`, `lb chroot_devpts` (memasang kernel filesystem);
  `debootstrap(8)` memakai `chroot(2)` yang butuh `CAP_SYS_CHROOT`.
- Pernyataan tegas bahwa `--privileged` **mematikan** batas capability,
  pembatasan device, read-only kernel mount, dan confinement seccomp/AppArmor.
  Container privileged **bukan** sandbox.
- Bagian baru **"Blast radius of the build container"**: hanya `${ORACLE_ROOT}`
  yang di-mount, propagation default `private`, semua tulisan `build.sh` hanya
  ke `build/`, dan penegasan bahwa `:ro` **bukan** kontrol keamanan karena
  `CAP_SYS_ADMIN` bisa `mount -o remount,rw`.
- Tabel opsi privilege yang **belum diuji**, beserta trade-off masing-masing,
  dan rekomendasi: pertahankan `--privileged` untuk build pertama, turunkan
  setelah ada bukti.

### E — hardening mount (diterapkan)

Bind mount dipecah dua, di kedua tahap (`lb config` dan `lb build`):

```diff
-	-v "${ORACLE_ROOT}:/work:Z" \
+	-v "${ORACLE_ROOT}:/work:ro,Z" \
+	-v "${BUILD_DIR}:/work/build:rw,Z" \
```

`build/` dipasang **terpisah** karena submount tidak otomatis mewarisi `:ro`
dari induknya. Tanpa mount kedua, live-build tidak bisa menulis.

**Dasar penerapan (terverifikasi statis, bukan asumsi):** seluruh operasi
tulis di `scripts/build.sh` sudah diperiksa satu per satu. Tidak ada satu pun
yang menulis ke `image/`. `cp` hanya membaca dari `SOURCE_DIR`; `install`
membaca `ORACLE_ROOT/config/*` dan menulis ke `INCLUDES` (di dalam `build/`);
`chmod`/`find -exec chmod` hanya menyentuh `build/`. `gen-profile-list.sh`
hanya menulis ke `$OUT`, yang berada di `build/`.

**Batas yang diakui:** ini guardrail terhadap salah tulis, **bukan** kontrol
keamanan. Di container `--privileged`, `CAP_SYS_ADMIN` cukup untuk
`mount -o remount,rw`, sehingga `:ro` bisa dilewati oleh proses yang berniat
jahat. Nilainya nyata tetapi terbatas: mencegah `cp`/`rm` yang salah arah
merusak `image/`, dan membuat pelanggaran lapisan terlihat.

**Yang TIDAK diubah:** `--privileged`, `--userns=host`, dan penggunaan
`sudo podman` dibiarkan. Belum ada dasar terverifikasi bahwa varian
capability yang lebih sempit cukup untuk `lb build`. Mengubahnya sekarang
akan menukar risiko yang diketahui dengan kegagalan build yang belum
dipahami. Kandidatnya tercatat di `ARCHITECTURE.md` §14.

### Status verifikasi

| Klaim | Status |
|---|---|
| `build.sh` tidak menulis ke `image/` | ✅ statis, semua baris diperiksa |
| `build/` dipasang rw, repo ro | ✅ diterapkan di kedua tahap |
| Sintaks `build.sh` | ✅ `bash -n` |
| Suite tes | ✅ 151 assertion, 6/6 lulus |
|| `:ro` benar-benar mencegah tulis saat `--privileged` | ❌ **belum** — dan menurut dokumentasi bisa dilewati |
|| Varian privilege lebih sempit cukup untuk `lb build` | ❌ **belum diuji** |

## Historis — kegagalan rootful Podman bridge (2026-10-30)

Diagnosis awal dan restart service di bawah tidak menyelesaikan masalah bridge.
Kesimpulan terkini dan workaround build ada pada bagian "Tindak lanjut — jalur
jaringan build". Jangan memakai status `APPLIED` di catatan lama sebagai bukti
bahwa bridge sudah sehat.

### Diagnosis

Container rootless (pasta backend) berhasil DNS & HTTP. Container rootful (bridge
podman0) gagal DNS dan timeout pada `apt-get update`.

**Audit read-only (dua diagnosa):**

1. Network configuration di Podman metadata: lengkap
   - Subnet: `10.88.0.0/16`
   - Gateway: `10.88.0.1`
   - Driver: bridge
   - DNS enabled: false

2. Aturan netavark di kernel: KOSONG
   - nft table inet netavark: tidak ada entry NAT masquerade
   - iptables nat POSTROUTING: kosong
   - Interface podman0: TIDAK ADA (saat idle)

3. Saat container berjalan:
   - Interface podman0 muncul (10.88.0.1/16)
   - Veth interface terhubung ke bridge
   - Tetapi NAT rules tetap KOSONG
   - Container: TCP ke gateway CLOSED, DNS FAIL

4. Service status:
   - systemctl is-active podman: **inactive**
   - systemctl is-active podman-network: **inactive**

### Hipotesis awal (tidak mengonfirmasi akar masalah)

Catatan lama mengaitkan NAT yang hilang dengan status service Podman. Restart
service tidak memperbaiki bridge; reinstall paket juga tidak mengubah hasil.
Tes kemudian membuktikan host networking berfungsi, tetapi belum menemukan
penyebab mengapa rootful bridge tidak memasang NAT rules.

### Tindakan awal (tidak menyelesaikan masalah)

```bash
sudo systemctl restart podman
```

**Dampak:**
- Podman daemon di-restart
- Netavark rules akan di-generate ulang saat container pertama kali dijalankan
- Container yang sedang berjalan dihentikan & dimulai ulang
- UFW config tidak berubah
- Kernel parameter tidak berubah

**Reversibilitas:** Idempoten; jalankan ulang untuk reset atau `systemctl restart podman`

### Verifikasi (PENDING)

Status: `sudo systemctl restart podman` BERHASIL dijalankan.
Podman status: `active` ✅

Test DNS rootful: **BLOCKED** (biometric auth timeout pada sudo)
- Perintah yang perlu dijalankan manual:
  ```bash
  sudo podman run --rm docker.io/library/debian:13 getent ahosts deb.debian.org
  ```
  Jika sukses → IP addresses ditampilkan
  Jika gagal → "Temporary failure resolving" atau timeout

Test rootless baseline: **OK** ✅
- rootless DNS: `151.101.194.132 STREAM debian.map.fastlydns.net` (berhasil)

**Session status (2026-10-30T05:30Z):**
- Perbaikan applied: systemctl restart podman (status = active)
- DNS verify rootful: BLOCKED (biometric auth timeout on sudo)
- APT verify rootful: BLOCKED (biometric auth timeout on sudo)
- Build start: BLOCKED (same biometric auth issue)

**Instruksi lama di bawah bagian ini sudah ditarik:** jangan menambahkan aturan
sudoers `NOPASSWD` untuk Podman/systemctl. Jalankan perintah admin secara
interaktif dari terminal host bila memang diperlukan.

### Tindak lanjut — jalur jaringan build (2026-10-30)

Reinstall `podman`, `containers-common`, `netavark`, `aardvark-dns`, `conmon`,
`catatonit`, dan `passt` tidak mengubah hasil bridge: network `podman` kosong,
`dns_enabled=false`, DNS gagal (`exit 2`), dan TCP egress gagal (`exit 124`).
Tes pada image Debian 13 yang sama berhasil dengan `--network=host` untuk DNS
dan TCP (`HOSTNET_DNS=0 HOSTNET_TCP=0`).

**Perbaikan build:** `scripts/build.sh` kini memakai host networking untuk
`podman build` serta kedua container `lb config`/`lb build`. Ini melewati
bridge/NAT yang gagal tanpa mengubah firewall host. Konsekuensinya, proses
builder dapat menjangkau layanan lokal host; gunakan hanya dengan source dan
builder yang dipercaya. Tidak ada ISO yang dibangun atau di-boot.

## Historis — preflight sebelum Podman dipasang ulang (2026-10-30T08:00Z)

Snapshot berikut dibuat sebelum reinstall dan sebelum tes `--network=host`.
Status jaringan dan paket di dalamnya sudah kedaluwarsa.

### Read-Only Verification (no sudo auth required)

**Static prerequisites:**
- Source files (image/auto/config, image/config/, image/Containerfile): ✅ ALL PRESENT
- Build script (scripts/build.sh): ✅ READY & EXECUTABLE
- Config identity: ✅ COMPLETE (ORACLE OS 0.1.0, Debian 13 trixie)
- Test suite: ✅ 7/7 passing (175 assertions)
- Disk space: ✅ SUFFICIENT (135GB available, need ~2GB)
- IPv4 forwarding: ✅ ENABLED (required for rootful bridge)
- DNS (rootless baseline): ✅ OK (151.101.194.132 resolves deb.debian.org)

**Cannot verify (requires sudo auth — blocked by biometric timeout):**
- Rootful Podman DNS access (test: `sudo podman run docker.io/library/debian:13 getent ahosts deb.debian.org`)
- Registry pull capability (test: `sudo podman pull --dry-run docker.io/library/debian:13`)
- Builder image build execution

### Build Readiness Assessment

**Ready to proceed:**
✅ All static requirements satisfied
✅ build.sh script complete & tested
✅ live-build configuration present
✅ Containerfile valid (guard + mount flags verified)
✅ Repository tests all passing

**Risk assessment:**
- Builder image does not exist yet (will be created during build)
- Network connectivity unverified for rootful (low risk — baseline DNS OK)
- Biometric auth required for manual build execution

### Next Steps for Phase 1 (M1 — First Boot)

1. **Option A:** Manual build in terminal (you execute)
   ```bash
   cd ~/Projects/Oracle-OS
   ./scripts/build.sh
   ```
   - Tap biometric when prompted
   - Wait 30-60 minutes
   - Report output (success / fail)

2. **Option B:** Continue next session
   - All preflight checks complete ✅
   - Build script ready ✅
   - Can start immediately when approved

### Decision Required

Build still requires a deliberate user start from the host terminal with normal
interactive `sudo`. The real build and boot remain unverified.

Current status: **READY, AWAITING APPROVAL**
| Build ISO nyata | ❌ belum pernah dijalankan |
