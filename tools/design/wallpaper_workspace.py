#!/usr/bin/env python3
"""
ORACLE-OS — Stage 2: Workspace Wallpaper (16:10).

GEOMETRI TIDAK DIDUPLIKASI. Dial diambil langsung dari fungsi geometri di
tools/gen_assets.py (sumber A1 yang sudah approved), jadi rasio ring/slot/tick
dijamin identik dengan aset terkunci.

Komposisi (semua proporsional terhadap W/H, jadi identik di 1920x1200 dan
1280x800):
  - latar Warm Ivory
  - Dial watermark Dusty Blue, opacity 18%, kanan bawah
  - motto "Work with clarity." kanan atas, sejajar garis kanan Dial
  - kolom ikon desktop kiri, top panel, bottom panel: dibiarkan kosong

Palet: hanya #E9E5DA, #667D89, #344653. Tidak ada warna sistem baru.
"""

import hashlib
import os
import re
import subprocess
import sys

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_assets import FONT_DIR, dial_geometry, ring_arc_path  # geometri A1

# ------------------------------------------------------------------ palet
IVORY = "#E9E5DA"
DUSTY = "#667D89"
STEEL = "#344653"

# ------------------------------------------------------- zona UI (Px NYATA)
# Panel XFCE punya tinggi piksel yang sama di 1280x800 maupun 1920x1200,
# jadi zona aman harus dalam px KONSTAN, bukan fraksi. Nilai:
#   TOP    = panel atas XFCE (~28px @1x) + margin -> 72
#   BOTTOM = panel bawah centered (~48px @1x) + margin -> 104
#   ICON   = kolom ikon desktop kiri -> 168
Z_TOP_PX = 72
Z_BOTTOM_PX = 104
Z_ICON_PX = 168

# ------------------------------------------------------- tata letak seni
M_RIGHT = 0.048          # margin kanan (dipakai Dial DAN motto -> satu garis)
BOTTOM_GAP_PX = 16       # celah ekstra di bawah Dial, di luar zona panel
DIAL_D = 0.46            # diameter Dial / lebar kanvas
MOTTO_TOP = 0.100        # top cap motto / tinggi kanvas
MOTTO_CAP = 0.021        # cap height motto / tinggi kanvas
DIAL_OPACITY = 0.18

MOTTO = "Work with clarity."
MOTTO_WEIGHT = "Inter-Medium"
MOTTO_TRACK_EM = 0.01


def f(v):
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0"


def text_outline(text, weight, cap_height):
    """Outline glyph -> daftar (x_offset, path_d), bbox, skala.

    Mengembalikan koordinat yang SUDAH siap untuk SVG (y tumbuh ke bawah),
    memakai skala vertikal negatif seperti pada wordmark A3.
    """
    font = TTFont(os.path.join(FONT_DIR, f"{weight}.otf"))
    upm = font["head"].unitsPerEm
    glyphset = font.getGlyphSet()
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]

    from fontTools.pens.boundsPen import BoundsPen

    track = (MOTTO_TRACK_EM * upm) if text != MOTTO else (MOTTO_TRACK_EM * upm)

    placed, x = [], 0.0
    minx = miny = 1e9
    maxx = maxy = -1e9
    for ch in text:
        g = cmap[ord(ch)]
        pen = SVGPathPen(glyphset)
        glyphset[g].draw(pen)
        d = pen.getCommands()
        if d:
            placed.append((x, d))
        bp = BoundsPen(glyphset)
        glyphset[g].draw(bp)
        if bp.bounds:
            bx0, by0, bx1, by1 = bp.bounds
            minx, maxx = min(minx, bx0 + x), max(maxx, bx1 + x)
            miny, maxy = min(miny, by0), max(maxy, by1)
        x += hmtx[g][0] + track

    scale = cap_height / (maxy - miny)
    return placed, (minx, miny, maxx, maxy), scale


def build_svg(W, H):
    # --- Dial: geometri A1, ukuran dibatasi agar muat di zona aman
    D = max_dial_diameter(W, H)
    cx = W * (1 - M_RIGHT) - D / 2.0
    cy = H - Z_BOTTOM_PX - BOTTOM_GAP_PX - D / 2.0
    g = dial_geometry("master", D, cx, cy)

    # --- Motto: rata kanan pada garis yang sama dengan tepi kanan Dial
    cap = MOTTO_CAP * H
    placed, (minx, miny, maxx, maxy), scale = text_outline(
        MOTTO, MOTTO_WEIGHT, cap)
    motto_right = W * (1 - M_RIGHT)
    motto_w = (maxx - minx) * scale
    x0 = motto_right - motto_w
    baseline = MOTTO_TOP * H + cap

    glyphs = "\n".join(
        f'      <path transform="translate({f(x0 + (xoff - minx) * scale)} '
        f'{f(baseline)}) scale({f(scale)} {f(-scale)})" d="{d}"/>'
        for xoff, d in placed
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <title>ORACLE-OS — Workspace wallpaper {W}x{H}</title>
  <!-- background -->
  <rect x="0" y="0" width="{W}" height="{H}" fill="{IVORY}"/>
  <!-- Dial watermark: geometri A1, Dusty Blue, opacity {DIAL_OPACITY} -->
  <g opacity="{DIAL_OPACITY}">
    <path d="{ring_arc_path(g)}" fill="none" stroke="{DUSTY}" stroke-width="{f(g['stroke'])}" stroke-linecap="butt"/>
    <rect x="{f(g['tick_x'])}" y="{f(g['tick_y'])}" width="{f(g['tick_w'])}" height="{f(g['tick_h'])}" fill="{DUSTY}"/>
  </g>
  <!-- motto -->
  <g fill="{STEEL}">
{glyphs}
  </g>
</svg>
"""


RESOLUTIONS = ((1920, 1200), (1280, 800))

# Rasio protrude tick master (dari METRICS A1, bukan hardcode lokal)
_PROTRUDE_RATIO = None


def max_dial_diameter(W, H):
    """Batas diameter Dial agar muat di antara zona top dan bottom, plus
    tidak menabrak kolom ikon kiri. Komposisi tetap proporsional; di layar
    pendek (1280x800) Dial otomatis mengecil."""
    global _PROTRUDE_RATIO
    if _PROTRUDE_RATIO is None:
        from gen_assets import METRICS
        _PROTRUDE_RATIO = METRICS["master"]["protrude_ratio"]
    vertical = (H - Z_TOP_PX - Z_BOTTOM_PX - BOTTOM_GAP_PX) / (1 + _PROTRUDE_RATIO)
    horizontal = W * (1 - M_RIGHT) - Z_ICON_PX
    return min(DIAL_D * W, vertical, horizontal)


def check_zones(W, H):
    """Hitung bbox seni dan tolak (fail-closed) kalau menabrak zona UI."""
    s = build_svg(W, H)
    rects = [(float(a), float(b), float(c), float(d))
             for a, b, c, d in re.findall(
                 r'<rect x="([\d.-]+)" y="([\d.-]+)" width="([\d.]+)" height="([\d.]+)" fill="#[0-9A-Fa-f]{6}"', s)]
    tick = rects[1]
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
        problems.append(f"Dial menabrak kolom ikon kiri (x={left:.0f} < {Z_ICON_PX})")
    if top < Z_TOP_PX:
        problems.append(f"Dial menabrak top panel (y={top:.0f} < {Z_TOP_PX})")
    if bottom > H - Z_BOTTOM_PX:
        problems.append(f"Dial menabrak bottom panel (y={bottom:.0f} > {H-Z_BOTTOM_PX})")
    if right > W:
        problems.append(f"Dial terpotong kanan (x={right:.0f} > {W})")
    if bottom > H:
        problems.append(f"Dial terpotong bawah (y={bottom:.0f} > {H})")
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

    manifest = []
    for W, H in RESOLUTIONS:
        zone = check_zones(W, H)
        if zone["problems"]:
            print(f"FATAL {W}x{H}: zona UI dilanggar ->", file=sys.stderr)
            for p in zone["problems"]:
                print(f"  - {p}", file=sys.stderr)
            sys.exit(1)

        svg_path = os.path.join(svg_dir, f"workspace-{W}x{H}.svg")
        with open(svg_path, "w", encoding="utf-8") as fh:
            fh.write(build_svg(W, H))

        png_path = os.path.join(png_dir, f"workspace-{W}x{H}.png")
        subprocess.run(
            ["rsvg-convert", "-w", str(W), "-h", str(H),
             "-o", png_path, svg_path],
            check=True, capture_output=True)

        manifest.append((svg_path, png_path, W, H))

    for svg_path, png_path, W, H in manifest:
        print(f"\n{W}x{H}")
        for p in (svg_path, png_path):
            print(f"  {os.path.relpath(p, here):40} "
                  f"{os.path.getsize(p):8d} B  sha256={sha256(p)[:16]}")
    return manifest


if __name__ == "__main__":
    main()
