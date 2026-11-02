#!/usr/bin/env python3
"""ORACLE-OS — Stage 2F-A: preview grid + validator Papirus.

Preview: grid ikon di atas latar terang (Porcelain), label jelas.
Validator: exit != 0 bila ada satu pun pemeriksaan gagal.
"""

import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_papirus as GP  # noqa: E402

ROOT = GP.ROOT
THEME = GP.THEME
PREV = GP.PREV

fails = []


def check(cond, label, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {label}" + (f"  {detail}" if detail else ""))
    if not cond:
        fails.append(label)


# ---------------------------------------------------------------- 1. struktur
print("=== 1. STRUKTUR TEMA ===")
check(os.path.isdir(THEME), "direktori tema ada", THEME)
check(os.path.exists(os.path.join(THEME, "index.theme")), "index.theme ada")

idx = open(os.path.join(THEME, "index.theme"), encoding="utf-8").read()
check("Inherits=Papirus,hicolor" in idx, "Inherits=Papirus,hicolor",
      "fallback ke Papirus penuh, bukan hicolor saja")
check("Name=ORACLE-Papirus" in idx, "Name=ORACLE-Papirus")

# ---------------------------------------------------------------- 2. cakupan
print("\n=== 2. CAKUPAN IKON WAJIB ===")
missing = []
for name in GP.REQUIRED:
    hits = GP.find_icon(name)
    made = [r for r, _, _ in hits if os.path.exists(os.path.join(THEME, r))]
    if not made:
        missing.append(name)
check(not missing, f"semua {len(GP.REQUIRED)} ikon wajib ada di tema",
      f"hilang: {missing}" if missing else "")

# ---------------------------------------------------------------- 3. recolor
print("\n=== 3. RECOLOR ===")
ARC_BLUE = "#5294e2"
leftover = []
total_svg = 0
for root, _, files in os.walk(THEME):
    for f in files:
        if not f.endswith(".svg"):
            continue
        total_svg += 1
        p = os.path.join(root, f)
        txt = open(p, encoding="utf-8", errors="ignore").read()
        if ARC_BLUE in txt.lower():
            leftover.append(os.path.relpath(p, THEME))
check(not leftover, f"tidak ada biru Papirus tersisa di {total_svg} SVG",
      f"{len(leftover)} file: {leftover[:5]}" if leftover else "")

# tidak ada warna baru di luar palet + warna netral Papirus.
# PENGECUALIAN SAH: blok <style> ColorScheme-* pada ikon symbolic. Blok itu
# mendefinisikan warna untuk class yang dipakai `currentColor`; nilainya
# TIDAK dirender langsung dan memang harus dipertahankan agar symbolic tetap
# berfungsi. Warna di dalam blok <style> karena itu dilewati.
PALETTE_OK = {c.lower() for c in (GP.IVORY, GP.PORCELAIN, GP.STEEL, GP.DUSTY,
                                  GP.BRASS, GP.BRASS_INK, GP.GRAPHITE)}
MAPPED = {c.lower() for c in GP.ACCENT_MAP.values()}
MAPPED |= {c.lower() for c in GP.STATUS_MAP.values()}
wild = Counter()
style_skipped = 0
for root, _, files in os.walk(THEME):
    for f in files:
        if not f.endswith(".svg"):
            continue
        txt = open(os.path.join(root, f), encoding="utf-8", errors="ignore").read()
        # buang blok <style>...</style> sebelum memindai
        stripped = re.sub(r"<style[^>]*>.*?</style>", "", txt, flags=re.S)
        if stripped != txt:
            style_skipped += 1
        for h in re.findall(r"#[0-9a-fA-F]{6}", stripped):
            h = h.lower()
            if h in PALETTE_OK or h in MAPPED:
                continue
            r, g, b = (int(h[i:i+2], 16) for i in (1, 3, 5))
            if max(r, g, b) - min(r, g, b) <= 12:
                continue
            wild[h] += 1
check(not wild, "tidak ada warna liar (non-netral) di luar palet",
      f"{dict(wild.most_common(6))}" if wild else
      f"({style_skipped} blok <style> symbolic dilewati)")

# ---------------------------------------------------------------- 4. preview
print("\n=== 4. PREVIEW ===")
for fn in ("icons-grid.png", "icons-xfce.png", "icons-folder.png"):
    p = os.path.join(PREV, fn)
    ok = os.path.exists(p) and os.path.getsize(p) > 3000
    check(ok, f"{fn} ada & >3 KB",
          f"{os.path.getsize(p)} B" if os.path.exists(p) else "hilang")

# ---------------------------------------------------------------- 5. manifest
print("\n=== 5. MANIFEST ===")
mp = os.path.join(ROOT, "manifest.txt")
check(os.path.exists(mp), "manifest.txt ada")
if os.path.exists(mp):
    mt = open(mp, encoding="utf-8").read()
    check("DIUBAH WARNA" in mt, "manifest mencatat ikon yang diubah")
    check("TIDAK DITEMUKAN" not in mt, "tidak ada blocker di manifest")

# ---------------------------------------------------------------- 6. lisensi
print("\n=== 6. LISENSI ===")
lic = os.path.join(ROOT, "docs", "NOTICE.md")
check(os.path.exists(lic), "NOTICE.md ada")
if os.path.exists(lic):
    lt = open(lic, encoding="utf-8").read()
    check("GPL-3" in lt, "menyebut GPL-3")
    check("Papirus" in lt, "menyebut Papirus upstream")

print("\n" + "=" * 52)
if fails:
    print(f"GAGAL: {len(fails)}")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("SEMUA LULUS")
sys.exit(0)