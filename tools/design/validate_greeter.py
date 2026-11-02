#!/usr/bin/env python3
"""ORACLE-OS — Stage 2F-B: validator konfigurasi greeter.

Memeriksa:
  1. Setiap key di conf benar-benar ada di binary 2.0.9 (bukan karangan).
  2. Tidak ada key CSS (greeter tidak mendukungnya).
  3. CSS ter-parse GTK3 tanpa error.
  4. Semua id CSS ada di binary.
  5. Kontras pasangan warna kunci.
  6. Preview ada.
Exit != 0 bila ada yang gagal.
"""

import configparser
import os
import re
import subprocess
import sys

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "greeter")
CFG = os.path.join(ROOT, "cfg")
PREV = os.path.join(ROOT, "preview")
BIN = os.path.expanduser(
    "~/.hermes/profiles/doraemon/cache/scratch/oracle-design/deb/greeter/usr/sbin/lightdm-gtk-greeter")

fails = []


def check(cond, label, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {label}" + (f"  {detail}" if detail else ""))
    if not cond:
        fails.append(label)


def lum(h):
    h = h.lstrip("#")
    c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


# ---------------------------------------------------------------- 1. conf
print("=== 1. KONFIGURASI ===")
confp = os.path.join(CFG, "lightdm-gtk-greeter.conf")
check(os.path.exists(confp), "conf ada")

cp = configparser.ConfigParser()
cp.optionxform = str
cp.read(confp)
check("greeter" in cp, "section [greeter] ada")
g = cp["greeter"] if "greeter" in cp else {}

# key harus ada di binary
strings = subprocess.run(["strings", BIN], capture_output=True, text=True).stdout
unknown = [k for k in g.keys() if k not in strings]
check(not unknown, f"semua {len(g)} key ada di binary 2.0.9", str(unknown))

# tidak boleh ada key untuk CSS (greeter tidak mendukungnya).
# PENTING: cocokkan nama key persis, bukan substring. "xft-hintstyle"
# mengandung "style" tetapi itu opsi hinting font Xft, bukan CSS.
CSS_KEYS = {"css", "css-file", "stylesheet", "gtk-css", "style"}
css_keys = [k for k in g.keys() if k.lower() in CSS_KEYS]
check(not css_keys, "tidak ada key CSS (greeter tidak mendukungnya)", str(css_keys))

# nilai wajib
check(g.get("theme-name") == "ORACLE", "theme-name=ORACLE", g.get("theme-name", "-"))
check(g.get("icon-theme-name") == "ORACLE-Papirus", "icon-theme-name=ORACLE-Papirus")
check(g.get("background", "").startswith("#"), "background berupa warna", g.get("background", "-"))
check(g.get("user-background") == "false", "user-background=false")
check(g.get("default-session") == "xfce", "default-session=xfce")
check(g.get("allow-debugging") == "false", "allow-debugging=false")

# indikator harus dari daftar yang ada di binary
inds = [i.strip() for i in g.get("indicators", "").split(";") if i.strip()]
bad_ind = [i for i in inds if i.startswith("~") and i not in strings]
check(not bad_ind, "semua indikator ~ ada di binary", str(bad_ind))

# ---------------------------------------------------------------- 2. CSS
print("\n=== 2. CSS ===")
cssp = os.path.join(CFG, "oracle-greeter.css")
check(os.path.exists(cssp), "css ada")
css = open(cssp, encoding="utf-8").read()

# parse dengan GTK3 sungguhan
probe = os.path.join(os.path.expanduser(
    "~/.hermes/profiles/doraemon/cache/scratch/oracle-design"), "css_check.py")
open(probe, "w").write('''
import gi, sys
gi.require_version("Gtk","3.0")
from gi.repository import Gtk
errs=[]
p=Gtk.CssProvider()
p.connect("parsing-error", lambda pr,sec,e: errs.append(f"{sec.get_start_line()+1}: {e.message}"))
p.load_from_path(sys.argv[1])
print(len(errs))
for e in errs[:10]: print("  ", e)
''')
r = subprocess.run(["/usr/bin/python3", probe, cssp], capture_output=True, text=True)
n_err = int(r.stdout.splitlines()[0]) if r.stdout.strip() else -1
check(n_err == 0, "CSS ter-parse GTK3 tanpa error", f"{n_err} error")
if n_err:
    print(r.stdout)

# semua id CSS harus ada di binary (komentar dibuang dulu: id usang hanya
# disebut di komentar penjelasan, bukan sebagai aturan aktif)
css_active = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
ids = sorted(set(re.findall(r"#([a-z_]+)\s*[{,]", css_active)))
missing_ids = [i for i in ids if i not in strings]
check(not missing_ids, f"semua {len(ids)} id CSS aktif ada di binary 2.0.9", str(missing_ids))

# tidak boleh memakai id dari sample 1.8 yang tidak ada di 2.0.9
STALE = ["content_frame", "buttonbox_frame", "shutdown_button", "restart_button",
         "shutdown_dialog", "restart_dialog"]
used_stale = [s for s in STALE if s in ids]
check(not used_stale, "tidak memakai id usang dari sample 1.8 sebagai selector", str(used_stale))

# ---------------------------------------------------------------- 3. kontras
print("\n=== 3. KONTRAS ===")
IVORY, PORC, STEEL, DUSTY, GRAPH = "#E9E5DA", "#F5F3EC", "#344653", "#667D89", "#30363B"

# Ambil warna disabled dari CSS AKTUAL, bukan konstanta hardcoded.
# Kalau CSS berubah, validator ikut berubah -- tidak bisa "lulus" palsu.
def css_color(selector, prop="color"):
    """Ambil nilai prop dari rule. `prop` dicocokkan sebagai nama properti
    utuh (bukan substring), supaya `color` tidak menangkap `background-color`."""
    m = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", css_active, re.S)
    if not m:
        return None
    body = m.group(1)
    mm = re.search(r"(?<![-a-z])" + prop + r"\s*:\s*(#[0-9a-fA-F]{6})", body)
    return mm.group(1) if mm else None

dis_btn = css_color("#login_button:disabled") or DUSTY
dis_panel = css_color("#panel_window .menubar .menuitem:disabled") or DUSTY
print(f"  (dibaca dari CSS: disabled button={dis_btn}, panel={dis_panel})")

pairs = [
    ("panel fg/bg", PORC, STEEL, 4.5),
    ("login window fg/bg", GRAPH, PORC, 4.5),
    ("entry fg/bg", GRAPH, IVORY, 4.5),
    ("login button fg/bg", PORC, STEEL, 4.5),
    ("cancel fg/bg", GRAPH, PORC, 4.5),
    ("infobar fg/bg", GRAPH, PORC, 4.5),
    ("disabled button", dis_btn, "#B9C1C2", 3.0),
    ("panel disabled", dis_panel, STEEL, 3.0),
]
for name, fg, bg, need in pairs:
    r_ = contrast(fg, bg)
    check(r_ >= need, f"{name} >= {need}", f"{r_:.2f}:1")

# ---------------------------------------------------------------- 4. preview
print("\n=== 4. PREVIEW ===")
for m in ("normal", "focus", "error", "session"):
    p = os.path.join(PREV, f"greeter-{m}.png")
    ok = os.path.exists(p) and os.path.getsize(p) > 3000
    check(ok, f"greeter-{m}.png ada", f"{os.path.getsize(p)} B" if os.path.exists(p) else "hilang")

print("\n" + "=" * 52)
if fails:
    print(f"GAGAL: {len(fails)}")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("SEMUA LULUS")
sys.exit(0)