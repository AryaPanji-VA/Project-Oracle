#!/usr/bin/env python3
"""ORACLE-OS — Stage 2F-A: render preview grid ikon.

Merender SVG nyata dari tema ORACLE-Papirus memakai rsvg-convert,
lalu menyusunnya jadi grid di atas latar Porcelain.
"""

import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_papirus as GP  # noqa: E402

THEME = GP.THEME
PREV = GP.PREV
TMP = os.path.expanduser("~/.hermes/profiles/doraemon/cache/scratch/oracle-design/pap-tmp")
os.makedirs(TMP, exist_ok=True)
os.makedirs(PREV, exist_ok=True)

FONT_DIR = os.path.expanduser(
    "~/.hermes/profiles/doraemon/cache/scratch/oracle-design/deb/inter/usr/share/fonts/opentype/inter")


def ui(size, bold=False):
    for p in ([os.path.join(FONT_DIR, "Inter-SemiBold.otf"),
               os.path.join(FONT_DIR, "Inter-Bold.otf")] if bold else
              [os.path.join(FONT_DIR, "Inter-Regular.otf")]):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def render(svg_path, size=48):
    """Render SVG ke PNG transparan, kembalikan PIL image."""
    out = os.path.join(TMP, f"{abs(hash((svg_path, size)))}.png")
    r = subprocess.run(
        ["rsvg-convert", "-w", str(size), "-h", str(size),
         "-o", out, svg_path],
        capture_output=True)
    if r.returncode != 0 or not os.path.exists(out):
        return None
    return Image.open(out).convert("RGBA")


def pick(name, size="48x48"):
    """Ambil SVG ukuran tertentu untuk nama ikon.

    PENTING: default 48x48, bukan 16x16. Ikon 16x16 Papirus adalah symbolic
    (currentColor) sehingga terender abu-abu dan tidak menunjukkan hasil
    recolor. Ukuran 22px+ yang berwarna.
    """
    hits = GP.find_icon(name)
    for rel, src, is_sym in hits:
        if rel.startswith(size + "/") and src.endswith(".svg") and not is_sym:
            p = os.path.join(THEME, rel)
            if os.path.exists(p):
                return p
    # fallback: ukuran berwarna terbesar yang ada
    for want in ("64x64", "48x48", "32x32", "24x24", "22x22"):
        for rel, src, is_sym in hits:
            if rel.startswith(want + "/") and src.endswith(".svg") and not is_sym:
                p = os.path.join(THEME, rel)
                if os.path.exists(p):
                    return p
    # terakhir: apa pun yang ada
    for rel, src, is_sym in hits:
        p = os.path.join(THEME, rel)
        if os.path.exists(p) and p.endswith(".svg"):
            return p
    return None


def grid(items, out_path, title, subtitle, cols=8, cell=104, icon=56):
    rows = (len(items) + cols - 1) // cols
    W = cols * cell + 40
    H = 86 + rows * (cell + 22) + 34
    img = Image.new("RGB", (W, H), GP.PORCELAIN)
    d = ImageDraw.Draw(img)

    d.text((20, 16), "MOCKUP STATIS", font=ui(13, bold=True), fill=GP.STEEL)
    d.text((20, 34), title, font=ui(11, bold=True), fill=GP.STEEL)
    d.text((20, 50), subtitle, font=ui(8), fill=GP.DUSTY)

    f = ui(7)
    for i, (name, path) in enumerate(items):
        r_, c_ = divmod(i, cols)
        cx = 20 + c_ * cell
        cy = 78 + r_ * (cell + 22)
        # kotak tile
        d.rounded_rectangle([cx, cy, cx + cell - 8, cy + cell - 8],
                            radius=4, fill=GP.IVORY, outline="#D6D7D4")
        if path:
            im = render(path, icon)
            if im:
                px = cx + (cell - 8 - icon) // 2
                py = cy + (cell - 8 - icon) // 2
                img.paste(im, (px, py), im)
            else:
                d.text((cx + 12, cy + 24), "?", font=ui(20, bold=True), fill=GP.DUSTY)
        else:
            d.text((cx + 12, cy + 24), "—", font=ui(16), fill=GP.DUSTY)
        # label
        label = name if len(name) <= 20 else name[:19] + "…"
        tw = d.textlength(label, font=f)
        d.text((cx + (cell - 8 - tw) / 2, cy + cell - 20), label, font=f, fill=GP.GRAPHITE)

    d.text((20, H - 16),
           "ikon dirender dari tema ORACLE-Papirus · latar Soft Porcelain #F5F3EC",
           font=ui(7), fill=GP.DUSTY)
    img.save(out_path)
    print(f"wrote {out_path} {img.size}")


def main():
    # 1) ikon XFCE (yang wajib)
    xfce_names = [n for n in GP.REQUIRED if n.startswith(("org.xfce", "xfsm", "application-x"))]
    grid([(n, pick(n)) for n in xfce_names],
         os.path.join(PREV, "icons-xfce.png"),
         "Ikon aplikasi & pengaturan XFCE",
         "dipakai .desktop di image · semua dari Papirus penuh, aksen di-recolor")

    # 2) folder & places
    place_names = [n for n in GP.REQUIRED if n in (
        "folder", "folder-home", "user-home", "user-desktop", "user-trash")]
    grid([(n, pick(n)) for n in place_names],
         os.path.join(PREV, "icons-folder.png"),
         "Folder & places",
         "aksen folder dipetakan ke Steel Blue")

    # 3) grid lengkap
    grid([(n, pick(n)) for n in GP.REQUIRED],
         os.path.join(PREV, "icons-grid.png"),
         "Semua ikon ORACLE-Papirus",
         f"{len(GP.REQUIRED)} ikon wajib · dirender dari SVG nyata",
         cols=7, cell=112, icon=60)


if __name__ == "__main__":
    main()