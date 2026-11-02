#!/usr/bin/env python3
"""Validator Stage 2E — terminal ANSI 16-color.

Mengembalikan exit code != 0 bila ada satu pemeriksaan pun gagal.
Tidak ada pemeriksaan yang "dianggap lulus".
"""

import configparser
import hashlib
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_terminal as G  # noqa: E402

ROOT = G.ROOT
THEME = os.path.join(ROOT, "cfg", "oracle.theme")
RC = os.path.join(ROOT, "cfg", "terminalrc.fragment")
PREV = os.path.join(ROOT, "preview")

fails = []
warns = []


def check(cond, label, detail=""):
    if cond:
        print(f"  PASS  {label}" + (f"  {detail}" if detail else ""))
    else:
        print(f"  FAIL  {label}  {detail}")
        fails.append(label)


def warn(cond, label, detail=""):
    if cond:
        print(f"  PASS  {label}  {detail}")
    else:
        print(f"  WARN  {label}  {detail}")
        warns.append(label)


# ---------------------------------------------------------------- 1. theme
print("=== 1. FILE THEME ===")
check(os.path.exists(THEME), "oracle.theme ada")
txt = open(THEME, encoding="utf-8").read()

cp = configparser.ConfigParser()
cp.optionxform = str
try:
    cp.read_string(txt)
    check(True, "parse .theme")
except Exception as e:
    check(False, "parse .theme", str(e))
    sys.exit(1)

check("Scheme" in cp, "section [Scheme] ada")
s = cp["Scheme"]

# key dikenal (dari strings binary xfce4-terminal)
KNOWN = {
    "Name", "ColorForeground", "ColorBackground", "ColorCursor",
    "ColorCursorForeground", "ColorCursorUseDefault", "ColorSelection",
    "ColorSelectionBackground", "ColorSelectionUseDefault", "ColorBold",
    "ColorBoldUseDefault", "ColorBoldIsBright", "ColorUseTheme",
    "ColorBackgroundVary", "TabActivityColor", "ColorPalette",
}
unknown = [k for k in s.keys()
           if k not in KNOWN and not re.fullmatch(r"Name\[[a-zA-Z_]{2,5}\]", k)]
check(not unknown, "tidak ada key tak dikenal", str(unknown))

# ---------------------------------------------------------------- 2. palette
print("\n=== 2. COLORPALETTE ===")
pal = [p.strip() for p in s["ColorPalette"].split(";")]
check(len(pal) == 16, "tepat 16 entri", f"({len(pal)})")
badhex = [p for p in pal if not re.fullmatch(r"#[0-9A-Fa-f]{6}", p)]
check(not badhex, "semua hex valid", str(badhex))
check([p.upper() for p in pal] == [c.upper() for c in G.PALETTE],
      "cocok dengan generator PALETTE")
dup = len(pal) != len(set(p.upper() for p in pal))
check(not dup, "tidak ada warna duplikat")

# ---------------------------------------------------------------- 3. kontras
print("\n=== 3. KONTRAS ===")
BG = G.BG
check(G.contrast(G.FG, BG) >= 4.5, "fg/bg >= 4.5",
      f"{G.contrast(G.FG, BG):.2f}:1")

# semua slot yang berperan teks
TEXT_SLOTS = [0, 1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14]
worst = min((G.contrast(G.PALETTE[i], BG), i) for i in TEXT_SLOTS)
check(worst[0] >= 4.5, "semua slot teks >= 4.5",
      f"terendah slot {worst[1]} = {worst[0]:.2f}:1")

# bright harus beda dari normal
for n, b in [(1, 9), (2, 10), (3, 11), (4, 12), (5, 13), (6, 14)]:
    d = sum(abs(G.hex2rgb(G.PALETTE[n])[i] - G.hex2rgb(G.PALETTE[b])[i])
            for i in range(3))
    check(G.PALETTE[n].upper() != G.PALETTE[b].upper() and d >= 15,
          f"normal {n} != bright {b}", f"deltaRGB {d}")

# cursor & selection
check(G.contrast("#344653", BG) >= 3.0, "cursor vs latar >= 3",
      f"{G.contrast('#344653', BG):.2f}:1")
check(G.contrast("#F5F3EC", "#344653") >= 4.5, "teks cursor vs blok >= 4.5",
      f"{G.contrast('#F5F3EC', '#344653'):.2f}:1")
check(G.contrast("#F5F3EC", "#344653") >= 4.5, "selection >= 4.5")

# peran semantik
print("\n  -- peran semantik --")
sem = [("perintah", G.C_CMD), ("argumen", G.C_ARG), ("string", G.C_STR),
       ("angka", G.C_NUM), ("direktori", G.C_DIR), ("sukses", G.C_OK),
       ("warning", G.C_WARN), ("error", G.C_ERR), ("dim", G.C_DIM),
       ("key", G.C_KEY)]
for name, col in sem:
    r = G.contrast(col, BG)
    check(r >= 4.5, f"semantik {name} >= 4.5", f"{col} {r:.2f}:1")

# ---------------------------------------------------------------- 4. semantic unik
print("\n=== 4. PERAN SEMANTIK TERBEDAKAN ===")
# error != warning, sukses != error
check(G.C_ERR != G.C_WARN, "error != warning",
      f"{G.C_ERR} vs {G.C_WARN}")
check(G.C_OK != G.C_ERR, "sukses != error")
check(G.C_DIR != G.C_ERR, "direktori != error")

# ---------------------------------------------------------------- 5. rc fragment
print("\n=== 5. TERMINALRC FRAGMENT ===")
check(os.path.exists(RC), "terminalrc.fragment ada")
rc = open(RC, encoding="utf-8").read()
check("[Configuration]" in rc, "punya [Configuration]")
check("FontName=JetBrains Mono 11" in rc, "FontName JetBrains Mono 11")
check("BackgroundMode=TERMINAL_BACKGROUND_SOLID" in rc, "background solid")
check("MiscCursorBlinks=FALSE" in rc, "cursor tidak berkedip")
# palette di rc harus sama dengan theme
m = re.search(r"^ColorPalette=(.+)$", rc, re.M)
check(m is not None, "rc punya ColorPalette")
if m:
    check(m.group(1).split(";") == pal, "rc palette == theme palette")
# warna di rc harus konsisten dgn theme
for key in ("ColorForeground", "ColorBackground", "ColorCursor",
            "ColorBold", "ColorSelection", "TabActivityColor"):
    mv = re.search(rf"^{key}=(.+)$", rc, re.M)
    check(mv is not None and mv.group(1).strip() == s.get(key, "").strip(),
          f"rc {key} == theme",
          f"{mv.group(1) if mv else '-'} vs {s.get(key,'-')}")

# ---------------------------------------------------------------- 6. preview
print("\n=== 6. PREVIEW ===")
expected = {"terminal-main.png": 5000, "terminal-syntax.png": 5000,
            "terminal-palette-inline.png": 5000, "palette-sheet.png": 5000,
            "semantic-sheet.png": 5000, "spec.txt": 300}
for fn, minsize in expected.items():
    p = os.path.join(PREV, fn)
    ok = os.path.exists(p) and os.path.getsize(p) >= minsize
    check(ok, f"{fn} ada & >= {minsize} B",
          f"{os.path.getsize(p)} B" if os.path.exists(p) else "hilang")

# semua 16 slot harus benar-benar muncul di preview konteks
try:
    from PIL import Image
    import collections as _c
    p = os.path.join(PREV, "terminal-palette-inline.png")
    im = Image.open(p).convert("RGB")
    cnt = _c.Counter(im.get_flattened_data() if hasattr(im, "get_flattened_data")
                     else list(im.getdata()))
    present = [i for i, col in enumerate(G.PALETTE)
               if cnt.get(G.hex2rgb(col), 0) > 0]
    check(len(present) == 16, "16 slot muncul di preview inline",
          f"{len(present)}/16, hilang: {[i for i in range(16) if i not in present]}")
except Exception as e:
    check(False, "cek slot di preview inline", str(e))

# ---------------------------------------------------------------- 7. determinisme
print("\n=== 7. DETERMINISME ===")
h_before = hashlib.sha256(open(THEME, "rb").read()).hexdigest()
subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__),
                                             "gen_terminal.py")],
               capture_output=True, check=True)
h_after = hashlib.sha256(open(THEME, "rb").read()).hexdigest()
check(h_before == h_after, "regenerasi menghasilkan theme identik",
      h_after[:16])

# ---------------------------------------------------------------- hasil
print("\n" + "=" * 52)
if fails:
    print(f"GAGAL: {len(fails)} pemeriksaan")
    for f in fails:
        print(f"  - {f}")
    sys.exit(1)
print(f"SEMUA LULUS ({len(warns)} peringatan)")
if warns:
    for w in warns:
        print(f"  ! {w}")
sys.exit(0)