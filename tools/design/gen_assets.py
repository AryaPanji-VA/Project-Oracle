#!/usr/bin/env python3
"""
ORACLE-OS — brand asset generator (Tahap 1)

Menghasilkan Dial mark, wordmark, dan lockup sebagai SVG. Geometri DITURUNKAN
dari pengukuran preview (docs/DESIGN-ASSETS.md), bukan dikira-kira.

Konstruksi mark (hasil pengukuran, bukan asumsi):
  - ring digambar sebagai SATU busur terbuka; celah (slot) di 12 o'clock
  - tick adalah bar yang duduk di celah itu, menonjol ke ATAS melewati tepi luar
    ring, dan turun melewati tepi dalam sampai masuk ke lubang ring
  - di ukuran kecil tick menonjol KURANG dari satu piksel, jadi secara visual
    tick menyatu dengan puncak ring (bukan mengambang di atasnya)

Jalankan:  <venv>/bin/python tools/gen_assets.py [outdir]
"""

import math
import os
import sys

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

# --------------------------------------------------------------------------
# Rasio terukur, dinormalisasi ke diameter ring (Ø)
# --------------------------------------------------------------------------
METRICS = {
    # master — dari lockup besar: Ø=92, stroke 11.5, slot 16, tick 10x36, protrude 5
    "master": {
        "stroke_ratio": 11.5 / 92.0,     # 0.1250
        "slot_ratio": 16 / 92.0,         # 0.1739
        "tick_w_ratio": 10 / 92.0,       # 0.1087
        "tick_h_ratio": 36 / 92.0,       # 0.3913
        "protrude_ratio": 5 / 92.0,      # 0.0543
    },
    # optical 16 px — diukur dan diuji pada render 16 px yang sebenarnya.
    # Kriteria yang dipakai bukan selera, melainkan: celah kiri dan kanan tick
    # harus SAMA di 16 px (simetris). Master gagal di sini (2 px vs 1 px),
    # karena tick-nya 0.109 x Ø sehingga jatuh di batas piksel.
    # slot 0.28 + tick 0.115 -> celah 2 px di kedua sisi pada Ø17.
    "optical16": {
        "stroke_ratio": 0.1250,
        "slot_ratio": 0.2800,
        "tick_w_ratio": 0.1150,
        "tick_h_ratio": 0.4100,
        "protrude_ratio": 0.0770,
    },
}

PALETTE = {
    "ivory": "#E9E5DA",
    "porcelain": "#F5F3EC",
    "steel": "#344653",
    "dusty": "#667D89",
    "brass": "#B8A98D",
    "graphite": "#30363B",
    "brass_ink": "#8C7B58",
}

FONT_DIR = os.environ.get(
    "INTER_DIR",
    os.path.expanduser(
        "~/.hermes/profiles/doraemon/cache/scratch/oracle-design/deb/"
        "inter/usr/share/fonts/opentype/inter"
    ),
)

WEIGHT = "Inter-SemiBold"
TRACK_EM = 16 / 64.0          # tracking terukur 16 px pada size 64 px
GAP_RATIO = 42 / 92.0         # jarak mark -> wordmark / Ø
CAP_RATIO = 47 / 92.0         # cap height / Ø


def f(v):
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0"


# --------------------------------------------------------------------------
# Dial
# --------------------------------------------------------------------------


def dial_geometry(kind, diameter, cx, cy):
    m = METRICS[kind]
    r_out = diameter / 2.0
    stroke = m["stroke_ratio"] * diameter
    r_in = r_out - stroke

    # SLOT = lebar celah pada busur ring. Tick adalah bar terpisah di dalamnya,
    # jadi slot HARUS lebih lebar dari tick (sisakan celah kiri-kanan).
    slot_w = m["slot_ratio"] * diameter
    r_mid = (r_out + r_in) / 2.0
    slot_half_deg = math.degrees(math.asin(min(1.0, (slot_w / 2.0) / r_mid)))

    tick_w = m["tick_w_ratio"] * diameter
    tick_h = m["tick_h_ratio"] * diameter
    protrude = m["protrude_ratio"] * diameter

    y_top = cy - r_out - protrude
    return dict(
        r_out=r_out,
        r_in=r_in,
        stroke=stroke,
        slot_w=slot_w,
        slot_half_deg=slot_half_deg,
        tick_w=tick_w,
        tick_h=tick_h,
        protrude=protrude,
        cx=cx,
        cy=cy,
        tick_x=cx - tick_w / 2.0,
        tick_y=y_top,
        # bbox ink: tick menentukan puncak, ring menentukan sisi & dasar
        top=y_top,
        bottom=cy + r_out,
        left=cx - r_out,
        right=cx + r_out,
    )


def ring_arc_path(g):
    """Satu busur hampir penuh, celah di puncak (12 o'clock)."""
    cx, cy = g["cx"], g["cy"]
    r = (g["r_out"] + g["r_in"]) / 2.0
    half = g["slot_half_deg"]
    a0 = -90 + half
    sweep = 360 - 2 * half

    def pt(deg):
        rad = math.radians(deg)
        return cx + r * math.cos(rad), cy + r * math.sin(rad)

    x0, y0 = pt(a0)
    x1, y1 = pt(a0 + sweep)
    large = 1 if sweep > 180 else 0
    return f"M {f(x0)} {f(y0)} A {f(r)} {f(r)} 0 {large} 1 {f(x1)} {f(y1)}"


def dial_svg(kind="master", ring_color=None, tick_color=None,
             diameter=460.0, pad=8.0, title="ORACLE Dial"):
    """Kanvas dihitung dari bbox ink, jadi tick tidak pernah terpotong."""
    preview = dial_geometry(kind, diameter, 0, 0)
    vb_x = preview["left"] - pad
    vb_y = preview["top"] - pad
    w = (preview["right"] - preview["left"]) + 2 * pad
    h = (preview["bottom"] - preview["top"]) + 2 * pad

    g = dial_geometry(kind, diameter, -vb_x, -vb_y)
    ring_color = ring_color or PALETTE["steel"]
    tick_color = tick_color or PALETTE["brass"]
    m = METRICS[kind]

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{f(w)}" height="{f(h)}" viewBox="0 0 {f(w)} {f(h)}" role="img" aria-label="{title}">
  <title>{title}</title>
  <!-- Dial {kind}: Ø {f(diameter)} | stroke/Ø {m['stroke_ratio']:.4f} | slot/Ø {m['slot_ratio']:.4f} -->
  <path d="{ring_arc_path(g)}" fill="none" stroke="{ring_color}" stroke-width="{f(g['stroke'])}" stroke-linecap="butt"/>
  <rect x="{f(g['tick_x'])}" y="{f(g['tick_y'])}" width="{f(g['tick_w'])}" height="{f(g['tick_h'])}" fill="{tick_color}"/>
</svg>
"""


# --------------------------------------------------------------------------
# Wordmark (outline asli, bukan <text>)
# --------------------------------------------------------------------------


def wordmark_outline(text="ORACLE", font_path=None):
    font_path = font_path or os.path.join(FONT_DIR, f"{WEIGHT}.otf")
    font = TTFont(font_path)
    upm = font["head"].unitsPerEm
    glyphset = font.getGlyphSet()
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    track_units = TRACK_EM * upm

    paths, x = [], 0.0
    minx = miny = 1e9
    maxx = maxy = -1e9
    for ch in text:
        gname = cmap[ord(ch)]
        pen = SVGPathPen(glyphset)
        glyphset[gname].draw(pen)
        d = pen.getCommands()
        if d:
            paths.append((x, d))
        bp = BoundsPen(glyphset)
        glyphset[gname].draw(bp)
        if bp.bounds:
            bx0, by0, bx1, by1 = bp.bounds
            minx, maxx = min(minx, bx0 + x), max(maxx, bx1 + x)
            miny, maxy = min(miny, by0), max(maxy, by1)
        x += hmtx[gname][0] + track_units
    return paths, (minx, miny, maxx, maxy), upm


def wordmark_svg(color=None, cap_height=119.0, title="ORACLE wordmark"):
    paths, (minx, miny, maxx, maxy), _ = wordmark_outline()
    color = color or PALETTE["steel"]
    scale = cap_height / (maxy - miny)
    w = (maxx - minx) * scale
    h = cap_height

    body = "\n".join(
        f'    <path transform="translate({f((xoff - minx) * scale)} {f(maxy * scale)}) '
        f'scale({f(scale)} {f(-scale)})" d="{d}"/>'
        for xoff, d in paths
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{f(w)}" height="{f(h)}" viewBox="0 0 {f(w)} {f(h)}" role="img" aria-label="{title}">
  <title>{title}</title>
  <!-- {WEIGHT} di-outline | cap height {f(cap_height)} | tracking {TRACK_EM:.4f} em -->
  <g fill="{color}">
{body}
  </g>
</svg>
"""


# --------------------------------------------------------------------------
# Lockup horizontal
# --------------------------------------------------------------------------


def lockup_svg(kind="master", ring_color=None, tick_color=None, word_color=None,
               diameter=460.0, pad=8.0, title="ORACLE lockup", mono=False):
    ring_color = ring_color or PALETTE["steel"]
    tick_color = tick_color or PALETTE["brass"]
    word_color = word_color or PALETTE["steel"]
    # Monokrom sejati: tick TIDAK terlihat berbeda. Tick tetap digambar supaya
    # bentuk slot tidak "menutup" secara visual, tetapi warnanya sama dengan
    # ring — jadi hasilnya satu tinta, bukan dua tinta yang kebetulan mirip.
    tick_fill = ring_color if mono else tick_color

    g_probe = dial_geometry(kind, diameter, 0, 0)
    r_out = g_probe["r_out"]
    protrude = g_probe["protrude"]
    cap = CAP_RATIO * diameter
    gap = GAP_RATIO * diameter

    paths, (minx, miny, maxx, maxy), _ = wordmark_outline()
    scale = cap / (maxy - miny)
    wm_w = (maxx - minx) * scale

    # Satu kerangka: semua koordinat dalam viewBox.
    # Mark: kiri = pad, kanan = pad + Ø; tick menonjol setinggi protrude di atas.
    mark_x0 = pad
    ring_cx = pad + r_out
    ring_cy = pad + r_out + protrude        # tick top = pad
    wm_x0 = pad + 2 * r_out + gap           # teks mulai setelah mark + gap
    cap_top = ring_cy - cap / 2.0           # tepi atas huruf sejajar pusat ring
    baseline_y = cap_top + cap

    vb_w = wm_x0 + wm_w + pad
    vb_h = ring_cy + r_out + pad            # dasar ring + pad

    g = dial_geometry(kind, diameter, ring_cx, ring_cy)

    body = "\n".join(
        f'    <path transform="translate({f(wm_x0 + (xoff - minx) * scale)} '
        f'{f(baseline_y)}) scale({f(scale)} {f(-scale)})" d="{d}"/>'
        for xoff, d in paths
    )
    m = METRICS[kind]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{f(vb_w)}" height="{f(vb_h)}" viewBox="0 0 {f(vb_w)} {f(vb_h)}" role="img" aria-label="{title}">
  <title>{title}</title>
  <!-- lockup {kind}: Ø {f(diameter)} | gap/Ø {GAP_RATIO:.4f} | cap/Ø {CAP_RATIO:.4f} -->
  <path d="{ring_arc_path(g)}" fill="none" stroke="{ring_color}" stroke-width="{f(g['stroke'])}" stroke-linecap="butt"/>
  <rect x="{f(g['tick_x'])}" y="{f(g['tick_y'])}" width="{f(g['tick_w'])}" height="{f(g['tick_h'])}" fill="{tick_fill}"/>
  <g fill="{word_color}">
{body}
  </g>
</svg>
"""


def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_root = sys.argv[1] if len(sys.argv) > 1 else here
    svg_dir = os.path.join(out_root, "svg")
    var_dir = os.path.join(svg_dir, "variants")
    os.makedirs(var_dir, exist_ok=True)

    made = []

    def w(path, content):
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
        made.append(path)

    # A1 / A2 / A3 / A4
    w(os.path.join(svg_dir, "dial-master.svg"), dial_svg("master"))
    w(os.path.join(svg_dir, "dial-optical-16.svg"),
      dial_svg("optical16", PALETTE["graphite"], PALETTE["brass_ink"],
               title="ORACLE Dial — optical 16px"))
    w(os.path.join(svg_dir, "wordmark.svg"), wordmark_svg())
    w(os.path.join(svg_dir, "lockup-horizontal.svg"), lockup_svg("master"))

    # A5 — light / dark / monochrome
    #
    # Aturan tick: Muted Brass HANYA sah di atas bidang gelap (4.24:1 vs
    # Steel Blue). Di atas bidang terang ia 1.83:1 — gagal — jadi varian light
    # memakai Brass Ink sebagai tick dan Muted Brass dicadangkan untuk versi
    # besar dekoratif. Ini konsekuensi angka, bukan selera.
    for name, ring, tick, word in (
        ("light", PALETTE["steel"], PALETTE["brass_ink"], PALETTE["steel"]),
        ("dark", PALETTE["porcelain"], PALETTE["brass"], PALETTE["porcelain"]),
        ("mono", PALETTE["graphite"], PALETTE["graphite"], PALETTE["graphite"]),
    ):
        mono = name == "mono"
        w(os.path.join(var_dir, f"lockup-{name}.svg"),
          lockup_svg("master", ring, tick, word, title=f"ORACLE lockup — {name}", mono=mono))
        w(os.path.join(var_dir, f"dial-{name}.svg"),
          dial_svg("master", ring, tick if not mono else ring,
                   title=f"ORACLE Dial — {name}"))

    for p in made:
        print(f"  {os.path.relpath(p, out_root):42} {os.path.getsize(p):6d} B")
    print(f"\n{len(made)} file SVG ditulis ke {out_root}")

    # --- preview PNG: mark pada 16/24/32/48 px, plus scale-up pembanding ----
    preview_dir = os.path.join(out_root, "preview")
    os.makedirs(preview_dir, exist_ok=True)
    import subprocess
    import re
    for kind, svg_name in (("master", "dial-master.svg"),
                           ("optical16", "dial-optical-16.svg")):
        path = os.path.join(svg_dir, svg_name)
        src = open(path, encoding="utf-8").read()
        vb_w = float(re.search(r'viewBox="0 0 ([\d.]+)', src).group(1))
        ring_units = 460.0
        for target in (16, 24, 32, 48):
            # lebar render dipilih agar DIAMETER RING == target px
            width = target * vb_w / ring_units
            out = os.path.join(preview_dir, f"dial-{kind}-{target}px.png")
            subprocess.run(["rsvg-convert", "-w", f"{width:.2f}", path, "-o", out],
                           check=True, capture_output=True)
            print(f"  {os.path.relpath(out, out_root):42} Ø {target}px")
    print(f"\npreview PNG di {preview_dir}")


if __name__ == "__main__":
    main()
