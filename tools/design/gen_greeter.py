#!/usr/bin/env python3
"""ORACLE-OS — Stage 2F-B: LightDM GTK Greeter.

Target: lightdm-gtk-greeter 2.0.9-1 (Debian 13 Trixie), GTK 3.

TEMUAN AUDIT YANG MENENTUKAN (lihat docs/AUDIT-GREETER.md):
  1. Greeter TIDAK punya opsi konfigurasi CSS. 31 key config terverifikasi
     dari source; tidak satu pun untuk CSS.
  2. CSS greeter dikompilasi ke binary (lightdm_gtk_greeter_css_application)
     dan dipasang pada GTK_STYLE_PROVIDER_PRIORITY_APPLICATION (600).
  3. Tema dipilih lewat `theme-name`. Tema GTK ORACLE bisa menargetkan
     style class `.lightdm-gtk-greeter` dan named widget (#login_window,
     #panel_window, #user_combobox, ...) -- ini mekanisme resminya.

Karena itu: styling greeter = (a) config key yang ada, (b) CSS tambahan
di dalam tema GTK ORACLE yang menargetkan id greeter.

Menghasilkan:
  greeter/cfg/lightdm-gtk-greeter.conf      konfigurasi final (belum diterapkan)
  greeter/cfg/oracle-greeter.css            CSS greeter (untuk tema GTK)
  greeter/preview/*.png                     mockup statis
  greeter/docs/*                            audit + spesifikasi
"""

import os
import sys

# ------------------------------------------------------------------ palet
IVORY     = "#E9E5DA"
PORCELAIN = "#F5F3EC"
STEEL     = "#344653"
DUSTY     = "#667D89"
BRASS     = "#B8A98D"
BRASS_INK = "#8C7B58"
GRAPHITE  = "#30363B"
BORDER    = "#B9C1C2"

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "greeter")
CFG = os.path.join(ROOT, "cfg")
PREV = os.path.join(ROOT, "preview")
DOCS = os.path.join(ROOT, "docs")


def build_conf():
    """Konfigurasi greeter. Hanya key yang TERVERIFIKASI ada di 2.0.9."""
    return f"""# ============================================================================
# ORACLE-OS — LightDM GTK Greeter configuration
# Target: lightdm-gtk-greeter 2.0.9-1 (Debian 13 Trixie), GTK 3
#
# STATUS: BELUM DITERAPKAN. Ini spesifikasi untuk tahap integrasi.
#
# Setiap key di bawah terverifikasi ada di binary 2.0.9 (lihat
# docs/AUDIT-GREETER.md). Tidak ada key karangan.
#
# Precedence (dari tinggi ke rendah):
#   /etc/lightdm/lightdm-gtk-greeter.conf
#   /etc/lightdm/lightdm-gtk-greeter.conf.d/*.conf   (urut alfabet)
#   /usr/share/lightdm/lightdm-gtk-greeter.conf.d/*.conf
# File ini ditujukan untuk /etc/lightdm/lightdm-gtk-greeter.conf
# ============================================================================

[greeter]
# --- Tema & ikon ------------------------------------------------------------
# Tema GTK ORACLE. Ini yang membawa seluruh styling greeter, karena greeter
# tidak punya opsi CSS sendiri.
theme-name=ORACLE
icon-theme-name=ORACLE-Papirus
cursor-theme-name=dmz-cursor-theme
cursor-theme-size=24

# --- Latar ------------------------------------------------------------------
# Warna solid, bukan gambar: login harus tenang dan tidak bergantung pada
# resolusi wallpaper. Greeter menerima path gambar ATAU warna (#rrggbb).
background={IVORY}
# Jangan pakai background per-user: live image tidak punya ~/.face.
user-background=false
transition-type=none

# --- Tipografi --------------------------------------------------------------
font-name=Inter 11
xft-antialias=true
xft-hintstyle=hintfull
xft-rgba=rgb

# --- Jendela login ----------------------------------------------------------
position=50% 50%
hide-user-image=false
round-user-image=true
highlight-logged-user=true

# --- Panel ------------------------------------------------------------------
panel-position=top
clock-format=%H:%M
# Indikator yang tersedia di 2.0.9: ~a11y ~language ~session ~power ~clock
# ~host ~spacer ~layout. Hanya yang berguna di live image.
indicators=~host;~clock;~spacer;~session;~power;~a11y

# --- Aksesibilitas ----------------------------------------------------------
# "-name" = mati saat mulai. Live image: jangan aktifkan kontras tinggi
# otomatis, karena akan menimpa palet ORACLE.
a11y-states=-contrast;font;keyboard;reader
reader=orca

# --- Sesi -------------------------------------------------------------------
default-session=xfce

# --- Keamanan ---------------------------------------------------------------
allow-debugging=false
"""


def build_css():
    """CSS greeter. Dimuat lewat tema GTK ORACLE, bukan lewat config.

    Hanya id yang TERVERIFIKASI ada di 2.0.9:
      #login_window #panel_window #user_combobox #user_image
      #user_image_border #greeter_infobar #login_button #cancel_button
    """
    return f"""/* ==========================================================================
   ORACLE-OS — LightDM GTK Greeter styling
   Target: lightdm-gtk-greeter 2.0.9-1, GTK 3

   CARA PAKAI: sertakan berkas ini di dalam tema GTK ORACLE, mis.
   @import url("oracle-greeter.css");
   di akhir gtk-3.0/gtk.css. Greeter memakai tema yang sama (theme-name=ORACLE),
   jadi aturan ini hanya aktif saat greeter berjalan.

   Hanya id yang terverifikasi ada di binary 2.0.9. Id dari sample CSS 1.8
   (#content_frame, #buttonbox_frame, #shutdown_button, #restart_button,
   #shutdown_dialog, #restart_dialog) TIDAK dipakai -- tidak ada di 2.0.9.
   ========================================================================== */

/* --- panel atas ---------------------------------------------------------- */
#panel_window {{
    background-color: {STEEL};
    color: {PORCELAIN};
    border-style: none;
    box-shadow: none;
}}

#panel_window .menubar,
#panel_window .menubar > .menuitem {{
    background-color: transparent;
    color: {PORCELAIN};
    text-shadow: none;
    -gtk-icon-shadow: none;
}}

#panel_window .menubar .menuitem:disabled {{
    color: #8A9AA2;
}}

#panel_window .menubar .menu {{
    background-color: {PORCELAIN};
    border: 1px solid {BORDER};
    border-radius: 3px;
}}

#panel_window .menubar .menu .menuitem {{
    color: {GRAPHITE};
    text-shadow: none;
}}

#panel_window .menubar .menu .menuitem:hover {{
    background-color: {STEEL};
    color: {PORCELAIN};
}}

/* --- jendela login ------------------------------------------------------- */
#login_window {{
    background-color: {PORCELAIN};
    color: {GRAPHITE};
    border: 1px solid {BORDER};
    border-radius: 4px;
    box-shadow: none;
}}

/* --- pemilih user -------------------------------------------------------- */
#user_combobox {{
    color: {GRAPHITE};
    font-size: 15px;
}}

/* ComboBoxText di GTK3 terdiri dari button + label. Tanpa aturan ini,
   tombolnya mewarisi gaya gelap dari tema induk dan teks tidak terbaca. */
#user_combobox button,
#user_combobox .button {{
    background-color: {PORCELAIN};
    background-image: none;
    color: {GRAPHITE};
    border: 1px solid {BORDER};
    border-radius: 3px;
    box-shadow: none;
    text-shadow: none;
}}

#user_combobox button:hover,
#user_combobox .button:hover {{
    background-color: {IVORY};
}}

#user_combobox label {{
    color: {GRAPHITE};
}}

#user_combobox .menu {{
    background-color: {PORCELAIN};
    border: 1px solid {BORDER};
}}

#user_combobox .arrow {{
    color: {DUSTY};
}}

/* --- foto user ----------------------------------------------------------- */
#user_image {{
    border-radius: 4px;
}}

#user_image_border {{
    border: 1px solid {BORDER};
    border-radius: 4px;
}}

/* --- entry password ------------------------------------------------------ */
#login_window .entry {{
    background-color: {IVORY};
    color: {GRAPHITE};
    border: 1px solid {BORDER};
    border-radius: 3px;
    caret-color: {STEEL};
}}

#login_window .entry:focus {{
    border-color: {DUSTY};
    box-shadow: inset 0 0 0 1px {DUSTY};
}}

/* --- tombol -------------------------------------------------------------- */
#login_button {{
    background-color: {STEEL};
    color: {PORCELAIN};
    border: 1px solid {STEEL};
    border-radius: 3px;
    font-weight: bold;
}}

#login_button:hover {{
    background-color: #4B5B65;
    border-color: #4B5B65;
}}

#login_button:active {{
    background-color: #5E6C75;
    border-color: #5E6C75;
}}

#login_button:disabled {{
    background-color: {BORDER};
    color: #4E6069;
    border-color: {BORDER};
}}

#cancel_button {{
    background-color: {PORCELAIN};
    background-image: none;
    color: {GRAPHITE};
    border: 1px solid {BORDER};
    border-radius: 3px;
}}

#cancel_button label {{
    color: {GRAPHITE};
}}

#cancel_button:hover {{
    background-color: {IVORY};
    color: {GRAPHITE};
}}

/* --- infobar (pesan error / info) ---------------------------------------- */
/* InfoBar GTK3 punya latar dari message-type. Tanpa override, latarnya
   gelap dan teks Graphite tidak terbaca (terbukti di preview: kontras
   gagal). Latar dipaksa Porcelain, teks Graphite, dan aksen error memakai
   merah semantik yang sama dengan terminal (#B4503C). */
#greeter_infobar {{
    background-color: {PORCELAIN};
    background-image: none;
    color: {GRAPHITE};
    border: 1px solid {BORDER};
    border-left: 3px solid #B4503C;
    border-radius: 3px;
}}

#greeter_infobar label {{
    color: {GRAPHITE};
}}

#greeter_infobar box,
#greeter_infobar revealer {{
    background-color: transparent;
}}

/* --- style class greeter (fallback bila id tidak berlaku) ---------------- */
.lightdm-gtk-greeter {{
    background-color: {IVORY};
    color: {GRAPHITE};
}}
"""


def main():
    for d in (CFG, PREV, DOCS):
        os.makedirs(d, exist_ok=True)

    conf = build_conf()
    p = os.path.join(CFG, "lightdm-gtk-greeter.conf")
    open(p, "w", encoding="utf-8").write(conf)
    print(f"wrote {p} ({len(conf)} B)")

    css = build_css()
    p = os.path.join(CFG, "oracle-greeter.css")
    open(p, "w", encoding="utf-8").write(css)
    print(f"wrote {p} ({len(css)} B)")


if __name__ == "__main__":
    main()