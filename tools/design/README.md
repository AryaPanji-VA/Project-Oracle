# ORACLE-OS — Design Tools (disalin dari design repository)

Asal: `~/Projects/oracle-brand-assets/tools/`
Status: **arsip referensi**, bukan bagian dari build.

---

## Peringatan: tool ini TIDAK siap jalan di repo ini

Tool di direktori ini ditulis di **design repository** dan masih memakai
path absolut ke lokasi aslinya:

| Pola | Contoh di file |
|---|---|
| `~/Projects/oracle-brand-assets` | `audit_consistency.py:16` |
| `~/.hermes/profiles/doraemon/cache/scratch/oracle-design` | sumber `.deb`, font, CSS Arc |

Konsekuensi:

- `audit_consistency.py` akan mengaudit **design repository**, bukan repo ini.
- `validate_greeter.py` dan `gen_papirus.py` butuh berkas `.deb` di cache
  scratch yang **tidak ada di repo ini**.
- `gtk_recolor.py` butuh CSS Arc sumber yang juga di cache scratch.

**Jangan menjalankan tool ini terhadap repo ini tanpa menyesuaikan path.**
Saat ini fungsinya adalah mendokumentasikan **bagaimana aset dibuat**, bukan
untuk dijalankan ulang dari repo ini.

---

## Isi

| File | Fungsi | Bisa jalan di sini? |
|---|---|---|
| `gen_assets.py` | generator Dial/wordmark/lockup | tidak (butuh font Inter) |
| `audit_assets.py` | audit geometri + kontras brand | tidak |
| `wallpaper_workspace.py` | generator wallpaper Workspace | tidak |
| `wallpaper_minimal.py` | generator wallpaper Minimal | tidak |
| `gtk_recolor.py` | recolor CSS + aset Arc | tidak (butuh sumber Arc) |
| `gen_panel.py` | generator xfce4-panel.xml + preview | ya, sebagian |
| `gen_terminal.py` | generator colorscheme + preview | tidak (butuh Inter) |
| `gen_papirus.py` | generator ORACLE-Papirus | tidak (butuh Papirus .deb) |
| `gen_greeter.py` | generator conf + CSS greeter | **ya** |
| `validate_terminal.py` | validator terminal | **ya** |
| `validate_papirus.py` | validator Papirus | tidak (butuh .deb) |
| `validate_greeter.py` | validator greeter | tidak (butuh binary .deb) |
| `audit_consistency.py` | audit konsistensi global | tidak (path absolut) |
| `preview_papirus.py` | render grid ikon | tidak |
| `preview_greeter.py` | render preview greeter GTK3 | **ya** |

Hanya 4 dari 15 yang bisa dijalankan tanpa penyesuaian: `gen_greeter.py`,
`validate_terminal.py`, `preview_greeter.py`, dan sebagian `gen_panel.py`.

---

## Mengapa tidak diperbaiki sekarang

Stage 3A hanya memindahkan aset dan dokumentasi. Memperbaiki path tool
memerlukan:

1. Menetapkan lokasi sumber (`.deb`, CSS Arc, font) **di dalam repo** atau
   sebagai input eksternal yang terdokumentasi.
2. Menyesuaikan seluruh generator dan validator.
3. Menguji ulang setiap tool.

Itu pekerjaan tipe refactor, dan Stage 3A melarang refactor arsitektur.

Akan dikerjakan pada tahap implementasi, bila tool perlu dijalankan ulang
dari repo ini. Sampai saat itu, **design repository tetap menjadi tempat
tool dijalankan** — dan repo itu sengaja dipertahankan sebagai arsip.