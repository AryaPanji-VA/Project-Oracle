#!/usr/bin/env python3
"""ORACLE-OS — Stage 2F-A: Papirus icon theme, recolor terbatas.

STRATEGI (berbasis bukti audit, lihat docs/AUDIT-PAPIRUS.md):
  Pakai Papirus PENUH, bukan Papirus-Light.
  Alasan terukur: Papirus-Light tidak punya SATU PUN dari 20 ikon XFCE yang
  dipakai .desktop di image (org.xfce.terminalemulator, org.xfce.filemanager,
  org.xfce.panel, xfsm-logout, ...), dan juga tidak punya folder/actions
  (folder, user-home, edit-copy, view-refresh). Papirus penuh punya semuanya.
  Papirus-Light Inherits=breeze,hicolor -- BUKAN Papirus -- jadi ikon yang
  hilang jatuh ke hicolor, bukan ke Papirus.

  Recolor TERBATAS: hanya biru aksen Papirus (#5294E2 dan turunannya) yang
  dipetakan ke Steel Blue. Bentuk, geometri, dan detail Papirus dipertahankan
  apa adanya. Tidak ada ikon yang digambar ulang.

Menghasilkan:
  papirus/theme/ORACLE-Papirus/        tema ikon hasil recolor (subset)
  papirus/preview/*.png                grid preview
  papirus/docs/*                       dokumentasi
  papirus/manifest.txt                 daftar ikon yang diubah
"""

import os
import re
import shutil
import subprocess
import sys

# ------------------------------------------------------------------ palet
IVORY     = "#E9E5DA"
PORCELAIN = "#F5F3EC"
STEEL     = "#344653"
DUSTY     = "#667D89"
BRASS     = "#B8A98D"
BRASS_INK = "#8C7B58"
GRAPHITE  = "#30363B"

SRC = os.path.expanduser(
    "~/.hermes/profiles/doraemon/cache/scratch/oracle-design/deb/x_papirus/usr/share/icons/Papirus")
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "papirus")
THEME = os.path.join(ROOT, "theme", "ORACLE-Papirus")
PREV = os.path.join(ROOT, "preview")
DOCS = os.path.join(ROOT, "docs")

# ------------------------------------------------------------------ recolor map
# Hanya biru aksen Papirus. Nilai diturunkan dari sampel nyata (lihat audit).
# #5294E2 adalah biru aksen Papirus -- kebetulan SAMA dengan biru Arc, jadi
# pemetaan ini konsisten dengan keputusan GTK theme.
ACCENT_MAP = {
    "#5294e2": STEEL,        # aksen utama
    "#4877b1": "#2A3A45",    # aksen gelap (bayangan folder)
    "#1d344f": "#1F2A33",    # aksen sangat gelap
    "#3ea0f4": DUSTY,        # aksen terang (browser)
    "#0090ef": DUSTY,        # aksen terang (appfinder)
    "#4354cb": STEEL,        # aksen ungu-biru (browser)
    "#89e058": "#4E7A3A",    # hijau filemanager -> hijau earthy
    "#ffcd54": BRASS_INK,    # kuning filemanager -> brass
}

# Warna status Papirus di 16x16 (ikon berwarna, bukan symbolic).
# Ini warna STATUS (shutdown/reboot/positif/negatif) - dipertahankan maknanya
# tetapi digeser ke palet ORACLE yang setara secara semantik.
STATUS_MAP = {
    "#f44336": "#B4503C",   # merah status -> merah terminal (error/shutdown)
    "#ff9800": "#8A682E",   # oranye status -> kuning terminal (warning/reboot)
    "#4caf50": "#317E2A",   # hijau status -> hijau terminal (sukses)
    "#4285f4": STEEL,       # highlight -> Steel
    "#1e88e5": STEEL,       # biru panel -> Steel
    "#253951": "#2A3A45",   # biru gelap panel -> Steel gelap
    "#e6461d": "#B4503C",   # oranye-merah session -> merah terminal
    # warna ilustratif ikon 16x16 (session/settings/color) -> palet ORACLE
    "#ff7c19": "#8A682E",   # oranye roket -> kuning earthy
    "#ffe113": BRASS_INK,   # kuning terang -> brass
    "#ffc107": BRASS_INK,   # kuning palet -> brass
    "#007ede": STEEL,       # biru session -> Steel
    "#008374": "#2B7682",   # teal settings -> cyan terminal
    "#278df2": DUSTY,       # biru terang palet -> Dusty
    # --- sisa warna ilustratif (settings/editor/a11y/mail/battery/network) ---
    # Semua dipetakan ke palet ORACLE terdekat secara semantik. Tidak ada
    # warna baru yang diperkenalkan; hanya 7 warna brand + 3 turunan netral.
    "#34e0c4": "#2B7682",   # teal terang -> cyan terminal
    "#009688": "#2B7682",   # teal -> cyan terminal
    "#00796b": "#2B7682",   # teal gelap -> cyan terminal
    "#18c28c": "#317E2A",   # hijau-teal -> hijau terminal
    "#fb8300": "#8A682E",   # oranye -> kuning earthy
    "#f36021": "#B4503C",   # oranye-merah -> merah terminal
    "#fe9700": "#8A682E",   # oranye mail -> kuning earthy
    "#fec006": BRASS_INK,   # kuning mail -> brass
    "#fecd38": BRASS_INK,   # kuning terang mail -> brass
    "#f8c44e": BRASS_INK,   # kuning network -> brass
    "#fa3e30": "#B4503C",   # merah -> merah terminal
    "#ff5722": "#B4503C",   # oranye-merah lock -> merah terminal
    "#f4783a": "#8A682E",   # oranye baterai -> kuning earthy
    "#a544c9": "#B83D99",   # ungu -> magenta terminal
    "#3e50b4": STEEL,       # biru-ungu a11y -> Steel
    "#03a9f4": DUSTY,       # biru terang -> Dusty
    "#62c9ea": DUSTY,       # biru muda terminal -> Dusty
    "#5895dc": DUSTY,       # biru filemanager -> Dusty
    "#4671e6": STEEL,       # biru baterai -> Steel
    "#455a64": "#2A3A45",   # abu-biru executable -> Steel gelap
    "#c0f957": "#4E7A3A",   # hijau terang baterai -> hijau earthy
}

# Ikon yang WAJIB ada (dipakai .desktop / panel / file manager).
# Diverifikasi dari .desktop paket XFCE di image.
REQUIRED = [
    "org.xfce.terminalemulator", "org.xfce.filemanager", "org.xfce.webbrowser",
    "org.xfce.appfinder", "org.xfce.panel", "org.xfce.session",
    "org.xfce.settings.manager", "org.xfce.settings.appearance",
    "org.xfce.settings.display", "org.xfce.settings.keyboard",
    "org.xfce.settings.mouse", "org.xfce.settings.color",
    "org.xfce.settings.editor", "org.xfce.settings.accessibility",
    "org.xfce.settings.default-applications", "org.xfce.terminal",
    "org.xfce.terminal-settings", "org.xfce.xfdesktop", "org.xfce.mailreader",
    "xfsm-logout", "application-x-executable",
    # places / actions yang dipakai file manager & panel
    "folder", "folder-home", "user-home", "user-desktop", "user-trash",
    "edit-copy", "edit-paste", "edit-cut", "view-refresh", "system-shutdown",
    "system-reboot", "system-log-out", "system-lock-screen",
    # status panel
    "network-wireless", "network-wired", "audio-volume-high", "audio-volume-muted",
    "battery-full", "battery-caution", "battery-low",
]

SIZES = ["16x16", "22x22", "24x24", "32x32", "48x48", "64x64"]


def recolor_svg(text):
    """Ganti hanya warna aksen & status. Bentuk & atribut lain tidak disentuh."""
    out = text
    for old, new in {**ACCENT_MAP, **STATUS_MAP}.items():
        out = re.sub(re.escape(old), new, out, flags=re.IGNORECASE)
    return out


def is_symbolic(text):
    """True bila SVG benar-benar symbolic: memakai currentColor.

    CATATAN: blok <style> ColorScheme-* SENDIRIAN tidak cukup. Banyak ikon
    16x16 Papirus punya blok itu tetapi tetap memakai hex langsung
    (mis. system-shutdown.svg berisi fill:#f44336). Deteksi harus pada
    pemakaian `currentColor`, bukan pada keberadaan blok style.
    """
    return "currentColor" in text


def find_icon(name):
    """Cari file ikon BERWARNA (22px ke atas) DAN symbolic (16x16).

    Papirus punya dua jenis ikon yang berbeda secara struktural:
      - 16x16  : symbolic, memakai `fill:currentColor` + class ColorScheme-*.
                 Warnanya mengikuti warna teks GTK, bukan hex tetap. Recolor
                 hex TIDAK berpengaruh di sini.
      - 22px+  : ikon berwarna dengan hex langsung (#5294e2 dsb).

    Kembalikan (relpath, abspath, is_symbolic).
    """
    hits = []
    for size in SIZES:
        d = os.path.join(SRC, size)
        if not os.path.isdir(d):
            continue
        for cat in sorted(os.listdir(d)):
            cd = os.path.join(d, cat)
            if not os.path.isdir(cd):
                continue
            for ext in (".svg", ".png"):
                p = os.path.join(cd, name + ext)
                if not os.path.exists(p):
                    continue
                symbolic = False
                if p.endswith(".svg"):
                    txt = open(p, encoding="utf-8", errors="ignore").read()
                    symbolic = is_symbolic(txt)
                hits.append((os.path.join(size, cat, name + ext), p, symbolic))
    return hits


def build_theme():
    if os.path.isdir(THEME):
        shutil.rmtree(THEME)
    os.makedirs(THEME, exist_ok=True)

    changed, copied, symbolic, missing = [], [], [], []
    for name in REQUIRED:
        hits = find_icon(name)
        if not hits:
            missing.append(name)
            continue
        for rel, src, is_sym in hits:
            dst = os.path.join(THEME, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if src.endswith(".svg"):
                txt = open(src, encoding="utf-8", errors="ignore").read()
                if is_sym:
                    # symbolic: JANGAN recolor hex. Warnanya currentColor dan
                    # akan mengikuti warna teks GTK dari tema ORACLE.
                    open(dst, "w", encoding="utf-8").write(txt)
                    symbolic.append(rel)
                else:
                    new = recolor_svg(txt)
                    open(dst, "w", encoding="utf-8").write(new)
                    if new != txt:
                        changed.append(rel)
                    else:
                        copied.append(rel)
            else:
                shutil.copy2(src, dst)
                copied.append(rel)

    # index.theme: inherit ke Papirus supaya ikon lain tetap tersedia
    idx = f"""[Icon Theme]
Name=ORACLE-Papirus
Comment=ORACLE OS icon theme - Papirus with limited accent recolor
Inherits=Papirus,hicolor
Example=folder
FollowsColorScheme=true

DesktopDefault=48
DesktopSizes=16,22,24,32,48,64
ToolbarDefault=22
ToolbarSizes=16,22,24,32,48
MainToolbarDefault=22
MainToolbarSizes=16,22,24,32,48
SmallToolbarDefault=16
SmallToolbarSizes=16,22,24
PanelDefault=22
PanelSizes=16,22,24,32,48
"""
    open(os.path.join(THEME, "index.theme"), "w", encoding="utf-8").write(idx)

    return changed, copied, symbolic, missing


def main():
    os.makedirs(PREV, exist_ok=True)
    os.makedirs(DOCS, exist_ok=True)

    changed, copied, symbolic, missing = build_theme()
    print(f"ikon diubah warnanya   : {len(changed)}")
    print(f"ikon disalin apa adanya: {len(copied)}")
    print(f"ikon symbolic (16x16)  : {len(symbolic)}")
    print(f"ikon tidak ditemukan   : {len(missing)} {missing if missing else ''}")

    # manifest
    lines = ["# ORACLE-Papirus — manifest ikon", "",
             "# sumber: Papirus 20250501-1 (Debian 13 Trixie)",
             f"# total file: {len(changed)+len(copied)+len(symbolic)}", "",
             "## DIUBAH WARNA (aksen -> palet ORACLE)"]
    lines += [f"  {p}" for p in sorted(changed)]
    lines += ["", "## SYMBOLIC (currentColor, tidak di-recolor)"]
    lines += [f"  {p}" for p in sorted(symbolic)]
    lines += ["", "## DISALIN APA ADANYA"]
    lines += [f"  {p}" for p in sorted(copied)]
    if missing:
        lines += ["", "## TIDAK DITEMUKAN (blocker)"]
        lines += [f"  {n}" for n in missing]
    open(os.path.join(ROOT, "manifest.txt"), "w", encoding="utf-8").write(
        "\n".join(lines) + "\n")
    print(f"manifest: {os.path.join(ROOT,'manifest.txt')}")

    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main())