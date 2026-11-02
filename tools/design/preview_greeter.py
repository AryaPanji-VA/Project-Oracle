#!/usr/bin/env python3
"""ORACLE-OS — Stage 2F-B: preview greeter (render GTK3 sungguhan).

Merender widget GTK3 dengan CSS greeter ORACLE memakai Gtk.OffscreenWindow.
Ini BUKAN tangkapan LightDM sungguhan: tidak ada greeter, tidak ada PAM,
tidak ada session. Label MOCKUP STATIS dicetak di gambar.
"""

import os
import subprocess
import sys

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "greeter")
CFG = os.path.join(ROOT, "cfg")
PREV = os.path.join(ROOT, "preview")
os.makedirs(PREV, exist_ok=True)

SCRIPT = r'''
import gi, sys, os
gi.require_version("Gtk", "3.0"); gi.require_version("Gdk", "3.0")
gi.require_version("Pango", "1.0")
from gi.repository import Gtk, Gdk, Pango

CSS, OUT, MODE = sys.argv[1], sys.argv[2], sys.argv[3]

prov = Gtk.CssProvider()
prov.load_from_path(CSS)
Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), prov,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

IVORY="#E9E5DA"; PORCELAIN="#F5F3EC"; STEEL="#344653"; DUSTY="#667D89"
GRAPHITE="#30363B"; BORDER="#B9C1C2"

def ui(size, bold=False):
    for p in ([os.path.join(os.path.expanduser(
        "~/.hermes/profiles/doraemon/cache/scratch/oracle-design/deb/inter/usr/share/fonts/opentype/inter"),
        "Inter-SemiBold.otf")] if bold else [os.path.join(os.path.expanduser(
        "~/.hermes/profiles/doraemon/cache/scratch/oracle-design/deb/inter/usr/share/fonts/opentype/inter"),
        "Inter-Regular.otf")]):
        if os.path.exists(p):
            return p
    return "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# ---- root: latar Ivory (background=#E9E5DA)
win = Gtk.OffscreenWindow()
win.set_default_size(900, 560)
# Latar window diset eksplisit: kelas .lightdm-gtk-greeter hanya dipasang
# oleh greeter sungguhan, tidak oleh OffscreenWindow. Di greeter nyata,
# config `background=#E9E5DA` yang mengisi latar ini.
win.override_background_color(Gtk.StateFlags.NORMAL,
    Gdk.RGBA(*[int(IVORY[i:i+2],16)/255 for i in (1,3,5)], 1.0))
root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
root.get_style_context().add_class("lightdm-gtk-greeter")
win.add(root)

# ---- panel atas (Steel)
panel = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
panel.set_name("panel_window")
panel.set_size_request(-1, 32)
root.pack_start(panel, False, False, 0)

def lbl(text, color, size=11, bold=False):
    l = Gtk.Label(label=text)
    l.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(*[int(color[i:i+2],16)/255 for i in (1,3,5)], 1.0))
    l.override_font(Pango.FontDescription(f"Inter {size}" + (" Bold" if bold else "")))
    return l

panel.pack_start(lbl("oracle-os", PORCELAIN, 11, True), False, False, 8)
sp = Gtk.Box(); panel.pack_start(sp, True, True, 0)
panel.pack_start(lbl("14:32", PORCELAIN, 11, True), False, False, 8)

# ---- area tengah: jendela login
center = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
center.set_valign(Gtk.Align.CENTER)
center.set_halign(Gtk.Align.CENTER)
root.pack_start(center, True, True, 0)

login = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
login.set_name("login_window")
login.set_border_width(22)
login.set_size_request(340, -1)
center.pack_start(login, False, False, 0)

# user image (kotak)
img = Gtk.Box()
img.set_name("user_image")
img.set_size_request(64, 64)
img.set_halign(Gtk.Align.CENTER)
login.pack_start(img, False, False, 0)

# user combobox
combo = Gtk.ComboBoxText()
combo.set_name("user_combobox")
combo.append_text("oracle")
combo.set_active(0)
login.pack_start(combo, False, False, 0)

# password entry
entry = Gtk.Entry()
entry.set_placeholder_text("Password")
entry.set_visibility(False)
entry.get_style_context().add_class("entry")
login.pack_start(entry, False, False, 0)

if MODE == "error":
    info = Gtk.InfoBar()
    info.set_name("greeter_infobar")
    info.set_message_type(Gtk.MessageType.ERROR)
    info.get_content_area().add(Gtk.Label(label="Incorrect password"))
    login.pack_start(info, False, False, 0)

# tombol
btnbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
btnbox.set_halign(Gtk.Align.CENTER)
cancel = Gtk.Button(label="Cancel"); cancel.set_name("cancel_button")
loginb = Gtk.Button(label="Log In"); loginb.set_name("login_button")
if MODE == "focus":
    loginb.grab_focus()
if MODE == "disabled":
    loginb.set_sensitive(False)
btnbox.pack_start(cancel, False, False, 0)
btnbox.pack_start(loginb, False, False, 0)
login.pack_start(btnbox, False, False, 0)

# session selector (mode session)
if MODE == "session":
    sess = Gtk.ComboBoxText()
    sess.append_text("XFCE Session")
    sess.set_active(0)
    login.pack_start(sess, False, False, 0)

win.show_all()
for _ in range(40):
    while Gtk.events_pending(): Gtk.main_iteration()
w, h = win.get_size()
Gdk.pixbuf_get_from_window(win.get_window(), 0, 0, w, h).savev(OUT, "png", [], [])
print(f"saved {OUT} {w}x{h}")
'''


def main():
    script = os.path.join(os.path.expanduser(
        "~/.hermes/profiles/doraemon/cache/scratch/oracle-design"), "greeter_preview.py")
    open(script, "w").write(SCRIPT)
    css = os.path.join(CFG, "oracle-greeter.css")
    for mode in ("normal", "focus", "error", "session"):
        out = os.path.join(PREV, f"greeter-{mode}.png")
        r = subprocess.run(["/usr/bin/python3", script, css, out, mode],
                           capture_output=True, text=True)
        print(r.stdout.strip() or r.stderr.strip()[:200])


if __name__ == "__main__":
    main()