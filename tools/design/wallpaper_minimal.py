#!/usr/bin/env python3
"""
ORACLE-OS — Stage 2: Minimal Wallpaper (16:10).

Lebih tenang dari Workspace: TANPA motto. Satu-satunya elemen adalah Dial
watermark di lower band (kanan bawah), dengan latar Warm Ivory.

Sumber tunggal (TIDAK diduplikasi):
  - geometri Dial A1       -> tools/gen_assets.py (dial_geometry, ring_arc_path)
  - angka zona aman       -> tools/wallpaper_workspace.py (Z_*/BOTTOM_GAP_PX)
    (gate check_zones lokal mem-parse SVG sendiri, pakai konstanta itu)

Jangan mengubah wallpaper_workspace.py maupun gen_assets.py.
"""

import hashlib
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_assets import dial_geometry, ring_arc_path  # geometri A1
# Satu sumber ANGKA zona aman (Workspace dikunci; konstanta saja yang diimpor).
from wallpaper_workspace import BOTTOM_GAP_PX, Z_BOTTOM_PX, Z_ICON_PX, Z_TOP_PX

# --------------------------------------------------------------- palet
IVORY = "#E9E5DA"
DUSTY = "#667D89"

# ------------------------------------------------------- komposisi
# Dial duduk di lower band: pusat vertikal pada LOWER_BAND_Y x H (bawah-tengah
# kanvas), tepi kanan sejajar margin Workspace (konsisten antar dua wallpaper).
M_RIGHT = 0.048
LOWER_BAND_Y = 0.68
DIAL_D = 0.19             # diameter / lebar kanvas (lebih kecil dari Workspace
                          # 0.46 -> lebih tenang, sesuai konsep Minimal)
DIAL_OPACITY = 0.18

RESOLUTIONS = ((1920, 1200), (1280, 800))


def f(v):
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0"


def build_svg(W, H):
    D = DIAL_D * W
    cx = W * (1 - M_RIGHT) - D / 2.0
    cy = H * LOWER_BAND_Y
    g = dial_geometry("master", D, cx, cy)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <title>ORACLE-OS — Minimal wallpaper {W}x{H}</title>
  <!-- background -->
  <rect x="0" y="0" width="{W}" height="{H}" fill="{IVORY}"/>
  <!-- Dial watermark: geometri A1, Dusty Blue, opacity {DIAL_OPACITY}; satu-satunya elemen -->
  <g opacity="{DIAL_OPACITY}">
    <path d="{ring_arc_path(g)}" fill="none" stroke="{DUSTY}" stroke-width="{f(g['stroke'])}" stroke-linecap="butt"/>
    <rect x="{f(g['tick_x'])}" y="{f(g['tick_y'])}" width="{f(g['tick_w'])}" height="{f(g['tick_h'])}" fill="{DUSTY}"/>
  </g>
</svg>
"""


def check_zones(s, W, H):
    """Gate fail-closed: hitung bbox seni dari SVG (string) dan tolak kalau
    menabrak zona UI. Angka zona diimpor dari wallpaper_workspace (satu
    sumber), isi SVG di-parse sendiri."""
    rects = [(float(a), float(b), float(c), float(d))
             for a, b, c, d in re.findall(
                 r'<rect x="([\d.-]+)" y="([\d.-]+)" width="([\d.]+)" height="([\d.]+)" fill="#[0-9A-Fa-f]{6}"', s)]
    tick = rects[1]           # rect kedua = tick Dial (pertama background)
    m = re.search(r'A ([\d.]+) [\d.]+ 0 [01] 1', s)
    r = float(m.group(1))
    sw = float(re.search(r'stroke-width="([\d.]+)"', s).group(1))
    D = 2 * (r + sw / 2)

    cx = tick[0] + tick[2] / 2
    ring_top = tick[1] + 0.0543 * D
    cy = ring_top + r

    left, right = cx - r - sw / 2, cx + r + sw / 2
    top, bottom = tick[1], cy + r + sw / 2

    problems = []
    if left < Z_ICON_PX:
        problems.append(f"menabrak kolom ikon kiri (x={left:.0f} < {Z_ICON_PX})")
    if top < Z_TOP_PX:
        problems.append(f"menabrak top panel (y={top:.0f} < {Z_TOP_PX})")
    if bottom > H - Z_BOTTOM_PX:
        problems.append(f"menabrak bottom panel (y={bottom:.0f} > {H-Z_BOTTOM_PX})")
    if right > W:
        problems.append(f"terpotong kanan (x={right:.0f} > {W})")
    if bottom > H:
        problems.append(f"terpotong bawah (y={bottom:.0f} > {H})")
    return dict(D=D, box=(left, top, right, bottom), problems=problems)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    svg_dir = os.path.join(here, "wallpaper", "svg")
    png_dir = os.path.join(here, "wallpaper", "png")
    os.makedirs(svg_dir, exist_ok=True)
    os.makedirs(png_dir, exist_ok=True)

    for W, H in RESOLUTIONS:
        zone = check_zones(build_svg(W, H), W, H)
        if zone["problems"]:
            print(f"FATAL {W}x{H}: zona UI dilanggar ->", file=sys.stderr)
            for p in zone["problems"]:
                print(f"  - {p}", file=sys.stderr)
            sys.exit(1)

        svg_path = os.path.join(svg_dir, f"minimal-{W}x{H}.svg")
        with open(svg_path, "w", encoding="utf-8") as fh:
            fh.write(build_svg(W, H))

        png_path = os.path.join(png_dir, f"minimal-{W}x{H}.png")
        subprocess.run(
            ["rsvg-convert", "-w", str(W), "-h", str(H),
             "-o", png_path, svg_path],
            check=True, capture_output=True)

        print(f"\n{W}x{H}")
        for p in (svg_path, png_path):
            print(f"  {os.path.relpath(p, here):40} "
                  f"{os.path.getsize(p):8d} B  sha256={sha256(p)[:16]}")


if __name__ == "__main__":
    main()