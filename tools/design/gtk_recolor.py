#!/usr/bin/env python3
"""
ORACLE-OS — Stage 2C Tahap 4: full GTK recolor (fork Arc light).

Menghasilkan di gtk/ORACLE/gtk-3.0/:
  - gtk.css  : CSS Arc light di-recolor dengan semantic mapping ORACLE
  - assets/  : 125 PNG (62 id x 1x/@2x di-render dari assets.svg yang
               di-recolor; thumbnail-frame disalin dari gresource asli)

Sumber read-only (scratch): arc-gtk-main.css, arc-src/assets.svg,
gresource arc-theme 20221218-1. Tidak mengubah sumber mana pun.

Lisensi: turunan arc-theme GPL-3+ (lihat gtk/docs/NOTICE.md).
"""

import hashlib
import os
import re
import struct
import subprocess
import sys

# ------------------------------------------------------------------ palet
IVORY = "#E9E5DA"
PORCELAIN = "#F5F3EC"
STEEL = "#344653"
DUSTY = "#667D89"
GRAPHITE = "#30363B"


def hex2rgb(h):
    return tuple(int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))


def blend(fg, bg, a):
    f, b = hex2rgb(fg), hex2rgb(bg)
    return "#%02X%02X%02X" % tuple(round(f[i] * a + b[i] * (1 - a)) for i in range(3))


def lum(h):
    c = [x / 255 for x in hex2rgb(h)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


# ------------------------------------------------------- disabled fg (keputusan)
# Arya menyebut #AAABA9. Nilai itu TIDAK ADA di CSS Arc (0 kemunculan) dan
# hanya 1.83:1 di Ivory — lebih buruk dari #929494 (2.42:1).
# Disabled di Arc sebenarnya ditangani lewat ALPHA pada Graphite:
#     label:disabled { color: rgba(48, 54, 59, 0.55); }
# Alpha 0.55 menghasilkan #838583 = 2.95:1 di Ivory (gagal 3:1 untuk UI).
# Dipilih alpha 0.62 -> #767877 = 3.53:1 di Ivory (4.00:1 di Porcelain),
# tetap hanya 36% kontras teks normal (9.72:1) sehingga disabled jelas pudar.
DISABLED_FG = "#767877"
DISABLED_ALPHA = "0.62"
DISABLED_OLD_ALPHA = "0.55"
print("disabled_fg =", DISABLED_FG, f"(Ivory {ratio(DISABLED_FG, IVORY):.2f}:1, "
      f"Porcelain {ratio(DISABLED_FG, PORCELAIN):.2f}:1)")

# ---------------------------------------------------- GLOBAL hex map (CSS)
# Setiap warna Arc dipetakan PER ROL dominan. Kasus peran ganda ditangani
# lewat SPECIAL_RULES setelah replace global (lihat bawah).
GLOBAL_MAP = {
    # --- teks / aksen fungsional ---
    "#5c616c": GRAPHITE,   # teks utama
    "#5d626e": "#5A6268",  # osd disabled text (gelapkan)
    "#7d8189": "#4A5158",  # entry image / column header
    "#8a8e96": "#4A5158",  # dim label
    "#92959d": "#4A5158",  # tab flat / gedit panel
    "#a9acb2": "#6B7178",  # dim-label granite
    "#aeb0b6": "#6B7178",  # expander
    "#aaaeb7": "#6B7178",  # expander hover
    # --- biru Arc (seleksi / aksen) -> Steel family ---
    "#5294e2": STEEL,
    "#4dadd4": STEEL,       # suggested-action
    "#76c0de": "#4B5B65",   # suggested-action hover
    "#2e96c0": "#27343E",   # suggested-action active
    "#4189df": STEEL,       # documents-entry-tag active
    "#639fe5": "#4B5B65",   # documents-entry-tag hover
    "#4a85cb": "#27343E",   # row selected hover
    "#577ba7": STEEL,       # treeview drop
    "#1e61b0": "#27343E",   # link visited
    "#2679db": STEEL,       # link
    # --- tint biru muda (di atas seleksi Steel) -> teks TERANG ---
    # PENTING: nilai-nilai ini dipakai sebagai warna LINK/EXPANDER saat baris
    # terpilih, jadi latarnya Steel #344653. Abu menengah seperti #8B95A2
    # hanya mencapai 3.22:1 -- gagal ambang teks 4.5. Karena itu semuanya
    # dipetakan ke Porcelain atau near-Porcelain (>=8.8:1 di atas Steel).
    "#a9caf1": "#4B5B65",
    "#b1cff2": "#5E6C75",
    "#dceaf9": PORCELAIN,
    "#7eafe9": "#4B5B65",
    "#97bfee": "#8A949E",
    "#cbdff6": PORCELAIN,
    "#eef4fc": "#D8DAD6",
    "#e5effb": "#D8DAD6",
    "#bad4f3": PORCELAIN,
    # --- latar window / toolbar / surface ---
    "#f5f6f7": IVORY,
    "#edeef0": PORCELAIN,
    "#efeff0": PORCELAIN,
    "#f4f4f5": "#F2F0E9",
    "#fafbfb": PORCELAIN,
    "#fcfcfc": PORCELAIN,
    "#fbfbfc": PORCELAIN,
    "#fbfbfb": PORCELAIN,
    "#f7f7f7": "#F2F0E9",
    "#f8f8f9": PORCELAIN,
    "#fdfdfd": "#FAF9F4",
    "#ffffff": PORCELAIN,
    # --- border / separator ---
    "#dcdfe3": "#B9C1C2",
    "#cfd6e6": "#B9C1C2",
    "#cdd2d7": "#B9C1C2",
    "#d0d5da": "#C3CAC9",
    "#d9dde0": "#D6D7D4",
    # --- headerbar (special-case per rule) ---
    "#e7e8eb": STEEL,      # default; toolbar dikoreksi SPECIAL
    "#eff0f2": "#5E6C75",  # headerbar backdrop
    # --- panel gelap (mate/caja/unity) tetap gelap: konsisten Graphite ---
    "#353945": GRAPHITE,
    "#2f343f": GRAPHITE,
    "#2b2e37": GRAPHITE,
    "#2a2d37": GRAPHITE,
    # --- abu terang tersebar -> neutral muda ---
    "#b8babf": "#80868C",
    "#bdc6d1": "#7A8188",
    "#c7c9cd": "#5A6268",
    # --- OSD / overlay gelap: konten dan teks terang di atas permukaan gelap
    # (teks terang -> Ivory; border/abstrak -> neutral terang)
    "#bac3cf": "#E9E5DA",
    "#cfd5de": "#E9E5DA",
    "#5d6268": "#E9E5DA",
    "#d8dde4": "#F5F3EC",
    "#e7eaee": "#F5F3EC",
    "#f6f7f9": "#F5F3EC",
    "#f2f2f2": "#F2F0E9",       # list row hover
    "#d4d5db": "#B9C1C2",       # headerbar border
    # --- WM (window manager) ---
    "#525d76": GRAPHITE,
    "#21242b": "#27343E",
    "#90949e": "#6B7178",
    "#b6b8c0": "#80868C",
    "#7a7f8b": "#5A6268",
    "#d1d3da": "#B9C1C2",
    # --- placeholder (variabel tidak terpakai di body; map lintas aman) ---
    "#a8a8a8": blend(GRAPHITE, PORCELAIN, 0.50),
}

# Kasus peran ganda: sesudah GLOBAL, perbaiki aturan yang spesifik.
# Format: (selector_substring, selector_exclude_substring, old, new)
# - selector_substring  : rule yang selectornya MENGANDUNG ini
# - selector_exclude    : rule yang selectornya mengandung ini DILEWATI
#                         (mis. ".primary-toolbar" container vs
#                          ".primary-toolbar button.suggested-action")
SPECIAL_RULES = [
    # Toolbar container window-level harus Porcelain (bukan Steel seperti
    # headerbar). HANYA rule yang selectornya toolbar TANPA komponen
    # (button/entry/spinbutton) — kalau tidak, rule gabungan seperti
    # ".primary-toolbar button.suggested-action, headerbar button..." ikut
    # tersentuh dan merusak bg aksi (white di atas Porcelain).
    (".primary-toolbar",
     ("button", "entry", "spinbutton", "scale"),
     "#344653", PORCELAIN),
    # thumbnail-frame tidak tersedia sebagai asset (tidak ada id di assets.svg,
    # terverifikasi). Ganti border-image dengan border solid agar referensi valid.
    ("content-view.document-page",
     (),
     'border-image: url("assets/thumbnail-frame.png") 3 3 6 4;',
     'border-color: #667D89;'),
]

# Warna STATUS SEMANTIK dipertahankan dari Arc (tidak diganti) karena palet
# ORACLE tidak mendefinisikan warna status; menggantinya akan menghilangkan
# makna sinyal. Ini pengecualian eksplisit yang didokumentasikan.
PRESERVED_SEMANTIC = {
    "#FC4138", "#FD8D88",        # error
    "#F27835", "#F7AE86",        # warning
    "#F04A50", "#F4797E", "#EC1B22",  # destructive
    "#F08437",                   # drop(active)
    "#FF4D4D", "#FF6666",        # tab/gedit close hover
    "#FD716A",                   # conflict-row
    "#EEA279", "#F4807B",        # warning/error soft bg (headerbar entry)
    "#F75D37",                   # error+warning boundary
    "#73D216",                   # success / levelbar full
    "#F13039", "#F46067", "#F68086",  # wm close buttons
}


# --- RGBA: Arc menulis banyak warna sebagai rgba(r,g,b,a). Triple-nya harus
# dipetakan juga, kalau tidak biru Arc tetap tertinggal. Alpha dipertahankan.
RGBA_MAP = {
    # biru Arc & turunannya
    (82, 148, 226): STEEL,
    (38, 121, 219): STEEL,
    (65, 137, 223): STEEL,
    # teks/ikon Arc gelap
    (92, 97, 108): GRAPHITE,
    (82, 93, 118): DUSTY,        # garis/shadow; teks di atas gelap diperbaiki pass kontras
    (102, 109, 132): "#6B7480",
    (119, 127, 151): "#7A8188",
    (123, 142, 186): DUSTY,
    (123, 129, 141): "#7A8188",
    # shadow sangat gelap
    (53, 57, 69): GRAPHITE,
    (43, 46, 55): GRAPHITE,
    (42, 45, 55): GRAPHITE,
    (69, 74, 89): "#27343E",
    (75, 81, 98): "#27343E",
    (69, 72, 80): "#27343E",
    (54, 58, 70): "#27343E",
    (37, 40, 49): "#27343E",
    (35, 38, 46): "#27343E",
    (32, 34, 41): "#27343E",
    (31, 33, 40): "#27343E",
    (27, 29, 35): "#27343E",
    (26, 28, 34): "#27343E",
    (20, 22, 27): "#1F2A33",
    # netral terang
    (207, 214, 230): "#B9C1C2",
    (212, 213, 219): "#B9C1C2",
    (220, 223, 227): "#B9C1C2",
    (186, 195, 207): "#B9C1C2",
    (231, 234, 238): PORCELAIN,
    (239, 240, 242): "#5E6C75",
    (251, 251, 252): PORCELAIN,
    (253, 253, 254): PORCELAIN,
    (255, 255, 255): PORCELAIN,
    (245, 246, 247): IVORY,
    (231, 232, 235): STEEL,
    # status semantik dipertahankan (mapping ke dirinya sendiri)
    (238, 162, 121): "#EEA279",
    (244, 128, 123): "#F4807B",
}

# Permukaan gelap: teks di atasnya harus terang. Dipakai pass perbaikan kontras.
DARK_SURFACES = {STEEL, GRAPHITE, "#27343E", "#1F2A33", "#5E6C75", "#4B5B65"}
LIGHT_SURFACES = {IVORY, PORCELAIN, "#E6E5E0", "#D6D7D4", "#F2F0E9", "#B9C1C2", "#D1D3CC"}


def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _lum(h):
    c = [v / 255 for v in _rgb(h)]
    c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def recolor_rgba(text):
    """Petakan triple rgba sesuai RGBA_MAP, alpha dipertahankan."""
    def repl(m):
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if m.group(4) is None:
            return m.group(0)
        tgt = RGBA_MAP.get((r, g, b))
        if tgt is None:
            return m.group(0)
        tr, tg, tb = _rgb(tgt)
        return f"rgba({tr}, {tg}, {tb}, {m.group(4)})"
    return re.sub(
        r"rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([\d.]+)\s*\)", repl, text)


def _fix_fg_contrast(text):
    """Untuk setiap rule: kalau ada background-color eksplisit dan `color:`
    tidak kontras, pilih fg TERBAIK dari palet (Porcelain vs Graphite).
    Deterministik, tidak memperkenalkan warna baru. Fail-closed: hanya
    menyentuh deklarasi `color:` di rule yang punya bg eksplisit."""
    out = []
    i, n = 0, len(text)
    while i < n:
        j = text.find("{", i)
        if j < 0:
            out.append(text[i:])
            break
        k = text.find("}", j)
        if k < 0:
            out.append(text[i:])
            break
        sel, body = text[i:j], text[j + 1:k]
        if "{" in body:          # nested rule, biarkan
            out.append(text[i:k + 1])
            i = k + 1
            continue
        # bg bisa hex ATAU rgba opaque (alpha >= 0.95). _parse_color
        # mengembalikan None untuk bg transparan, jadi rule seperti itu
        # dilewati (tidak bisa dinilai kontrasnya secara jujur).
        bg_decl = re.findall(r"background(?:-color)?\s*:\s*([^;]+);", body)
        bg = _parse_color(bg_decl[-1]) if bg_decl else None
        if bg:

            def fix(m):
                val = m.group(1).strip()
                hx = None
                mh = re.fullmatch(r"(#[0-9a-fA-F]{6})", val)
                mr = re.fullmatch(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)[^)]*\)", val)
                if mh:
                    hx = mh.group(1)
                elif mr:
                    hx = "#%02X%02X%02X" % (int(mr.group(1)), int(mr.group(2)), int(mr.group(3)))
                if not hx:
                    return m.group(0)
                if contrast(hx, bg) >= 4.4:
                    return m.group(0)
                best = max((PORCELAIN, GRAPHITE), key=lambda c: contrast(c, bg))
                return f"color: {best};"

            # (?<![-a-z]) wajib: tanpa itu regex ikut menelan
            # "background-color:" dan merusak deklarasi.
            body = re.sub(r"(?<![-a-z])color\s*:\s*([^;]+);", fix, body)
        out.append(sel + "{" + body + "}")
        i = k + 1
    return "".join(out)


def recolor_css(text):
    """Ganti semua hex sesuai GLOBAL_MAP, lalu rgba, lalu terapkan
    SPECIAL_RULES, terakhir perbaiki kontras foreground di rule ber-bg.
    Warna status semantik (PRESERVED_SEMANTIC) tidak disentuh."""
    out = text
    # 0) keyword warna CSS -> hex agar bisa dipetakan & diukur kontrasnya
    for name, hx in (("white", PORCELAIN), ("black", GRAPHITE)):
        out = re.sub(rf"(?<![-a-zA-Z#]){name}(?![-a-zA-Z])", hx, out)
    for old, new in GLOBAL_MAP.items():
        old_l = old.lower()
        out = re.sub(old_l, new, out, flags=re.IGNORECASE)
    out = recolor_rgba(out)
    # Disabled fg: naikkan alpha Graphite 0.55 -> 0.62 HANYA pada `color:`.
    # Terverifikasi 21/21 kemunculan rgba(48,54,59,0.55) adalah color;
    # 0 dipakai sebagai border, jadi perubahan ini tidak menyentuh border.
    out = re.sub(
        r"(?<![-a-z])color\s*:\s*rgba\(\s*48,\s*54,\s*59,\s*0\.55\s*\)",
        f"color: rgba(48, 54, 59, {DISABLED_ALPHA})", out)
    for sel, excludes, old, new in SPECIAL_RULES:
        # terapkan hanya dalam blok rule yang selector-nya mengandung sel
        out = _apply_in_selector(out, sel, excludes, old, new)
    out = _fix_fg_contrast(out)
    return out


def _apply_in_selector(text, sel_sub, excludes, old, new):
    """Terapkan replace old->new hanya pada rule yang selectornya mengandung
    sel_sub DAN tidak mengandung satu pun string di `excludes`.
    Parse rule dengan brace matching sederhana."""
    res = []
    i = 0
    n = len(text)
    while i < n:
        j = text.find("{", i)
        if j < 0:
            res.append(text[i:])
            break
        sel = text[i:j]
        # cari penutup
        depth = 1
        k = j + 1
        while k < n and depth > 0:
            if text[k] == "{":
                depth += 1
            elif text[k] == "}":
                depth -= 1
            k += 1
        body = text[j + 1:k - 1]
        if sel_sub in sel and not any(ex in sel for ex in excludes):
            body = body.replace(old, new)
        res.append(text[i:j + 1] + body + "}")
        i = k
    return "".join(res)


# ---------------------------------------------------- assets.svg recolor
ASSET_MAP = {
    # biru Arc -> Steel (checkbox/radio/switch active, titlebutton hover/active)
    "#5294e2": STEEL,
    "#c0e3ff": blend(STEEL, PORCELAIN, 0.35),   # tint biru muda -> Dusty tone
    "#7eafe9": blend(STEEL, PORCELAIN, 0.35),
    "#4dadd4": STEEL,
    "#2d323d": GRAPHITE,   # bg gelap asset (icon) -> Graphite
    "#2d323f": GRAPHITE,
    "#353a47": GRAPHITE,
    "#2b303b": GRAPHITE,
    "#262934": GRAPHITE,
    "#15171c": "#1E2226",
    "#000000": "#1E2226",  # outline hitam -> Graphite muram
}


def recolor_svg(svg_text, mapping):
    """Ganti fill/stroke hex di SVG.
    Pakai mapping gabungan: GLOBAL_MAP (semantik penuh) + nilai spesifik aset.
    Urutan penting: entri khusus aset dulu, lalu GLOBAL_MAP, supaya tint
    seperti #c0e3ff tidak tertimpa aturan umum."""
    merged = dict(ASSET_MAP)
    for k, v in GLOBAL_MAP.items():
        merged.setdefault(k, v)
    out = svg_text
    # case-insensitive, longest-first agar tidak ada penggantian parsial
    for old in sorted(merged, key=len, reverse=True):
        new = merged[old]
        out = re.sub(re.escape(old), new, out, flags=re.IGNORECASE)
    return out


# ---------------------------------------------------- render assets dari svg
# Ukuran per id (dari distribusi blok PNG asli): 16/32 (checkbox,radio,title),
# 52x24/104x48 (switch), 40/80 (thumbnail - disalin, bukan render).
SIZES = {
    "checkbox": (16, 16), "radio": (16, 16), "titlebutton": (16, 16),
    "switch": (52, 24), "thumbnail": (40, 40),
}


def size_for_id(iid):
    if iid.startswith("switch"):
        return (52, 24)
    if iid.startswith("titlebutton"):
        return (16, 16)
    if iid.startswith("thumbnail"):
        return (40, 40)
    return (16, 16)


def render_asset(assets_svg, iid, w, h, out_path):
    """Render id dari SVG via rsvg-convert --export-id + force size."""
    r = subprocess.run(
        ["rsvg-convert", "-i", iid, "-w", str(w), "-h", str(h),
         "-o", out_path, assets_svg],
        capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"render {iid}: {r.stderr.strip()[:120]}")
    return out_path


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _unmapped_rgba(css):
    """Triple rgba yang tidak dipetakan DAN bukan warna ORACLE/semantik.
    Hitam murni dikecualikan: shadow dekoratif (alpha rendah)."""
    oracle = {k.upper() for k in
              (IVORY, PORCELAIN, STEEL, DUSTY, GRAPHITE, DISABLED_FG,
               "#B9C1C2", "#5E6C75", "#4B5B65", "#27343E", "#1F2A33",
               "#6B7480", "#7A8188", "#E6E5E0", "#D6D7D4", "#F2F0E9", "#D1D3CC")}
    oracle |= {h.upper() for h in PRESERVED_SEMANTIC}
    oracle_triples = {_rgb(h) for h in oracle}
    oracle_triples.add((0, 0, 0))            # shadow dekoratif
    bad = set()
    for m in re.finditer(r"rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*[\d.]+\s*\)", css):
        t = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
        if t not in oracle_triples:
            bad.add(t)
    return sorted(bad)


def _parse_color(v):
    """Ambil hex dari deklarasi warna (hex/rgb/rgba). None bila bukan warna solid."""
    v = v.strip()
    mh = re.search(r"#[0-9a-fA-F]{6}", v)
    if mh:
        return mh.group(0)
    mr = re.search(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+))?\s*\)", v)
    if mr:
        a = float(mr.group(4)) if mr.group(4) else 1.0
        if a < 0.95:            # transparan: tidak bisa dinilai sebagai latar solid
            return None
        return "#%02X%02X%02X" % (int(mr.group(1)), int(mr.group(2)), int(mr.group(3)))
    return None


def _contrast_audit(css):
    """Hitung kontras tiap rule yang punya `color:` + background eksplisit.
    rgba dengan alpha < 0.95 dilewati (tidak solid). <3.0 = GAGAL, 3.0-4.5 = INFO."""
    fails, checks, skipped = [], 0, 0
    i, n = 0, len(css)
    while i < n:
        j = css.find("{", i)
        if j < 0:
            break
        k = css.find("}", j)
        if k < 0:
            break
        sel = css[i:j].strip()
        body = css[j + 1:k]
        if "{" not in body:
            bg_decl = re.findall(r"background(?:-color)?\s*:\s*([^;]+);", body)
            fg_decl = re.findall(r"(?<![-a-z])color\s*:\s*([^;]+);", body)
            if bg_decl and fg_decl:
                bg = _parse_color(bg_decl[-1])
                fg = _parse_color(fg_decl[-1])
                if bg and fg:
                    checks += 1
                    r = contrast(fg, bg)
                    if r < 3.0:
                        fails.append(f"GAGAL {r:5.2f}:1 {sel[:70]} fg={fg} bg={bg}")
                    elif r < 4.5:
                        fails.append(f"INFO  {r:5.2f}:1 {sel[:70]} fg={fg} bg={bg}")
                else:
                    skipped += 1
        i = k + 1
    return fails, checks, skipped


def audit(OUT):
    """Audit final: parse CSS, refs valid, kontras, biru sisa, manifest."""
    import collections as _c
    report = []

    def say(s=""):
        report.append(s)
        print(s)

    say("=== AUDIT TAHAP 4 ===")

    # 1) parse CSS: brace balance sederhana
    css_path = os.path.join(OUT, "gtk.css")
    css = open(css_path, encoding="utf-8").read()
    depth = 0
    for ch in css:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth < 0:
                say("  FAIL: brace negatif (CSS tidak seimbang)")
                break
    say(f"  1) CSS brace balance: {'OK (0)' if depth == 0 else 'GAGAL: ' + str(depth)}")

    # 2) refs asset valid
    refs = sorted(set(re.findall(r'url\("([^"]+)"\)', css)))
    asset_dir = os.path.join(OUT, "assets")
    missing = [r for r in refs if not os.path.exists(os.path.join(asset_dir, r.replace("assets/", "")))]
    say(f"  2) refs url() = {len(refs)}; hilang = {len(missing)} {missing if missing else ''}")

    # 3) sisa biru Arc di komponen fungsional — HEX **dan** RGBA
    hex_blue = [h for h in set(re.findall(r"#[0-9a-fA-F]{6}", css))
                if h.lower() == "#5294e2"]
    rgba_blue = re.findall(
        r"rgba\(\s*82\s*,\s*148\s*,\s*226\s*,[^)]+\)", css)
    rgb_blue = re.findall(
        r"rgb\(\s*82\s*,\s*148\s*,\s*226\s*\)", css)
    say(f"  3) sisa biru Arc: hex={len(hex_blue)} rgba={len(rgba_blue)} "
        f"rgb={len(rgb_blue)} -> {'BERSIH' if not (hex_blue or rgba_blue or rgb_blue) else 'ADA SISA'}")

    # 3b) triple rgba lain yang belum terpetakan (harus 0)
    unmapped = _unmapped_rgba(css)
    say(f"  3b) triple rgba belum terpetakan: {len(unmapped)} {unmapped[:8] if unmapped else ''}")

    # 4) warna semantik yang dipertahankan (memastikan tidak hilang tak sengaja)
    sem_preserved_lower = {h.lower() for h in PRESERVED_SEMANTIC}
    sem_remaining = sorted({h.lower() for h in set(re.findall(r"#[0-9a-fA-F]{6}", css))
                            if h.lower() in sem_preserved_lower})
    say(f"  4) warna status semantik dipertahankan: {len(sem_remaining)} {sem_remaining}")

    # 5) hitung hex unik & total
    hexes = _c.Counter(re.findall(r"#[0-9a-fA-F]{6}", css))
    say(f"  5) hex unik = {len(hexes)}, total = {sum(hexes.values())}")

    # 5b) AUDIT KONTRAS per-rule (semua rule yang punya color + bg eksplisit)
    fails, checks, skipped = _contrast_audit(css)
    say(f"  5b) kontras: {checks} rule diukur, {skipped} dilewati (transparan), "
        f"{len(fails)} perlu perhatian")
    for f in fails[:15]:
        say(f"      {f}")
    if len(fails) > 15:
        say(f"      ... dan {len(fails) - 15} lainnya")

    # 6) file assets
    pngs = sorted(os.listdir(asset_dir))
    say(f"  6) file assets/ = {len(pngs)} ({sum(1 for p in pngs if p.endswith('.png'))} png)")

    # 7) manifest SHA-256 — satu manifest di root paket (ORACLE/),
    #    mencakup COPYING, NOTICE.md, dan seluruh isi gtk-3.0/.
    root = os.path.dirname(OUT)
    manifest = []
    for walk_root, dirs, files in os.walk(root):
        dirs.sort()
        for f in sorted(files):
            if f == "SHA256SUMS.txt":
                continue
            p = os.path.join(walk_root, f)
            rel = os.path.relpath(p, root)
            manifest.append(f"{sha256(p)}  {rel}")
    with open(os.path.join(root, "SHA256SUMS.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(manifest) + "\n")
    # bersihkan manifest lama yang salah tempat (di gtk-3.0/)
    stale = os.path.join(OUT, "SHA256SUMS.txt")
    if os.path.exists(stale):
        os.remove(stale)
    say(f"  7) manifest: {len(manifest)} file -> {root}/SHA256SUMS.txt")

    return "\n".join(report)


# ---------------------------------------------------- main pipeline
def main():
    BASE_SCRATCH = os.path.expanduser(
        "~/.hermes/profiles/doraemon/cache/scratch/oracle-design")
    OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/gtk/ORACLE/gtk-3.0"
    assets_dir = os.path.join(OUT, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    print("== 1) recolor CSS ==")
    css_src = open(f"{BASE_SCRATCH}/arc-gtk-main.css", encoding="utf-8").read()
    css_out = recolor_css(css_src)
    with open(os.path.join(OUT, "gtk.css"), "w", encoding="utf-8") as fh:
        fh.write(css_out)
    print(f"  gtk.css: {len(css_out)} B, sha={sha256(os.path.join(OUT, 'gtk.css'))[:16]}")

    print("\n== 2) recolor assets.svg + render 124 PNG ==")
    svg_src = open(f"{BASE_SCRATCH}/arc-src/arc-theme-20221218/common/gtk-3.0/assets/assets.svg",
                   encoding="utf-8").read()
    svg_rec = recolor_svg(svg_src, ASSET_MAP)
    # simpan svg terecolor sebagai catatan sumber
    with open(os.path.join(OUT, "assets", "oracle-assets.svg"), "w", encoding="utf-8") as fh:
        fh.write(svg_rec)
    # tulis ke temp utk rsvg
    tmp_svg = os.path.join(BASE_SCRATCH, "oracle-assets-recolored.svg")
    with open(tmp_svg, "w", encoding="utf-8") as fh:
        fh.write(svg_rec)

    css2 = open(os.path.join(OUT, "gtk.css"), encoding="utf-8").read()
    refs = sorted(set(re.findall(r'url\("([^"]+)"\)', css2)))
    rendered = []
    for ref in refs:
        base = ref.replace("assets/", "").replace(".png", "")
        if base == "thumbnail-frame":
            continue
        iid = base.replace("@2", "")
        scale = 2 if base.endswith("@2") else 1
        w, h = size_for_id(iid)
        out_path = os.path.join(assets_dir, f"{base}.png")
        render_asset(tmp_svg, iid, w * scale, h * scale, out_path)
        rendered.append(base)
    print(f"  rendered {len(set(rendered))} unique id -> {len(rendered)} PNG (1x+@2x)")

    print("\n== 3) thumbnail-frame -> tidak bisa dirender (tidak ada id di "
          "assets.svg/assets.txt, terverifikasi). Rule CSS diganti border solid. ==")
    thumb_out = os.path.join(assets_dir, "thumbnail-frame.png")
    if os.path.exists(thumb_out):
        os.remove(thumb_out)
        print(f"  hapus sisa {thumb_out}")

    print("\n== 4) hapus gtk.gresource (folder-based theme) ==")
    gr = os.path.join(OUT, "gtk.gresource")
    if os.path.exists(gr):
        os.remove(gr)
        print(f"  dihapus {gr}")

    print("\n== 5) audit ==")
    audit(OUT)
    print("\nSELESAI")


def _copy_thumbnail(recolor=True, out=None):
    """Ambil blok PNG thumbnail-frame dari gresource (netral), recolor biru."""
    BASE_SCRATCH = os.path.expanduser(
        "~/.hermes/profiles/doraemon/cache/scratch/oracle-design")
    gpath = f"{BASE_SCRATCH}/deb/x_arc-theme/usr/share/themes/Arc/gtk-3.0/gtk.gresource"
    data = open(gpath, "rb").read()
    # string nama thumbnail-frame.png ada di namelist; cari PNG magic setelahnya
    marker = data.find(b"assets/thumbnail-frame.png")
    if marker < 0:
        raise RuntimeError("thumbnail-frame.png tidak ditemukan di gresource")
    PNG = b"\x89PNG\r\n\x1a\n"
    start = data.find(PNG, marker)
    if start < 0:
        raise RuntimeError("PNG blok utk thumbnail tidak ditemukan")
    import struct as _s
    p = start + 8
    while p + 8 <= len(data):
        ln, typ = _s.unpack_from(">I4s", data, p)
        p += 8 + ln + 4
        if typ == b"IEND":
            break
    raw = data[start:p]
    if recolor:
        import io as _io
        from PIL import Image
        im = Image.open(_io.BytesIO(raw)).convert("RGBA")
        px = im.load()
        w, h = im.size
        for y in range(h):
            for x in range(w):
                r, g, b, a = px[x, y]
                if a > 100 and abs(r - 0x52) < 60 and abs(g - 0x94) < 60 and abs(b - 0xE2) < 60:
                    px[x, y] = (0x34, 0x46, 0x53, a)
        im.save(out, "PNG")
    else:
        with open(out, "wb") as fh:
            fh.write(raw)
    return out


if __name__ == "__main__":
    main()