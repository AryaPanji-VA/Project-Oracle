# ORACLE OS — Saran Tahap Selanjutnya

> Laporan evaluasi. **Belum ada pekerjaan yang dijalankan** — ini bahan
> keputusan, bukan catatan pekerjaan selesai.
> Disusun: 2026-11-06, setelah ISO demo Phase 5 terverifikasi 40/40.

---

## 1. Di mana posisi proyek sebenarnya

Dokumen proyek belum mencerminkan kenyataan. Ini bukan kesalahan besar,
tapi harus diakui sebelum memilih langkah berikutnya:

| Sumber | Yang tertulis | Kenyataan |
|---|---|---|
| `docs/ROADMAP.md` | Phase 5 "Planned", 0/7 task dicentang | ~85% sudah dikerjakan |
| `docs/STATUS.md` | Terakhir diperbarui 2026-11-05, berhenti di Stage 3G | Phase 5 tidak disebut sama sekali |
| Git | HEAD `0a639ae`, sinkron origin | 11 file Phase 5 belum di-commit |
| CHANGELOG | tidak ada | — |

**Yang sudah terpenuhi dari 7 task Phase 5:**

- ✅ Build diulang dari kondisi terdokumentasi (`0a639ae` → ISO)
- ✅ Checklist pengujian per-image (`verify-iso.py`, 40 cek)
- ✅ Boot, konfigurasi, fungsi inti diuji (QEMU, probe serial)
- ⚠️ Known issues terdokumentasi — ada di `PHASE5-DEMO-USABLE.md` §6, tapi belum jadi dokumen tersendiri
- ✅ Checksum artefak rilis (SHA256SUMS + `.sha256` per ISO)
- ⚠️ Prosedur backup/pemulihan — ada di `~/oracle-recovery/README.md`, tapi di luar repo
- ❌ **Versi dan catatan perubahan — tidak ada**

Artinya Phase 5 belum benar-benar tutup menurut kriteria acceptance-nya
sendiri, meski produknya sudah jauh melampaui.

---

## 2. Tiga kandidat tahap berikutnya

### Opsi A — Tutup Phase 5 secara administratif

**Isi:** commit 11 file, centang roadmap, perbarui STATUS.md, buat
`CHANGELOG.md`, pindahkan known issues jadi dokumen, bersihkan 2 worktree
basi (`t_089a7170`, `t_bd3e7349`).

| | |
|---|---|
| Usaha | 1 sesi, kecil |
| Risiko | Nyaris nol |
| Hasil | Repo jujur; pekerjaan Phase 5 tidak hilang |

**Kenapa mendesak:** 11 file itu saat ini hanya ada di working tree. Satu
`git checkout .` atau kerusakan disk menghapus empat build dan seluruh
verifikasi. Ini risiko terbesar yang masih terbuka, dan paling murah ditutup.

---

### Opsi B — Installer (Calamares)

**Isi:** tambahkan Calamares ke ISO supaya ORACLE OS bisa dipasang ke disk.

**Fakta yang sudah saya verifikasi:** `calamares 3.3.14-1` **tersedia** di
repo Debian 13 (trixie), plus `calamares-settings-debian`. Jadi jalurnya
nyata, bukan spekulasi.

| | |
|---|---|
| Usaha | 2–3 sesi |
| Risiko | Sedang — partisi, bootloader, GRUB |
| Hasil | ORACLE OS jadi OS yang benar-benar terpasang |

**Kenapa ini penting:** tanpa installer, ORACLE OS selamanya demo. Semua
kerja identitas, tema, dan tooling tidak bisa dipakai sehari-hari karena
setiap reboot mengembalikan ke kondisi awal. Ini plafon produk.

**Yang harus diwaspadai:** Calamares menarik Qt/KDE — ISO akan membengkak
(perkiraan +150–250 MB). Perlu diuji apakah tema GTK ORACLE tetap utuh di
lingkungan Qt, dan apakah GRUB hasil install memakai branding ORACLE.

---

### Opsi C — Persistensi live

**Isi:** aktifkan persistensi live-boot (`persistence` label) supaya
perubahan bertahan antar-reboot tanpa installer.

| | |
|---|---|
| Usaha | 1 sesi |
| Risiko | Rendah |
| Hasil | Demo bisa "menyimpan keadaan", tapi bukan sistem terpasang |

**Kenapa dipertimbangkan:** ini 20% usaha dari Opsi B untuk 60% manfaat
demo. Kalau tujuanmu demo berulang ke orang lain, ini cukup.

**Batasnya:** tetap live image. Tidak ada manajemen paket permanen, tidak
ada update, tidak ada multi-user sungguhan. Ini menunda masalah, bukan
menyelesaikannya.

---

### Opsi D — Kernel Research (Phase 6 di roadmap)

Roadmap menaruh ini sebagai long-term. Saya **tidak menyarankan** ini
sekarang: ia tidak menambah kemampuan OS, dan roadmap sendiri menyatakan
ini bukan prasyarat. Mengerjakannya sebelum ada installer berarti
memperdalam fondasi bangunan yang belum punya pintu.

---

## 3. Rekomendasi

**Urutan: A → C → B.**

1. **A dulu, sekarang.** Bukan karena menarik, tapi karena 11 file tanpa
   commit adalah satu-satunya risiko yang bisa menghapus pekerjaan nyata.
   Sekali sesi, selesai.

2. **C sebelum B.** Persistensi membuat demo berikutnya terasa jauh lebih
   hidup, dengan risiko dan usaha jauh lebih kecil. Kamu bisa demo berkali-kali
   sambil menyiapkan installer dengan tenang.

3. **B sebagai tujuan sesungguhnya.** Di sinilah ORACLE OS berhenti jadi
   demo. Setelah ini, Phase 6 (kernel) baru masuk akal.

**Sebelum demo ke orang lain,** satu hal di luar urutan di atas: **uji boot
dari USB fisik.** Semua verifikasi kita di QEMU. Kegagalan paling umum di
hardware asli adalah driver grafis dan WiFi — dua hal yang tidak akan
muncul di QEMU. Ini butuh izin eksplisitmu karena menyentuh perangkat fisik
(Safety Boundaries §6).

---

## 4. Utang teknis yang belum tersentuh

Dicatat supaya tidak hilang, bukan untuk dikerjakan sekarang:

| Utang | Dampak |
|---|---|
| Tidak ada hardening (firewall, enkripsi, audit) | Belum layak dipakai online sehari-hari |
| `profiles.conf` kosong; NetworkManager masuk lewat desktop list | Keputusan belum tercatat di `DECISION-HISTORY.md` |
| Reproducibility tidak bit-untuk-bit (repo Debian bergerak) | Build ulang menghasilkan checksum berbeda |
| Belum ada snapshot repo Debian | Tidak ada jaminan build masa depan identik |
| 5 ISO iterasi (5.6 GB) belum diputuskan | Boros ruang, membingungkan saat demo |
| `build/` masih berisi ISO lama 31 Okt (824 MB) | Bukan artefak Phase 5, jangan tertukar |

---

## 5. Pertanyaan yang perlu kamu jawab

1. **Tujuan terdekatnya apa** — demo berulang ke orang, atau OS harian?
   Kalau demo: A → C. Kalau harian: A → B.
2. **Boleh commit?** Instruksi awal melarang commit/push. Kalau larangan
   itu masih berlaku, Opsi A harus diubah jadi "siapkan commit, jangan
   jalankan".
3. **Mau uji USB fisik?** Butuh persetujuan eksplisit.
4. **5 ISO iterasi** — simpan semua, atau sisakan yang demo saja?
