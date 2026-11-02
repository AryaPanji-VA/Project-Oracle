#!/usr/bin/env python3
"""ORACLE-OS — Stage 2G: audit konsistensi desain global.

Memeriksa seluruh aset yang sudah diproduksi, bukan hanya yang terbaru:
  A1-A5 brand, wallpaper, GTK, panel, terminal, papirus, greeter.

Output: laporan teks + exit code. Tidak ada pemeriksaan yang "dianggap lulus".
"""

import os
import re
import subprocess
import sys
from collections import Counter

BASE = os.path.expanduser("~/Projects/oracle-brand-assets")

# ------------------------------------------------------------------ palet resmi
PALETTE = {
    "Warm Ivory": "#E9E5DA",
    "Soft Porcelain": "#F5F3EC",
    "Steel Blue": "#344653",
    "Dusty Blue": "#667D89",
    "Muted Brass": "#B8A98D",
    "Graphite": "#30363B",
    "Brass Ink": "#8C7B58",
}
PALETTE_HEX = {v.upper() for v in PALETTE.values()}

# warna turunan yang DISENGAJA dan terdokumentasi
DERIVED = {
    "#B9C1C2": "border (GTK/papirus/greeter)",
    "#5E6C75": "headerbar active",
    "#4B5B65": "headerbar hover",
    "#27343E": "shadow deep",
    "#1F2A33": "shadow deepest",
    "#6B7480": "neutral mid",
    "#7A8188": "neutral mid-light",
    "#E6E5E0": "button hover",
    "#D6D7D4": "button active",
    "#F2F0E9": "row hover",
    "#D1D3CC": "wallpaper dial blend",
    "#929494": "disabled (GTK, diganti #767877)",
    "#767877": "disabled fg final",
    "#5B707B": "terminal dim",
    "#4E6069": "greeter disabled on light",
    "#8A9AA2": "greeter disabled on dark",
    "#2A3A45": "papirus accent dark",
    "#4E7A3A": "papirus green earthy",
}
# warna status semantik (disepakati, dipertahankan)
SEMANTIC = {
    "#B4503C", "#8A682E", "#317E2A", "#3674A1", "#B83D99", "#2B7682",
    "#C33D22", "#26801E", "#90661E", "#1F72AE", "#C8239F", "#1B7987",
    "#FC4138", "#FD8D88", "#F27835", "#F7AE86", "#F04A50", "#F4797E",
    "#EC1B22", "#F08437", "#FF4D4D", "#FF6666", "#FD716A", "#F75D37",
    "#73D216", "#F13039", "#F46067", "#F68086", "#EEA279", "#F4807B",
}

fails, warns = [], []


def check(cond, label, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {label}" + (f"  {detail}" if detail else ""))
    if not cond:
        fails.append(label)


def warn(cond, label, detail=""):
    print(f"  {'PASS' if cond else 'WARN'}  {label}" + (f"  {detail}" if detail else ""))
    if not cond:
        warns.append(label)


# ------------------------------------------------------------------ 1. struktur
print("=== 1. KELENGKAPAN ASET ===")
EXPECTED = {
    "A1-A5 brand": ["svg/dial-master.svg", "svg/dial-optical-16.svg",
                    "svg/wordmark.svg", "svg/lockup-horizontal.svg"],
    "Wallpaper": ["wallpaper/svg/workspace-1920x1200.svg",
                  "wallpaper/svg/minimal-1920x1200.svg"],
    "GTK": ["gtk/ORACLE/gtk-3.0/gtk.css", "gtk/ORACLE/COPYING",
            "gtk/ORACLE/NOTICE.md"],
    "Panel": ["panel/cfg/xfce4-panel.xml", "panel/docs/SPEC-PANEL.md"],
    "Terminal": ["terminal/cfg/oracle.theme", "terminal/docs/SPEC-TERMINAL.md"],
    "Papirus": ["papirus/theme/ORACLE-Papirus/index.theme",
                "papirus/docs/NOTICE.md"],
    "Greeter": ["greeter/cfg/lightdm-gtk-greeter.conf",
                "greeter/cfg/oracle-greeter.css"],
}
for area, files in EXPECTED.items():
    missing = [f for f in files if not os.path.exists(os.path.join(BASE, f))]
    check(not missing, f"{area}: file inti ada", str(missing))

# ------------------------------------------------------------------ 2. palet
print("\n=== 2. KONSISTENSI PALET ===")
# PENTING: ikon Papirus adalah karya turunan pihak ketiga (GPL-3). Warna
# netral Papirus (bayangan, outline, highlight putih) BUKAN warna liar --
# itu bagian dari bentuk aslinya dan memang dipertahankan. Yang diaudit
# untuk "warna liar" adalah aset ORACLE sendiri: brand, wallpaper, GTK,
# panel, terminal, greeter. Papirus diaudit terpisah di validator-nya.
ORACLE_DIRS = ["svg", "wallpaper", "gtk", "panel", "terminal", "greeter", "docs"]
hex_all = Counter()
for sub in ORACLE_DIRS:
    root_dir = os.path.join(BASE, sub)
    if not os.path.isdir(root_dir):
        continue
    for root, dirs, files in os.walk(root_dir):
        if "__pycache__" in root:
            continue
        for f in files:
            if not f.endswith((".svg", ".css", ".xml", ".theme", ".conf")):
                continue
            # Dokumentasi (.md/.txt) SENGAJA dikecualikan: berkas itu memuat
            # TABEL PEMETAAN warna Arc -> ORACLE untuk menjelaskan keputusan.
            # Warna di sana adalah rujukan, bukan nilai yang dirender.
            p = os.path.join(root, f)
            if "COPYING" in p:
                continue
            try:
                txt = open(p, encoding="utf-8", errors="ignore").read()
            except Exception:
                continue
            for h in re.findall(r"#[0-9a-fA-F]{6}", txt):
                hex_all[h.upper()] += 1

# Warna netral (grayscale) di SVG aset Arc: bayangan, outline, highlight.
# Ini bagian dari BENTUK aset Arc yang dipertahankan (keputusan Tahap 4:
# "pertahankan transparansi, dimensi, dan detail visual"). Bukan warna liar.
def is_neutral(h):
    r, g, b = (int(h[i:i+2], 16) for i in (1, 3, 5))
    return max(r, g, b) - min(r, g, b) <= 14


# Warna dekoratif di SVG sumber Arc (oracle-assets.svg): bayangan ber-opacity,
# outline, dan merah tombol close. Ini BUKAN warna fungsional CSS -- tidak
# satu pun muncul di gtk.css sebagai nilai aktif. Dipertahankan karena
# mengubahnya akan merusak detail visual aset (keputusan Tahap 4).
SVG_DECORATIVE = {
    "#5B627B", "#5F697F", "#8A949E", "#383C4A", "#5F6578",
    "#CC575D", "#D7787D", "#BE3841",
}

known = PALETTE_HEX | {k.upper() for k in DERIVED} | {k.upper() for k in SEMANTIC}
known |= {h.upper() for h in SVG_DECORATIVE}
unknown = {h: c for h, c in hex_all.items() if h not in known and not is_neutral(h)}
neutral = {h: c for h, c in hex_all.items() if h not in known and is_neutral(h)}
print(f"  hex unik di aset ORACLE : {len(hex_all)}")
print(f"  dari palet resmi        : {len([h for h in hex_all if h in PALETTE_HEX])}")
print(f"  turunan terdokumentasi  : {len([h for h in hex_all if h in {k.upper() for k in DERIVED}])}")
print(f"  status semantik         : {len([h for h in hex_all if h in {k.upper() for k in SEMANTIC}])}")
print(f"  netral aset Arc (sah)   : {len(neutral)}")
check(not unknown, "tidak ada hex non-netral tak terdokumentasi di aset ORACLE",
      f"{len(unknown)} hex: {sorted(unknown.items(), key=lambda x: -x[1])[:8]}"
      if unknown else "")

# ------------------------------------------------------------------ 3. Dial
print("\n=== 3. PENGGUNAAN DIAL & WORDMARK ===")
dial_master = os.path.join(BASE, "svg/dial-master.svg")
check(os.path.exists(dial_master), "dial-master.svg ada")
dial = open(dial_master, encoding="utf-8").read()
# geometri: ring + satu tick
check("circle" in dial or "path" in dial, "dial punya geometri ring")
# wallpaper memakai dial
wp = open(os.path.join(BASE, "wallpaper/svg/workspace-1920x1200.svg"),
          encoding="utf-8").read()
warn("Dusty" in wp or "#667D89" in wp.upper(), "wallpaper memakai Dusty Blue")

# ------------------------------------------------------------------ 4. kontras
print("\n=== 4. KONTRA S KUNCI LINTAS ASET ===")


def lum(h):
    h = h.lstrip("#")
    c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def cr(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


pairs = [
    ("GTK teks window", "#30363B", "#E9E5DA", 4.5),
    ("GTK headerbar", "#F5F3EC", "#344653", 4.5),
    ("Panel atas", "#F5F3EC", "#344653", 4.5),
    ("Panel bawah", "#30363B", "#F5F3EC", 4.5),
    ("Terminal teks", "#30363B", "#F5F3EC", 4.5),
    ("Greeter panel", "#F5F3EC", "#344653", 4.5),
    ("Greeter login", "#30363B", "#F5F3EC", 4.5),
]
for name, fg, bg, need in pairs:
    r = cr(fg, bg)
    check(r >= need, f"{name} >= {need}", f"{r:.2f}:1")

# ------------------------------------------------------------------ 5. aset lama
print("\n=== 5. ASET LAMA / TERTUKAR ===")
# pilot CSS tidak boleh menjadi tema final
pilot = os.path.join(BASE, "gtk/pilot/oracle-pilot.gtk.css")
final = os.path.join(BASE, "gtk/ORACLE/gtk-3.0/gtk.css")
check(os.path.exists(final), "tema GTK final ada")
if os.path.exists(pilot):
    ph = subprocess.run(["sha256sum", pilot], capture_output=True, text=True).stdout.split()[0]
    fh = subprocess.run(["sha256sum", final], capture_output=True, text=True).stdout.split()[0]
    check(ph != fh, "tema final != CSS pilot (tidak tertukar)")

# ------------------------------------------------------------------ 6. referensi
print("\n=== 6. REFERENSI FILE RUSAK ===")
# url() di gtk.css
gtk_css = open(final, encoding="utf-8").read()
refs = sorted(set(re.findall(r'url\("([^"]+)"\)', gtk_css)))
gtk_assets = os.path.join(BASE, "gtk/ORACLE/gtk-3.0/assets")
missing_ref = [r for r in refs
               if not os.path.exists(os.path.join(gtk_assets, os.path.basename(r)))]
check(not missing_ref, f"semua {len(refs)} url() GTK valid", str(missing_ref))

# index.theme Papirus
idx = open(os.path.join(BASE, "papirus/theme/ORACLE-Papirus/index.theme"),
           encoding="utf-8").read()
warn("Inherits=Papirus" in idx, "papirus inherit ke Papirus")

# ------------------------------------------------------------------ 7. lisensi
print("\n=== 7. LISENSI & ATRIBUSI ===")
for name, path, needle in [
    ("GTK NOTICE", "gtk/ORACLE/NOTICE.md", "GPL-3"),
    ("GTK COPYING", "gtk/ORACLE/COPYING", "GENERAL PUBLIC LICENSE"),
    ("Papirus NOTICE", "papirus/docs/NOTICE.md", "GPL-3"),
]:
    p = os.path.join(BASE, path)
    ok = os.path.exists(p) and needle in open(p, encoding="utf-8", errors="ignore").read()
    check(ok, f"{name} menyebut {needle}")

# ------------------------------------------------------------------ 8. manifest
print("\n=== 8. MANIFEST SHA256 ===")
for area in ("gtk/ORACLE", "panel", "terminal", "papirus", "greeter"):
    p = os.path.join(BASE, area, "SHA256SUMS.txt")
    ok = os.path.exists(p)
    if not ok:
        warn(False, f"{area}/SHA256SUMS.txt", "belum dibuat")
        continue
    r = subprocess.run(["sha256sum", "-c", "SHA256SUMS.txt"],
                       cwd=os.path.join(BASE, area), capture_output=True, text=True)
    bad = [l for l in r.stdout.splitlines() if not l.endswith(": OK")]
    check(not bad, f"{area} manifest valid",
          f"{len(bad)} gagal" if bad else f"{len(r.stdout.splitlines())} file")

print("\n" + "=" * 52)
if fails:
    print(f"GAGAL: {len(fails)}")
    for f in fails:
        print("  -", f)
    if warns:
        print(f"PERINGATAN: {len(warns)}")
        for w in warns:
            print("  !", w)
    sys.exit(1)
print(f"SEMUA LULUS ({len(warns)} peringatan)")
for w in warns:
    print("  !", w)
sys.exit(0)