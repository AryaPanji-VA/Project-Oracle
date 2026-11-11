# ORACLE OS — Status Penghentian Sementara (On Hold)

**Dihentikan:** 2026-11-11
**Alasan:** pemilik (Arya) fokus pada project kampus.
**Rencana lanjutan:** belum ditetapkan — buka dokumen ini lagi kapan pun.

Dokumen ini ditulis supaya proyek bisa dilanjutkan bertahun-tahun kemudian
tanpa perlu mengingat-ingat atau mengulang pekerjaan yang sudah selesai.

---

## 1. Posisi terakhir

- **Branch:** `main`
- **HEAD saat dihentikan:** commit `1f5179d` (docs roadmap) + commit README on-hold
- **Remote:** `origin/main` di `0a639ae` — beberapa commit lokal mungkin
  belum ter-push saat dokumen ini ditulis; **cek `git log origin/main..HEAD`
  lebih dulu dan push sebelum melanjutkan apapun.**
- **Working tree:** bersih; semua pekerjaan tooling sudah ter-commit.
- **Test suite:** `./tests/run_all.sh` → **10/10 suite, 246 assertion**
  (host) dan 10/10 di guest Debian build.

## 2. Status fase (ROADMAP per 2026-11-11)

| Phase | Status |
|---|---|
| 0 — Foundation | Complete |
| 1 — First Bootable | Complete |
| 2 — Core Identity | Complete |
| 3 — Sentinel Security Lab | In Progress (4/7) |
| 4 — ORACLE Tooling | Done |
| 5 — Reliability & Release | Done |
| 6 — Kernel Research | Long-term, belum dimulai |

## 3. Yang BEKERJA dan sudah dibuktikan

Jangan bangun ulang ini — sudah jadi dan sudah diverifikasi di ISO yang
di-boot sungguhan, bukan cuma di shell development:

- **ISO desktop demo-usable:** boot → LightDM → XFCE, identitas `ORACLE OS
  0.1.0`, network-manager, firefox-esr, audio stack + volume control di
  panel, polkit agent. Verifikasi E2E `verify-iso.py`: **40/40**.
- **`oracle status`** — dashboard satu layar (kernel, disk, network, unit
  gagal, postur keamanan).
- **`oracle doctor`** — self-check dengan saran perbaikan konkret.
- **`oracle lab`** — security lab dua network namespace (`10.66.0.1`
  attacker / `10.66.0.2` target, veth, tanpa rute keluar, DNS ditutup).
  Butuh sudo; alasan teknis dan jebakan yang sudah dilewati ada di
  `docs/ORACLE-TOOLING.md`. Verifikasi E2E `verify-tooling.py`: **22/22**.
- **Build reproducibility:** `./scripts/build.sh` dari checkout bersih di
  guest Debian 13 menghasilkan ISO yang bisa di-boot (±50-70 menit).

## 4. Artefak rilis

Di luar repo (ISO tidak pernah di-commit):

| File | Lokasi | sha256 |
|---|---|---|
| ISO final tooling | `~/Backups/ORACLE-OS-tooling.iso` | `0ae7e8fc…f674` |
| ISO Phase 5 demo | `~/Backups/ORACLE-OS-phase5-demo.iso` | `d151b694…` |
| Baseline lama | `~/Backups/oracle-os_baseline_*` | lihat `build/SHA256SUMS` |

`sha256sum -c` sudah lulus untuk keduanya. **Backup ini hanya ada di disk
host** — kalau host reset lagi (pernah terjadi), pertimbangkan menyimpan
salinan di luar mesin sebelum proyek lama berhenti.

## 5. Environment build (jangan diulang dari nol)

- Build **wajib di VM Debian 13** (`~/VMs/oracle-debian13`, SSH port 2223,
  user `oraclebuild`, key `~/VMs/oracle-debian13/ssh/`). Guard
  `require_build_vm()` di `scripts/build.sh` menolak bare metal — itu fitur,
  bukan bug.
- Checkout build aktif di guest: `~/oracle-phase5`. Direktori
  `~/oracle-os-graphical` di guest = arsip lineage lama; jangan dihapus.
- Snapshot qcow2 `pre-phase5-recovery` terdaftar di disk VM.
- Tooling recovery host: `~/oracle-recovery/` (`boot-vm.sh`, `run-demo.sh`,
  `verify-iso.py`, `verify-tooling.py`, `PHASE5-SUMMARY.md`). **Direktori ini
  di luar repo dan tidak ter-backup ke Git — kalau ingin aman, commit ke
  folder `tools/` saat melanjutkan.**

## 6. Yang TERBUKA saat dihentikan

Sesuai `docs/NEXT-STAGE-REPORT.md` (rekomendasi A → C → B):

1. **(A) Administratif** — DONE: roadmap direkonsiliasi (`1f5179d`).
2. **(C) Persistensi live session** — belum dimulai. Prioritas #1 saat
   lanjut: tanpa ini semua hasil `oracle lab` dan konfigurasi hilang saat
   reboot.
3. **(B) Installer Calamares** — belum dimulai. `calamares 3.3.14-1`
   tersedia di Debian 13; estimasi +150-250 MB ISO.
4. **Sisa Phase 3 (3/7 task):** snapshot/recovery eksperimen lab, target
   latihan lokal, prosedur eksperimen terdokumentasi.
5. **Dekorasi ISO lama:** `~/VMs/oracle-debian13/phase5-out/` menampung 6
   ISO (±6.7 GB). Tidak ada yang dihapus tanpa izin Arya; candidates aman
   untuk dibuang: build1/build2/build3 (build4=final, build5=demo, tooling
   =terbaru).

## 7. Batas yang diketahui (jangan diklaim sebaliknya)

- Belum ada installer — ISO hanya live.
- Tidak ada persistensi — semua perubahan hilang saat reboot.
- Belum diuji di hardware fisik sungguhan (hanya QEMU).
- Belum ada hardening keamanan serius; `oracle lab` terisolasi tapi OS-nya
  bukan security-hardened.
- `oracle lab` di ISO default belum membawa nmap/nc/curl/tcpdump (alat ada
  di profil `networking`); perintah melaporkan ini secara jujur.
- Push ke GitHub membutuhkan `gh auth login` interaktif (tidak ada
  kredensial non-interaktif di host saat penghentian).

## 8. Cara melanjutkan (checklist)

```bash
cd ~/Projects/Oracle-OS
git log origin/main..HEAD          # 1. push dulu kalau masih ada lokal
./tests/run_all.sh                 # 2. pastikan 10/10 masih hijau
# 3. nyalakan VM build: ~/oracle-recovery/boot-vm.sh
#    sinkronkan repo ke guest ~/oracle-phase5 (tar|ssh; rsync tidak ada)
# 4. baca docs/NEXT-STAGE-REPORT.md → pilih C (persistensi) atau B (installer)
```

Prinsip yang berlaku terus: build hanya di guest, jangan sentuh baseline
backup, jangan commit/push tanpa persetujuan, laporan jujur > klaim bersih.
