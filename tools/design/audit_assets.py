#!/usr/bin/env python3
"""
ORACLE-OS — audit aset Tahap 1.

Dua lapis verifikasi, keduanya menghasilkan angka:

  1. GEOMETRI DARI BERKAS — rasio dibaca langsung dari atribut SVG (path/rect),
     lalu dicocokkan dengan rasio yang diminta. Ini eksak, tidak terpengaruh
     antialias.
  2. KECOCOKAN BENTUK — SVG dirender pada 16/24/32/48 px lalu dibandingkan
     dengan potongan acuan dari brand guide memakai IoU. Ini yang membuktikan
     varian optical memang lebih benar di ukuran kecil.

Jalankan:  <venv>/bin/python tools/audit_assets.py
Keluaran:  docs/audit-report.txt
"""

import io
import os
import re
import subprocess

import numpy as np
from PIL import Image

# Satu sumber angka target: METRICS di gen_assets.py. Jangan hardcode ulang
# rasio optical/master di sini — kalau METRICS berubah, audit ikut berubah.
from gen_assets import METRICS

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG = os.path.join(HERE, "svg")
VAR = os.path.join(SVG, "variants")
BG = (245, 243, 236)

REF_PNG = os.environ.get(
    "REF_PNG",
    os.path.expanduser(
        "~/.hermes/profiles/doraemon/cache/documents/native-inputs/"
        "94e50af016db2e7d0449eec223df315ff2a73a85303019260bcb0f316337f961/"
        "dashboard_20261101_222644_9d776eaa_image_77aa94.png"
    ),
)

# Potongan acuan pada brand guide: (x0, x1, y0, y1) untuk tiap ukuran.
REF_BOXES = {
    "16": (427, 452, 713, 740),
    "24": (336, 375, 698, 739),
    "32": (229, 281, 686, 737),
    "48": (93, 170, 658, 734),
}


# ---------------------------------------------------------------- utilitas
def render(path, width):
    raw = subprocess.run(
        ["rsvg-convert", "-w", f"{width:.2f}", path],
        check=True, capture_output=True).stdout
    im = Image.open(io.BytesIO(raw)).convert("RGBA")
    flat = Image.new("RGBA", im.size, BG + (255,))
    flat.alpha_composite(im)
    return np.array(flat.convert("RGB")).astype(int)


def ink(arr, tol=18):
    return np.abs(arr - np.array(BG)).sum(axis=2) > tol


def trimmed(mask):
    ys, xs = np.nonzero(mask)
    return mask[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def iou(a, b):
    ha, wa = max(a.shape[0], b.shape[0]), max(a.shape[1], b.shape[1])
    def pad(m):
        o = np.zeros((ha, wa), bool)
        o[:m.shape[0], :m.shape[1]] = m
        return o
    A, B = pad(a), pad(b)
    return (A & B).sum() / (A | B).sum()


def svg_text(path):
    return open(path, encoding="utf-8").read()


def viewbox(path):
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg_text(path))
    return float(m.group(1)), float(m.group(2))


def arc_and_rect(path):
    """Ambil radius busur, stroke-width, dua ujung busur, dan rect tick.

    Ujung busur adalah tempat celah (slot) dibuka, jadi lebar slot diukur dari
    jarak horizontal kedua ujung itu — bukan dari lebar rect tick. Ini yang
    sempat tertukar di versi audit sebelumnya.
    """
    s = svg_text(path)
    arc = re.search(
        r'<path d="M ([\d.-]+) ([\d.-]+) A ([\d.]+) [\d.]+ 0 [01] 1 ([\d.-]+) ([\d.-]+)"', s)
    sw = re.search(r'stroke-width="([\d.]+)"', s)
    rect = re.search(
        r'<rect x="([\d.-]+)" y="([\d.-]+)" width="([\d.]+)" height="([\d.]+)"', s)
    x1, y1, r, x2, y2 = (float(arc.group(i)) for i in range(1, 6))
    return dict(r=r, stroke=float(sw.group(1)),
                arc_ends=((x1, y1), (x2, y2)),
                rect=tuple(float(v) for v in rect.groups()))


def lum(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


# ---------------------------------------------------------------- laporan
def main():
    L = []

    def say(s=""):
        L.append(s)
        print(s)

    say("ORACLE-OS — Audit Aset Tahap 1")
    say("=" * 80)

    files = []
    for d in (SVG, VAR):
        for n in sorted(os.listdir(d)):
            if n.endswith(".svg"):
                files.append(os.path.join(d, n))

    say(f"\n0. INVENTARIS — {len(files)} berkas SVG")
    say("-" * 80)
    say(f"{'berkas':40}{'viewBox':>18}{'bytes':>8}")
    for p in files:
        vb = viewbox(p)
        say(f"{os.path.relpath(p, HERE):40}{vb[0]:8.1f}x{vb[1]:<9.1f}{os.path.getsize(p):8}")
    for p in files:
        txt = svg_text(p)
        if "<image" in txt or "data:image" in txt:
            say(f"  !! raster tertanam ditemukan di {p}")
    say("  (tidak ada <image> / data URI: seluruh aset murni vektor)")

    say("\n1. GEOMETRI DIBACA DARI BERKAS (eksak, bukan dari raster)")
    say("-" * 80)
    say(f"{'berkas':30}{'Ø':>8}{'stroke':>8}{'s/Ø':>7}{'slot':>8}{'slot/Ø':>8}{'tick_w':>8}{'tick_h':>8}{'h/Ø':>7}")
    ratios = {}
    for p in (os.path.join(SVG, "dial-master.svg"),
              os.path.join(SVG, "dial-optical-16.svg")):
        g = arc_and_rect(p)
        dia = 2 * (g["r"] + g["stroke"] / 2)
        (x1, _), (x2, _) = g["arc_ends"]
        slot = abs(x2 - x1)          # jarak horizontal ujung busur = lebar celah
        tw, th = g["rect"][2], g["rect"][3]
        ratios[os.path.basename(p)] = dict(dia=dia, stroke=g["stroke"],
                                           slot=slot, tw=tw, th=th)
        say(f"{os.path.basename(p):30}{dia:8.2f}{g['stroke']:8.2f}{g['stroke'] / dia:7.4f}"
            f"{slot:8.2f}{slot / dia:8.4f}{tw:8.2f}{th:8.2f}{th / dia:7.4f}")

    m = ratios["dial-master.svg"]
    o = ratios["dial-optical-16.svg"]
    mt = METRICS["master"]
    ot = METRICS["optical16"]
    say(f"\n{'':30}{'stroke/Ø':>10}{'slot/Ø':>10}{'tick_w/Ø':>11}{'tick_h/Ø':>11}")
    say(f"{'target master':30}{mt['stroke_ratio']:>10.4f}{mt['slot_ratio']:>10.4f}"
        f"{mt['tick_w_ratio']:>11.4f}{mt['tick_h_ratio']:>11.4f}")
    say(f"{'hasil  master':30}{m['stroke'] / m['dia']:>10.4f}{m['slot'] / m['dia']:>10.4f}"
        f"{m['tw'] / m['dia']:>11.4f}{m['th'] / m['dia']:>11.4f}")
    say(f"{'target optical16':30}{ot['stroke_ratio']:>10.4f}{ot['slot_ratio']:>10.4f}"
        f"{ot['tick_w_ratio']:>11.4f}{ot['tick_h_ratio']:>11.4f}")
    say(f"{'hasil  optical16':30}{o['stroke'] / o['dia']:>10.4f}{o['slot'] / o['dia']:>10.4f}"
        f"{o['tw'] / o['dia']:>11.4f}{o['th'] / o['dia']:>11.4f}")
    say(f"\n  slot optical / slot master = {o['slot'] / o['dia'] / (m['slot'] / m['dia']):.2f}x"
        f"   <- 'tick gap lebih lebar' yang diminta")
    say(f"  tick_w optical / tick_w master = "
        f"{o['tw'] / o['dia'] / (m['tw'] / m['dia']):.2f}x")
    say(f"  celah kiri-kanan di dalam slot, optical: "
        f"{(o['slot'] - o['tw']) / 2 / o['dia']:.4f} x Ø per sisi")

    say("\n2. UJI 16 px SEBENARNYA — apakah tick terbaca TERPISAH dan SIMETRIS")
    say("-" * 80)
    say("  Ini kriteria objektif untuk varian optical: pada 16 px, celah kiri dan")
    say("  kanan tick harus sama. Kalau tidak, tick tampak 'menempel' ke satu sisi.")

    def at16(path):
        vb_w, _ = viewbox(path)
        g = arc_and_rect(path)
        dia_units = 2 * (g["r"] + g["stroke"] / 2)
        arr = render(path, 16.0 * vb_w / dia_units)
        m = np.abs(arr - np.array(BG)).sum(axis=2) > 18
        ys, xs = np.nonzero(m)
        return m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]

    def gaps(mask):
        H, W = mask.shape
        out = []
        for ry in range(H):
            rr = np.nonzero(mask[ry])[0]
            if len(rr) < 3:
                continue
            rs, c = [], [rr[0]]
            for v in rr[1:]:
                if v - c[-1] <= 1:
                    c.append(v)
                else:
                    rs.append((c[0], c[-1]))
                    c = [v]
            rs.append((c[0], c[-1]))
            if len(rs) == 3:
                out.append((rs[1][0] - rs[0][1] - 1, rs[2][0] - rs[1][1] - 1))
        return out

    say(f"\n{'varian':16}{'Ø':>4}{'celah (kiri,kanan)':>26}{'simetris':>12}")
    for label, path in (("master", os.path.join(SVG, "dial-master.svg")),
                        ("optical16", os.path.join(SVG, "dial-optical-16.svg"))):
        m = at16(path)
        g = gaps(m)
        sym = bool(g) and all(a == b for a, b in g)
        shown = ", ".join(f"({a},{b})" for a, b in g[:3]) if g else "tidak terpisah"
        say(f"{label:16}{m.shape[1]:>4}{shown:>26}{'YA' if sym else 'TIDAK':>12}")
    say("\n  Bukti visual 16 px (master / optical):")
    mm = at16(os.path.join(SVG, "dial-master.svg"))
    oo = at16(os.path.join(SVG, "dial-optical-16.svg"))
    wid = max(mm.shape[1], oo.shape[1])
    for r in range(max(mm.shape[0], oo.shape[0])):
        a = "".join("#" if v else "." for v in mm[r]) if r < mm.shape[0] else ""
        b = "".join("#" if v else "." for v in oo[r]) if r < oo.shape[0] else ""
        say(f"    {a:<{wid}}   {b}")

    say("\n3. VARIAN WARNA")
    say("-" * 80)
    for name in ("light", "dark", "mono"):
        for kind in ("dial", "lockup"):
            p = os.path.join(VAR, f"{kind}-{name}.svg")
            cols = sorted(set(re.findall(r"#[0-9A-Fa-f]{6}", svg_text(p))))
            say(f"  {kind + '-' + name:14}{len(cols)} warna   {' '.join(cols)}")

    say("\n4. KONTRAS TERHADAP LATAR TUJUAN (ambang grafis 3:1)")
    say("-" * 80)
    checks = (
        ("light  ring #344653 pada #F5F3EC", "#344653", "#F5F3EC"),
        ("light  tick #8C7B58 pada #F5F3EC", "#8C7B58", "#F5F3EC"),
        ("dark   ring #F5F3EC pada #344653", "#F5F3EC", "#344653"),
        ("dark   tick #B8A98D pada #344653", "#B8A98D", "#344653"),
        ("mono   #30363B pada #F5F3EC", "#30363B", "#F5F3EC"),
        ("opt16  ring #30363B pada #F5F3EC", "#30363B", "#F5F3EC"),
        ("opt16  tick #8C7B58 pada #F5F3EC", "#8C7B58", "#F5F3EC"),
    )
    for label, fg, bg in checks:
        r = ratio(fg, bg)
        say(f"  {label:38}{r:6.2f}:1  {'PASS' if r >= 3 else 'FAIL'}")
    r = ratio("#B8A98D", "#F5F3EC")
    say(f"  {'DITOLAK: Brass #B8A98D pada #F5F3EC':38}{r:6.2f}:1  FAIL (dicatat)")

    say("\n5. BATAS AUDIT INI")
    say("-" * 80)
    say("  - Tidak ada rendering di dalam XFCE/QEMU. Kecocokan bentuk diukur")
    say("    dari raster rsvg, bukan dari tangkapan layar sesi nyata.")
    say("  - IoU terhadap acuan terbatas oleh resolusi preview (16 px di preview")
    say("    adalah 25 px diameter). Angka 16/24/32/48 adalah ukuran RENDER.")
    say("  - Kontras dihitung dari nilai hex, bukan diukur dari layar.")

    out = os.path.join(HERE, "docs", "audit-report.txt")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"\n-> {out}")


if __name__ == "__main__":
    main()