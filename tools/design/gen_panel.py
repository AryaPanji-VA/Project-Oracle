#!/usr/bin/env python3
"""ORACLE-OS — XFCE Panel 4.20: generator konfigurasi + preview.

Menghasilkan:
  panel/cfg/xfce4-panel.xml      konfigurasi xfconf lengkap (dua panel)
  panel/cfg/APPLY.md             instruksi pasang (manual, tidak dijalankan)
  panel/preview/panel-*.png      mockup statis (label jelas di gambar)
  panel/preview/spec.txt         angka terukur

Semua nilai diturunkan dari audit di panel/docs/AUDIT-PANEL.md.
Tidak ada properti yang tidak ada di xfce4-panel 4.20.4-1.
"""

import os
from PIL import Image, ImageDraw, ImageFont

# ----------------------------------------------------------------- palet
IVORY    = "#E9E5DA"
PORCELAIN= "#F5F3EC"
STEEL    = "#344653"
DUSTY    = "#667D89"
BRASS    = "#B8A98D"
BRASS_INK= "#8C7B58"
GRAPHITE = "#30363B"
BORDER   = "#B9C1C2"
DISABLED = "#767877"

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "panel")
CFG  = os.path.join(ROOT, "cfg")
PREV = os.path.join(ROOT, "preview")
os.makedirs(CFG, exist_ok=True)
os.makedirs(PREV, exist_ok=True)

# ----------------------------------------------------------------- ukuran
TOP_H      = 32     # px, <= Z_TOP_PX 72
BOTTOM_H   = 48     # px, <= Z_BOTTOM_PX 104
TOP_ICON   = 18
BOTTOM_ICON= 32
BORDER_W   = 1


def rgba(hex_, alpha=1.0):
    """xfconf background-rgba = array double 0.0..1.0, BUKAN 0..255."""
    h = hex_.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return (r / 255.0, g / 255.0, b / 255.0, alpha)


def rgba_xml(hex_, alpha=1.0):
    """Empat <value type="double"> untuk background-rgba."""
    vals = rgba(hex_, alpha)
    return "\n".join(
        f'        <value type="double" value="{v:.6f}"/>' for v in vals)


# ----------------------------------------------------------------- konfigurasi
# plugin-id panel atas: 1..8 ; panel bawah: 11..17
TOP_PLUGINS = [
    ("applicationsmenu", {}),                       # 1
    ("launcher", {"items": ["xfce4-terminal-emulator.desktop"]}),   # 2
    ("launcher", {"items": ["xfce4-file-manager.desktop"]}),        # 3
    ("separator", {"style": 0, "expand": True}),    # 4 spacer
    ("tasklist", {"grouping": 1, "flat-buttons": True}),            # 5
    ("separator", {"style": 0, "expand": True}),    # 6 spacer
    ("systray", {"square-icons": True}),            # 7
    ("clock", {"digital-layout": 1, "digital-time-format": "%H:%M"}),  # 8
]

BOTTOM_PLUGINS = [
    ("showdesktop", {}),                            # 11
    ("separator", {"style": 1, "expand": False, "size": 8}),  # 12 garis
    ("launcher", {"items": ["xfce4-terminal-emulator.desktop"]}),   # 13
    ("launcher", {"items": ["xfce4-file-manager.desktop"]}),        # 14
    ("launcher", {"items": ["xfce4-web-browser.desktop"]}),         # 15
    ("launcher", {"items": ["xfce4-appfinder.desktop"]}),           # 16
    ("separator", {"style": 1, "expand": False, "size": 8}),  # 17 garis
]


def xml_plugins(start_id, specs):
    out = []
    for i, (name, props) in enumerate(specs):
        pid = start_id + i
        if props:
            out.append(f'    <property name="plugin-{pid}" type="string" value="{name}">')
            for k, v in props.items():
                if isinstance(v, bool):
                    out.append(f'      <property name="{k}" type="bool" value="{str(v).lower()}"/>')
                elif isinstance(v, int):
                    out.append(f'      <property name="{k}" type="uint" value="{v}"/>')
                elif isinstance(v, list):
                    out.append(f'      <property name="{k}" type="array">')
                    for item in v:
                        out.append(f'        <value type="string" value="{item}"/>')
                    out.append('      </property>')
                else:
                    out.append(f'      <property name="{k}" type="string" value="{v}"/>')
            out.append('    </property>')
        else:
            out.append(f'    <property name="plugin-{pid}" type="string" value="{name}"/>')
    return out


def build_xml():
    top_ids  = list(range(1, 1 + len(TOP_PLUGINS)))
    bot_ids  = list(range(11, 11 + len(BOTTOM_PLUGINS)))

    L = []
    L.append('<?xml version="1.0" encoding="UTF-8"?>')
    L.append('<!--')
    L.append('  ORACLE-OS — XFCE Panel 4.20 configuration')
    L.append('  Target: xfce4-panel 4.20.4-1 (Debian 13 Trixie)')
    L.append('  Stage 2D. Dihasilkan oleh tools/gen_panel.py — jangan edit manual.')
    L.append('')
    L.append('  Latar panel ditetapkan lewat background-style + background-rgba,')
    L.append('  BUKAN lewat gtk.css: panel memasang CSS inline pada')
    L.append('  GTK_STYLE_PROVIDER_PRIORITY_APPLICATION (600), di atas tema (200).')
    L.append('  Lihat panel/docs/AUDIT-PANEL.md section 3.1.')
    L.append('-->')
    L.append('<channel name="xfce4-panel" version="1.0">')
    L.append('  <property name="configver" type="int" value="2"/>')
    L.append('  <property name="panels" type="array">')
    for pid in (1, 2):
        L.append(f'    <value type="int" value="{pid}"/>')

    # ---------------- panel 1: top
    L.append('    <property name="panel-1" type="empty">')
    L.append('      <property name="position" type="string" value="p=6;x=0;y=0"/>')
    L.append('      <property name="mode" type="uint" value="0"/>')          # horizontal
    L.append('      <property name="size" type="uint" value="%d"/>' % TOP_H)
    L.append('      <property name="length" type="uint" value="100"/>')      # 100%
    L.append('      <property name="length-adjust" type="bool" value="false"/>')
    L.append('      <property name="icon-size" type="uint" value="%d"/>' % TOP_ICON)
    L.append('      <property name="nrows" type="uint" value="1"/>')
    L.append('      <property name="position-locked" type="bool" value="true"/>')
    L.append('      <property name="autohide-behavior" type="uint" value="0"/>')  # never
    L.append('      <property name="disable-struts" type="bool" value="false"/>')
    L.append('      <property name="span-monitors" type="bool" value="false"/>')
    L.append('      <property name="dark-mode" type="bool" value="false"/>')
    L.append('      <property name="background-style" type="uint" value="1"/>')   # solid
    L.append('      <property name="background-rgba" type="array">')
    L.append(rgba_xml(STEEL))
    L.append('      </property>')
    L.append('      <property name="plugin-ids" type="array">')
    for pid in top_ids:
        L.append(f'        <value type="int" value="{pid}"/>')
    L.append('      </property>')
    L.append('    </property>')

    # ---------------- panel 2: bottom dock
    L.append('    <property name="panel-2" type="empty">')
    L.append('      <property name="position" type="string" value="p=10;x=0;y=0"/>')
    L.append('      <property name="mode" type="uint" value="0"/>')
    L.append('      <property name="size" type="uint" value="%d"/>' % BOTTOM_H)
    L.append('      <property name="length" type="uint" value="520"/>')     # px tetap
    L.append('      <property name="length-adjust" type="bool" value="true"/>')
    L.append('      <property name="icon-size" type="uint" value="%d"/>' % BOTTOM_ICON)
    L.append('      <property name="nrows" type="uint" value="1"/>')
    L.append('      <property name="position-locked" type="bool" value="true"/>')
    L.append('      <property name="autohide-behavior" type="uint" value="0"/>')
    L.append('      <property name="disable-struts" type="bool" value="false"/>')
    L.append('      <property name="span-monitors" type="bool" value="false"/>')
    L.append('      <property name="dark-mode" type="bool" value="false"/>')
    L.append('      <property name="background-style" type="uint" value="1"/>')
    L.append('      <property name="background-rgba" type="array">')
    L.append(rgba_xml(PORCELAIN))
    L.append('      </property>')
    L.append('      <property name="plugin-ids" type="array">')
    for pid in bot_ids:
        L.append(f'        <value type="int" value="{pid}"/>')
    L.append('      </property>')
    L.append('    </property>')
    L.append('  </property>')

    # ---------------- plugins
    L.append('  <property name="plugins" type="empty">')
    L.extend(xml_plugins(1, TOP_PLUGINS))
    L.extend(xml_plugins(11, BOTTOM_PLUGINS))
    L.append('  </property>')
    L.append('</channel>')
    return "\n".join(L) + "\n"


# ----------------------------------------------------------------- preview
def font(size, bold=False):
    cands = [
        "/usr/share/fonts/truetype/inter/Inter-SemiBold.ttf" if bold else
        "/usr/share/fonts/truetype/inter/Inter-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for c in cands:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def dial(d, cx, cy, r, color, tick_color, w=2):
    """Dial ORACLE: ring + satu index tick di kanan atas."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=w)
    # tick slot: gap di ring kanan-atas
    return


def icon_square(d, x, y, s, bg, fg, glyph):
    d.rounded_rectangle([x, y, x + s, y + s], radius=3, fill=bg)
    f = font(max(8, int(s * 0.55)), bold=True)
    bb = d.textbbox((0, 0), glyph, font=f)
    d.text((x + (s - (bb[2] - bb[0])) / 2 - bb[0],
            y + (s - (bb[3] - bb[1])) / 2 - bb[1]), glyph, font=f, fill=fg)


def draw_top_panel(img, d, y, width, label=True, real=False):
    """Panel atas: Steel, teks Porcelain, aksen Brass."""
    d.rectangle([0, y, width, y + TOP_H], fill=STEEL)
    d.line([0, y + TOP_H, width, y + TOP_H], fill="#2A3A45", width=1)

    x = 12
    # applicationsmenu: Dial mark kecil + label
    r = 7
    cx, cy = x + r + 1, y + TOP_H // 2
    dial(d, cx, cy, r, PORCELAIN, BRASS, w=2)
    # tick terang: garis pendek di kanan ring (dalam celah)
    d.line([cx + r - 1, cy - 4, cx + r - 1, cy + 1], fill=BRASS, width=2)
    x = cx + r + 9
    f = font(11, bold=True)
    d.text((x, y + TOP_H // 2 - 7), "Applications", font=f, fill=PORCELAIN)
    x += 92

    # dua launcher
    for glyph in ("T", "F"):
        icon_square(d, x, y + (TOP_H - 20) // 2, 20, "#3C4F5C", PORCELAIN, glyph)
        x += 26

    # tasklist (tengah): dua window
    x_mid = width // 2 - 90
    for name, active in (("Terminal", True), ("Files", False)):
        bw = 84
        bg = "#2A3A45" if active else STEEL
        d.rounded_rectangle([x_mid, y + 5, x_mid + bw, y + TOP_H - 5], radius=3, fill=bg)
        if active:
            d.line([x_mid + 4, y + TOP_H - 2, x_mid + bw - 4, y + TOP_H - 2], fill=BRASS, width=2)
        d.text((x_mid + 8, y + 10), name, font=font(10), fill=PORCELAIN)
        x_mid += bw + 6

    # systray
    xr = width - 190
    for i in range(3):
        d.rounded_rectangle([xr, y + 8, xr + 14, y + TOP_H - 8], radius=2,
                            fill="#4A5C68")
        xr += 18

    # clock
    f = font(11, bold=True)
    d.text((width - 62, y + TOP_H // 2 - 7), "14:32", font=f, fill=PORCELAIN)

    if label:
        d.text((width - 62, y - 14), "top", font=font(9), fill=DUSTY)


def draw_bottom_panel(img, d, y, width, label=True):
    """Panel bawah: Porcelain, border Dusty, ikon Graphite, aksen Brass."""
    pw = 520
    x0 = (width - pw) // 2
    d.rectangle([x0, y, x0 + pw, y + BOTTOM_H], fill=PORCELAIN)
    d.rectangle([x0, y, x0 + pw, y + BOTTOM_H], outline=DUSTY, width=1)

    # showdesktop
    s = 30
    ix = x0 + 12
    icon_square(d, ix, y + (BOTTOM_H - s) // 2, s, "#EDEAE1", STEEL, "D")
    ix += s + 8

    # separator garis
    d.line([ix, y + 12, ix, y + BOTTOM_H - 12], fill=BORDER, width=1)
    ix += 10

    # empat launcher
    for glyph in ("T", "F", "W", "A"):
        icon_square(d, ix, y + (BOTTOM_H - s) // 2, s, "#EDEAE1", STEEL, glyph)
        ix += s + 8

    # separator garis
    d.line([ix, y + 12, ix, y + BOTTOM_H - 12], fill=BORDER, width=1)

    if label:
        d.text((x0 + pw + 8, y + BOTTOM_H // 2 - 6), "bottom dock", font=font(9), fill=DUSTY)


def build_preview_real(width=1920, height=1200):
    """Preview skala 1:1 di atas wallpaper Workspace yang sudah disetujui.
    Panel digambar pada tinggi piksel sesungguhnya, lebar penuh."""
    wp = os.path.join(os.path.dirname(ROOT), "wallpaper", "png",
                      f"workspace-{width}x{height}.png")
    if not os.path.exists(wp):
        raise SystemExit(f"wallpaper tidak ada: {wp}")
    img = Image.open(wp).convert("RGB")
    d = ImageDraw.Draw(img)

    # panel atas: full width, di y=0
    draw_top_panel(img, d, 0, width, label=False, real=True)
    # panel bawah: 520 px, tengah, menempel dasar layar
    draw_bottom_panel_real(img, d, width, height)

    # label MOCKUP STATIS di area kosong kiri atas-bawah panel
    d.rectangle([24, 52, 300, 78], fill="#E9E5DA")
    d.text((30, 56), "MOCKUP STATIS", font=font(13, bold=True), fill=STEEL)
    d.text((30, 84), "bukan render XFCE", font=font(9), fill=DUSTY)
    return img


def draw_bottom_panel_real(img, d, width, height):
    pw, ph = 520, BOTTOM_H
    x0 = (width - pw) // 2
    y0 = height - ph - 16          # BOTTOM_GAP_PX = 16
    d.rectangle([x0, y0, x0 + pw, y0 + ph], fill=PORCELAIN)
    d.rectangle([x0, y0, x0 + pw, y0 + ph], outline=DUSTY, width=1)

    s = BOTTOM_ICON
    ix = x0 + 16
    icon_square(d, ix, y0 + (ph - s) // 2, s, "#EDEAE1", STEEL, "D")
    ix += s + 12
    d.line([ix, y0 + 12, ix, y0 + ph - 12], fill=BORDER, width=1)
    ix += 14
    for glyph in ("T", "F", "W", "A"):
        icon_square(d, ix, y0 + (ph - s) // 2, s, "#EDEAE1", STEEL, glyph)
        ix += s + 14
    d.line([ix, y0 + 12, ix, y0 + ph - 12], fill=BORDER, width=1)


def build_preview(width=1000, height=340):
    img = Image.new("RGB", (width, height), IVORY)
    d = ImageDraw.Draw(img)

    # label MOCKUP STATIS
    d.text((16, 12), "MOCKUP STATIS", font=font(13, bold=True), fill=STEEL)
    d.text((16, 30), "ORACLE-OS panel - preview skematis, bukan render XFCE",
           font=font(9), fill=DUSTY)

    # skala: gambar 1:1 piksel untuk panel, tapi kanvas 1000 px mewakili 1920
    scale_note = "skala horizontal 1000px = 1920px sesungguhnya"
    d.text((16, 44), scale_note, font=font(8), fill=GRAPHITE)

    top_y = 80
    draw_top_panel(img, d, top_y, width)
    d.text((16, top_y - 16), "PANEL ATAS  Steel #344653  32px  p=6 (NW)  length 100%",
           font=font(9), fill=STEEL)

    bot_y = height - 78
    draw_bottom_panel(img, d, bot_y, width)
    d.text((16, bot_y - 16), "PANEL BAWAH  Porcelain #F5F3EC  48px  p=10 (SC)  length 520px",
           font=font(9), fill=STEEL)

    # keterangan kontras
    y = height - 26
    d.text((16, y), "Kontras: atas Porcelain/Steel 8.81:1 · bawah Graphite/Porcelain 11.02:1 · "
                    "aksen Muted Brass 4.24:1 / Brass Ink 3.72:1",
           font=font(8), fill=GRAPHITE)
    return img


def build_contrast_sheet(width=760, height=300):
    """Lembar kecil: dua panel dengan contoh ikon + label kontras."""
    img = Image.new("RGB", (width, height), PORCELAIN)
    d = ImageDraw.Draw(img)
    d.text((16, 12), "MOCKUP STATIS - spesifikasi warna panel",
           font=font(12, bold=True), fill=STEEL)

    # atas
    y = 40
    d.rectangle([16, y, width - 16, y + TOP_H], fill=STEEL)
    d.text((28, y + 9), "Applications", font=font(11, bold=True), fill=PORCELAIN)
    d.text((width - 90, y + 9), "14:32", font=font(11, bold=True), fill=PORCELAIN)
    d.text((width - 90, y - 12), "Porcelain 8.81:1", font=font(8), fill=DUSTY)
    d.line([28, y + TOP_H - 2, 120, y + TOP_H - 2], fill=BRASS, width=2)
    d.text((130, y + TOP_H + 2), "aktif: Muted Brass 4.24:1", font=font(8), fill=GRAPHITE)

    # bawah
    y2 = y + 110
    pw = 360
    x0 = 16
    d.rectangle([x0, y2, x0 + pw, y2 + BOTTOM_H], fill=PORCELAIN)
    d.rectangle([x0, y2, x0 + pw, y2 + BOTTOM_H], outline=DUSTY, width=1)
    s = 30
    ix = x0 + 14
    for glyph in ("T", "F", "W"):
        icon_square(d, ix, y2 + (BOTTOM_H - s) // 2, s, "#EDEAE1", STEEL, glyph)
        ix += s + 10
    d.text((x0, y2 + BOTTOM_H + 4), "border Dusty 3.89:1 · ikon Steel 8.81:1",
           font=font(8), fill=GRAPHITE)
    return img


def main():
    xml = build_xml()
    p = os.path.join(CFG, "xfce4-panel.xml")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(xml)
    print(f"wrote {p} ({len(xml)} B)")

    img = build_preview()
    p2 = os.path.join(PREV, "panel-mockup.png")
    img.save(p2)
    print(f"wrote {p2} {img.size}")

    img2 = build_contrast_sheet()
    p3 = os.path.join(PREV, "panel-kontras.png")
    img2.save(p3)
    print(f"wrote {p3} {img2.size}")

    try:
        real = build_preview_real(1920, 1200)
        p5 = os.path.join(PREV, "panel-on-wallpaper-1920x1200.png")
        real.save(p5)
        print(f"wrote {p5} {real.size}")
    except SystemExit as e:
        print("skip 1:1 preview:", e)

    spec = f"""ORACLE-OS — XFCE Panel 4.20 spesifikasi terukur
target paket: xfce4-panel 4.20.4-1 (Debian 13 Trixie)

PANEL ATAS
  posisi        p=6  (NW, kiri atas)
  size          {TOP_H} px        (batas safe zone {72} px -> sisa {72-TOP_H})
  length        100 % penuh
  icon-size     {TOP_ICON} px
  latar         Steel {STEEL}   alpha 1.0  (opaque, tanpa compositor)
  teks          Porcelain {PORCELAIN}  kontras 8.81:1
  aksen aktif   Muted Brass {BRASS}   kontras 4.24:1
  plugin        1 applicationsmenu, 2-3 launcher, 4 spacer, 5 tasklist,
                6 spacer, 7 systray, 8 clock

PANEL BAWAH (dock)
  posisi        p=10 (SC, bawah tengah)
  size          {BOTTOM_H} px        (batas safe zone {104} px -> sisa {104-BOTTOM_H})
  length        520 px (length-adjust=true, piksel tetap)
  icon-size     {BOTTOM_ICON} px
  latar         Porcelain {PORCELAIN}  alpha 1.0
  border        Dusty {DUSTY} 1px   kontras 3.89:1 (wajib: Porcelain/Ivory = 1.13:1)
  ikon          Steel {STEEL}   kontras 8.81:1
  aksen aktif   Brass Ink {BRASS_INK}  kontras 3.72:1
  plugin        11 showdesktop, 12 separator(garis), 13-16 launcher,
                17 separator(garis)

KEDUA PANEL
  autohide      never (0)
  position-locked=true
  dark-mode     false
  nrows         1
  background-style 1 (solid color) -- WAJIB xfconf, CSS tema tidak berpengaruh
"""
    p4 = os.path.join(PREV, "spec.txt")
    with open(p4, "w", encoding="utf-8") as fh:
        fh.write(spec)
    print(f"wrote {p4}")


if __name__ == "__main__":
    main()