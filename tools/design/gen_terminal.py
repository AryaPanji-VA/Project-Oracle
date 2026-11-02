#!/usr/bin/env python3
"""ORACLE-OS — Stage 2E: terminal ANSI 16-color palette + preview.

Menghasilkan:
  terminal/cfg/oracle.theme            colorscheme xfce4-terminal
  terminal/cfg/terminalrc.fragment     potongan konfigurasi (font, cursor, dll)
  terminal/preview/terminal-*.png      mockup statis berlabel
  terminal/preview/palette-sheet.png   lembar 16 warna + kontras
  terminal/preview/spec.txt            angka terukur

Palette diturunkan, bukan dikarang:
  - slot 0,7,8,15 memakai warna ORACLE langsung (Graphite, Dusty, border, Ivory)
  - slot 1-6,9-14: hue ANSI standar, saturasi 0.50, lightness = nilai
    TERTINGGI yang masih lolos kontras >= 4.5:1 terhadap latar Porcelain
  - "bright" = saturasi +0.12..0.20 dan lightness -0.02 (lebih pekat,
    BUKAN lebih terang: di light theme bright yang lebih terang menghilang)

Target: xfce4-terminal 1.1.4-1 (Debian 13 Trixie), VTE 0.61.91+.
"""

import colorsys
import os
from PIL import Image, ImageDraw, ImageFont

# ------------------------------------------------------------------ palet
IVORY     = "#E9E5DA"
PORCELAIN = "#F5F3EC"
STEEL     = "#344653"
DUSTY     = "#667D89"
BRASS     = "#B8A98D"
BRASS_INK = "#8C7B58"
GRAPHITE  = "#30363B"
BORDER    = "#B9C1C2"

BG = PORCELAIN          # latar terminal
FG = GRAPHITE           # teks utama

# 16 slot ANSI — urutan baku: 0-7 normal, 8-15 bright
PALETTE = [
    GRAPHITE,    # 0  black          (brand)
    "#B4503C",   # 1  red
    "#317E2A",   # 2  green
    "#8A682E",   # 3  yellow         (hue Brass Ink 40.4°, delta 2.6°)
    "#3674A1",   # 4  blue           (hue Steel 205.2°, delta 0.1°)
    "#B83D99",   # 5  magenta
    "#2B7682",   # 6  cyan
    DUSTY,       # 7  white          (brand: Dusty Blue)
    BORDER,      # 8  bright black   (brand: border GTK)
    "#C33D22",   # 9  bright red
    "#26801E",   # 10 bright green
    "#90661E",   # 11 bright yellow
    "#1F72AE",   # 12 bright blue
    "#C8239F",   # 13 bright magenta
    "#1B7987",   # 14 bright cyan
    IVORY,       # 15 bright white   (brand: Warm Ivory)
]

SLOT_NAMES = [
    "black", "red", "green", "yellow", "blue", "magenta", "cyan", "white",
    "bright black", "bright red", "bright green", "bright yellow",
    "bright blue", "bright magenta", "bright cyan", "bright white",
]

# peran semantik untuk preview
C_CMD     = PALETTE[4]    # blue      — perintah
C_ARG     = PALETTE[0]    # black     — argumen
C_STR     = PALETTE[2]    # green     — string
C_NUM     = PALETTE[5]    # magenta   — angka
C_DIR     = PALETTE[4]    # blue      — direktori
C_OK      = PALETTE[2]    # green     — sukses
C_WARN    = PALETTE[3]    # yellow    — warning
C_ERR     = PALETTE[1]    # red       — error
C_KEY     = PALETTE[6]    # cyan      — key / branch
C_BRASS   = BRASS_INK     # aksen     — prompt tick

# Komentar/dim TIDAK memakai slot 7: Dusty asli hanya 3.89:1 di Porcelain,
# gagal ambang teks 4.5. Slot 7 tetap Dusty (peran "white"/UI, sesuai
# konvensi light scheme Debian). Untuk teks dim dipakai turunan Dusty
# dengan hue (200.6°) & saturasi (0.146) SAMA, lightness 0.469 -> 0.42.
# Dipilih L=0.42 (bukan 0.41/0.40) karena itu lightness TERTINGGI yang
# masih lolos 4.5:1 -> paling "dim" tapi tetap terbaca. Hasil 4.67:1.
C_DIM     = "#5B707B"

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "terminal")
CFG = os.path.join(ROOT, "cfg")
PREV = os.path.join(ROOT, "preview")
os.makedirs(CFG, exist_ok=True)
os.makedirs(PREV, exist_ok=True)

FONT_DIR = os.path.expanduser(
    "~/.hermes/profiles/doraemon/cache/scratch/oracle-design/deb/inter/usr/share/fonts/opentype/inter")
MONO_CANDIDATES = [
    "/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Regular.ttf",
    "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf",
]
MONO_BOLD_CANDIDATES = [
    "/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Bold.ttf",
    "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf",
]
UI_CANDIDATES = [
    os.path.join(FONT_DIR, "Inter-Regular.otf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]
UI_BOLD_CANDIDATES = [
    os.path.join(FONT_DIR, "Inter-SemiBold.otf"),
    os.path.join(FONT_DIR, "Inter-Bold.otf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def _first(paths):
    for p in paths:
        if os.path.exists(p):
            return p
    return None


def mono(size, bold=False):
    p = _first(MONO_BOLD_CANDIDATES if bold else MONO_CANDIDATES)
    return ImageFont.truetype(p, size) if p else ImageFont.load_default()


def ui(size, bold=False):
    p = _first(UI_BOLD_CANDIDATES if bold else UI_CANDIDATES)
    return ImageFont.truetype(p, size) if p else ImageFont.load_default()


# ------------------------------------------------------------------ warna util
def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lum(h):
    c = [v / 255 for v in hex2rgb(h)]
    c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def hue_of(h):
    r, g, b = [v / 255 for v in hex2rgb(h)]
    hh, _, _ = colorsys.rgb_to_hls(r, g, b)
    return hh * 360


# ------------------------------------------------------------------ theme file
def build_theme():
    """Format .theme xfce4-terminal: [Scheme] + key=value."""
    L = ["[Scheme]"]
    L.append("Name=ORACLE")
    L.append("Name[id]=ORACLE")
    L.append(f"ColorForeground={FG}")
    L.append(f"ColorBackground={BG}")
    L.append(f"ColorCursor={STEEL}")
    L.append(f"ColorCursorForeground={PORCELAIN}")
    L.append("ColorCursorUseDefault=FALSE")
    # selection: Steel dengan teks Porcelain (8.81:1)
    L.append(f"ColorSelection={STEEL}")
    L.append(f"ColorSelectionBackground={STEEL}")
    L.append("ColorSelectionUseDefault=FALSE")
    # bold: tetap Graphite, jangan jadi bright (bright di light theme = pudar)
    L.append(f"ColorBold={FG}")
    L.append("ColorBoldUseDefault=FALSE")
    L.append("ColorBoldIsBright=FALSE")
    L.append("ColorUseTheme=FALSE")
    L.append("ColorBackgroundVary=FALSE")
    L.append(f"TabActivityColor={BRASS_INK}")
    L.append("ColorPalette=" + ";".join(PALETTE))
    return "\n".join(L) + "\n"


def build_rc_fragment():
    """Potongan terminalrc. Bukan file utuh: hanya key yang kita tetapkan."""
    return f"""# ORACLE-OS — potongan terminalrc (xfce4-terminal 1.1.4-1)
# Salin key ini ke ~/.config/xfce4/terminal/terminalrc, atau ke
# /etc/xdg/xfce4/terminal/terminalrc untuk default sistem.
# JANGAN menimpa seluruh file: terminalrc berisi key lain milik user.

[Configuration]
ColorForeground={FG}
ColorBackground={BG}
ColorCursor={STEEL}
ColorCursorForeground={PORCELAIN}
ColorCursorUseDefault=FALSE
ColorSelection={STEEL}
ColorSelectionBackground={STEEL}
ColorSelectionUseDefault=FALSE
ColorBold={FG}
ColorBoldUseDefault=FALSE
ColorBoldIsBright=FALSE
ColorUseTheme=FALSE
ColorBackgroundVary=FALSE
TabActivityColor={BRASS_INK}
ColorPalette={";".join(PALETTE)}
FontName=JetBrains Mono 11
FontUseSystem=FALSE
FontAllowBold=TRUE
MiscCursorShape=TERMINAL_CURSOR_SHAPE_BLOCK
MiscCursorBlinks=FALSE
MiscAlwaysShowTabs=FALSE
MiscBell=FALSE
ScrollingUnlimited=TRUE
ScrollingBar=TERMINAL_SCROLLBAR_NONE
BackgroundMode=TERMINAL_BACKGROUND_SOLID
"""


# ------------------------------------------------------------------ preview
LINE_H = 20
PAD = 18
TITLE_H = 34


def draw_terminal(d, x, y, w, h, lines, title="oracle@workstation: ~/src"):
    """Gambar jendela terminal flat: titlebar Porcelain, body Porcelain."""
    # body
    d.rectangle([x, y, x + w, y + h], fill=BG)
    # titlebar
    d.rectangle([x, y, x + w, y + TITLE_H], fill=IVORY)
    d.line([x, y + TITLE_H, x + w, y + TITLE_H], fill=BORDER, width=1)
    # border
    d.rectangle([x, y, x + w, y + h], outline=BORDER, width=1)

    # tiga titik window control (flat, bukan macOS)
    cx = x + 14
    for col in (BORDER, BORDER, BORDER):
        d.ellipse([cx, y + 13, cx + 8, y + 21], fill=col)
        cx += 14
    # judul
    f = ui(11, bold=True)
    tw = d.textlength(title, font=f)
    d.text((x + (w - tw) / 2, y + 10), title, font=f, fill=STEEL)

    # isi
    fm = mono(12)
    fm_b = mono(12, bold=True)
    ty = y + TITLE_H + PAD
    for segs in lines:
        tx = float(x + PAD)
        for text, color, bold in segs:
            fnt = fm_b if bold else fm
            # bulatkan x: posisi pecahan membuat blok/teks ter-antialias
            # dan kehilangan warna solid (terbukti: slot 7 hilang).
            d.text((round(tx), ty), text, font=fnt, fill=color)
            tx += d.textlength(text, font=fnt)
        ty += LINE_H
    return ty


def prompt_segs(cmd_parts):
    """Prompt ORACLE: tick brass + user@host + path + $"""
    return [("▏", C_BRASS, False),
            ("oracle", C_OK, True), ("@", C_DIM, False),
            ("workstation", C_OK, True), (":", C_DIM, False),
            ("~/src", C_DIR, True), ("$ ", C_DIM, False)] + cmd_parts


def build_terminal_preview(width=980, height=560):
    img = Image.new("RGB", (width, height), IVORY)
    d = ImageDraw.Draw(img)

    # label MOCKUP STATIS
    d.text((20, 14), "MOCKUP STATIS", font=ui(13, bold=True), fill=STEEL)
    d.text((20, 32), "ORACLE terminal - preview skematis, bukan render xfce4-terminal",
           font=ui(9), fill=DUSTY)

    lines = [
        prompt_segs([("ls", C_CMD, True), (" -la", C_ARG, False)]),
        [("total 24", C_DIM, False)],
        [("drwxr-xr-x  4 oracle oracle 4096 Nov  2 14:20 ", C_DIM, False),
         ("docs", C_DIR, True)],
        [("drwxr-xr-x  2 oracle oracle 4096 Nov  2 14:20 ", C_DIM, False),
         ("iso", C_DIR, True)],
        [("drwxr-xr-x  6 oracle oracle 4096 Nov  2 14:20 ", C_DIM, False),
         ("src", C_DIR, True)],
        [("-rw-r--r--  1 oracle oracle  812 Nov  2 14:20 ", C_DIM, False),
         ("notes.md", C_ARG, False)],
        [],
        prompt_segs([("git status", C_CMD, True)]),
        [("On branch ", C_ARG, False), ("main", C_KEY, True)],
        [("Your branch is up to date with ", C_ARG, False),
         ("'origin/main'", C_STR, False), (".", C_ARG, False)],
        [],
        [("Changes not staged for commit:", C_ARG, False)],
        [("  modified:   ", C_WARN, False), ("src/panel.c", C_ARG, False)],
        [("  new file:   ", C_OK, False), ("docs/SPEC.md", C_ARG, False)],
        [],
        prompt_segs([("make build", C_CMD, True)]),
        [("[ 1/3] ", C_DIM, False), ("Compiling", C_ARG, False),
         (" panel.c", C_ARG, False)],
        [("warning: ", C_WARN, True),
         ("unused variable 'tmp' [-Wunused-variable]", C_ARG, False)],
        [("[ 2/3] ", C_DIM, False), ("Compiling", C_ARG, False),
         (" theme.c", C_ARG, False)],
        [("error: ", C_ERR, True),
         ("expected ';' before '}' token", C_ARG, False)],
        [("make: ", C_ERR, True), ("*** [Makefile:12: theme.o] Error 1", C_ARG, False)],
        [("build failed", C_ERR, True), (" (exit 2)", C_DIM, False)],
        [],
        prompt_segs([("echo $?", C_CMD, True)]),
        [("2", C_NUM, False)],
    ]

    draw_terminal(d, 20, 56, width - 40, height - 76, lines)

    # keterangan bawah (dipisah dua baris agar tidak terpotong)
    d.text((20, height - 30),
           "JetBrains Mono 11pt · latar Soft Porcelain #F5F3EC",
           font=ui(8), fill=GRAPHITE)
    d.text((20, height - 18),
           "teks Graphite #30363B (11.02:1) · prompt Steel #344653 · aksen Brass Ink #8C7B58",
           font=ui(8), fill=DUSTY)
    return img


def build_syntax_preview(width=980, height=430):
    """Contoh syntax highlighting: shell + python + git log."""
    img = Image.new("RGB", (width, height), IVORY)
    d = ImageDraw.Draw(img)
    d.text((20, 14), "MOCKUP STATIS", font=ui(13, bold=True), fill=STEEL)
    d.text((20, 32), "ORACLE terminal - syntax highlighting & semantic colors",
           font=ui(9), fill=DUSTY)

    lines = [
        [("# ", C_DIM, False), ("deploy.sh", C_DIM, False)],
        [("#!/usr/bin/env bash", C_DIM, False)],
        [("set ", C_CMD, True), ("-euo pipefail", C_ARG, False)],
        [],
        [("TARGET", C_KEY, False), ("=", C_ARG, False),
         ('"oracle-os"', C_STR, False)],
        [("VERSION", C_KEY, False), ("=", C_ARG, False), ("13", C_NUM, False)],
        [],
        [("if", C_CMD, True), (" [[ ", C_ARG, False), ("-d", C_ARG, False),
         (" build/ ]]", C_ARG, False), ("; then", C_CMD, True)],
        [("    rm", C_CMD, True), (" -rf build/", C_ARG, False)],
        [("fi", C_CMD, True)],
        [],
        [("echo", C_CMD, True), (' "Building ', C_STR, False),
         ("$TARGET", C_KEY, False), (' v', C_STR, False),
         ("$VERSION", C_KEY, False), ('"', C_STR, False)],
        [("lb build", C_CMD, True), (" 2>&1 | ", C_ARG, False),
         ("tee", C_CMD, True), (" build.log", C_ARG, False)],
        [],
        [("✓ ", C_OK, True), ("build complete", C_OK, False),
         ("  (2m 14s)", C_DIM, False)],
        [("⚠ ", C_WARN, True), ("2 packages skipped", C_WARN, False)],
        [("✗ ", C_ERR, True), ("iso checksum mismatch", C_ERR, False)],
    ]
    draw_terminal(d, 20, 56, width - 40, height - 76, lines,
                  title="oracle@workstation: ~/build")
    return img


def build_palette_inline(width=1320, height=250):
    """Baris 16 warna di dalam konteks terminal: membuktikan semua slot
    benar-benar terpakai dan terbaca, bukan hanya swatch terpisah."""
    img = Image.new("RGB", (width, height), IVORY)
    d = ImageDraw.Draw(img)
    d.text((20, 14), "MOCKUP STATIS", font=ui(13, bold=True), fill=STEEL)
    d.text((20, 32), "ORACLE terminal - 16 slot ANSI di dalam konteks",
           font=ui(9), fill=DUSTY)

    # latar jendela terminal digambar manual supaya blok warna bisa
    # ditempatkan presisi dengan rect (bukan glyph).
    x0, y0 = 20, 56
    w, h = width - 40, height - 76
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=BG)
    d.rectangle([x0, y0, x0 + w, y0 + TITLE_H], fill=IVORY)
    d.line([x0, y0 + TITLE_H, x0 + w, y0 + TITLE_H], fill=BORDER, width=1)
    d.rectangle([x0, y0, x0 + w, y0 + h], outline=BORDER, width=1)
    cx = x0 + 14
    for _ in range(3):
        d.ellipse([cx, y0 + 13, cx + 8, y0 + 21], fill=BORDER)
        cx += 14
    f = ui(11, bold=True)
    title = "oracle@workstation: ~/src"
    d.text((x0 + (w - d.textlength(title, font=f)) / 2, y0 + 10),
           title, font=f, fill=STEEL)

    fm = mono(11)
    fm_b = mono(12, bold=True)
    block_w, block_h = 12, 11
    # cell_w dihitung dari font sebenarnya, bukan ditebak: nama terpanjang
    # ("bright magenta") menentukan lebar minimum tiap sel.
    d_ = d
    name_w = max(d_.textlength(n, font=fm) for n in SLOT_NAMES)
    cell_w = int(22 + block_w + 6 + name_w + 22)   # +22 = jarak antar sel
    avail = (x0 + w) - (x0 + 16) - 10
    max_cell = avail // 8
    if cell_w > max_cell:
        cell_w = max_cell
    ty = y0 + TITLE_H + 16

    for row_start in (0, 8):
        for i in range(row_start, row_start + 8):
            col = i - row_start
            bx = x0 + 16 + col * cell_w
            # nomor slot
            d.text((bx, ty), f"{i:>2}", font=fm, fill=C_DIM)
            # blok warna (rect -> warna tepat, tanpa antialias)
            d.rectangle([bx + 22, ty + 2, bx + 22 + block_w, ty + 2 + block_h],
                        fill=PALETTE[i], outline=BORDER, width=1)
            # nama slot, selalu Graphite agar terbaca
            d.text((bx + 22 + block_w + 6, ty), SLOT_NAMES[i],
                   font=fm, fill=PALETTE[0])
        ty += 26

    ty += 8
    ex = [
        [("$ ", C_DIM, False), ("grep", C_CMD, True), (" -rn ", C_ARG, False),
         ('"error"', C_STR, False), (" src/", C_DIR, True)],
        [("src/main.c", C_ARG, False), (":42:", C_NUM, False),
         ("error", C_ERR, True), (": ", C_ARG, False),
         ("missing semicolon", C_ARG, False)],
        [("src/util.c", C_ARG, False), (":7:", C_NUM, False),
         ("warning", C_WARN, True), (": ", C_ARG, False),
         ("unused variable", C_ARG, False)],
        [("✓ ", C_OK, True), ("2 files checked", C_OK, False),
         ("   branch ", C_DIM, False), ("main", C_KEY, True)],
    ]
    for segs in ex:
        tx = float(x0 + 16)
        for text, color, bold in segs:
            fnt = mono(12, bold=True) if bold else fm
            d.text((round(tx), ty), text, font=fnt, fill=color)
            tx += d.textlength(text, font=fnt)
        ty += LINE_H
    return img


def build_palette_sheet(width=900, height=470):
    """Lembar 16 warna: swatch + hex + kontras."""
    img = Image.new("RGB", (width, height), PORCELAIN)
    d = ImageDraw.Draw(img)
    d.text((20, 16), "MOCKUP STATIS - ANSI 16-color palette", font=ui(13, bold=True), fill=STEEL)
    d.text((20, 34), "kontras diukur terhadap latar Soft Porcelain #F5F3EC",
           font=ui(9), fill=DUSTY)

    cols, rows = 4, 4
    cw, ch = 210, 92
    x0, y0 = 20, 60
    for i in range(16):
        r, c = divmod(i, cols)
        x = x0 + c * cw
        y = y0 + r * ch
        col = PALETTE[i]
        # swatch
        d.rectangle([x, y, x + 56, y + 56], fill=col, outline=BORDER, width=1)
        # nomor di dalam swatch, warna kontras
        fg_in = PORCELAIN if contrast(PORCELAIN, col) > contrast(GRAPHITE, col) else GRAPHITE
        d.text((x + 8, y + 6), str(i), font=mono(13, bold=True), fill=fg_in)
        # teks
        d.text((x + 66, y + 2), SLOT_NAMES[i], font=ui(10, bold=True), fill=STEEL)
        d.text((x + 66, y + 18), col, font=mono(10), fill=GRAPHITE)
        ratio = contrast(col, BG)
        tag = "teks" if ratio >= 4.5 else ("UI" if ratio >= 3 else "latar")
        d.text((x + 66, y + 34), f"{ratio:.2f}:1  {tag}", font=ui(9), fill=DUSTY)

    d.text((20, height - 22),
           "slot 0/7/8/15 = warna brand langsung · slot 1-6,9-14 = hue ANSI, "
           "lightness maksimum yang masih >=4.5:1",
           font=ui(8), fill=GRAPHITE)
    return img


def build_semantic_sheet(width=900, height=300):
    """Peta peran semantik: peran -> slot -> warna."""
    img = Image.new("RGB", (width, height), PORCELAIN)
    d = ImageDraw.Draw(img)
    d.text((20, 16), "MOCKUP STATIS - peran semantik", font=ui(13, bold=True), fill=STEEL)

    roles = [
        ("perintah / command", 4, C_CMD),
        ("argumen", 0, C_ARG),
        ("string", 2, C_STR),
        ("angka", 5, C_NUM),
        ("direktori", 4, C_DIR),
        ("sukses", 2, C_OK),
        ("warning", 3, C_WARN),
        ("error", 1, C_ERR),
        ("komentar / dim", 7, C_DIM),
        ("key / branch", 6, C_KEY),
    ]
    y = 52
    for label, slot, col in roles:
        d.rectangle([20, y, 44, y + 16], fill=col, outline=BORDER, width=1)
        d.text((54, y + 1), label, font=ui(10), fill=GRAPHITE)
        d.text((300, y + 1), f"slot {slot}", font=mono(10), fill=DUSTY)
        d.text((380, y + 1), col, font=mono(10), fill=GRAPHITE)
        d.text((500, y + 1), f"{contrast(col, BG):.2f}:1", font=ui(10), fill=DUSTY)
        y += 22
    return img


def main():
    theme = build_theme()
    p = os.path.join(CFG, "oracle.theme")
    open(p, "w", encoding="utf-8").write(theme)
    print(f"wrote {p} ({len(theme)} B)")

    rc = build_rc_fragment()
    p = os.path.join(CFG, "terminalrc.fragment")
    open(p, "w", encoding="utf-8").write(rc)
    print(f"wrote {p} ({len(rc)} B)")

    for fn, builder in [("terminal-main.png", build_terminal_preview),
                        ("terminal-syntax.png", build_syntax_preview),
                        ("terminal-palette-inline.png", build_palette_inline),
                        ("palette-sheet.png", build_palette_sheet),
                        ("semantic-sheet.png", build_semantic_sheet)]:
        img = builder()
        out = os.path.join(PREV, fn)
        img.save(out)
        print(f"wrote {out} {img.size}")

    # spec.txt
    lines = ["ORACLE-OS - terminal ANSI 16-color spesifikasi terukur",
             "target: xfce4-terminal 1.1.4-1 (Debian 13 Trixie), VTE 0.61.91+",
             f"latar: Soft Porcelain {BG}   teks: Graphite {FG}  ({contrast(FG,BG):.2f}:1)",
             ""]
    for i in range(16):
        c = PALETTE[i]
        lines.append(f"  {i:>2} {SLOT_NAMES[i]:15} {c}  {contrast(c,BG):5.2f}:1")
    lines += ["", "cursor: Steel #344653 di atas Porcelain, teks Porcelain",
              "selection: Steel #344653, teks Porcelain (8.81:1)",
              "bold: Graphite (tidak jadi bright)", ""]
    p = os.path.join(PREV, "spec.txt")
    open(p, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"wrote {p}")


if __name__ == "__main__":
    main()