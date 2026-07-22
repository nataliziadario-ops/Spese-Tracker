#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera le icone Android di Spendy a partire da www/icon-512.png.

Perche' serve: Capacitor, quando ricrea il progetto android/, mette le SUE
icone di default. Questo script produce le icone di Spendy (comprese quelle
"adattive" che Android ritaglia in cerchio o quadrato a seconda del telefono)
e le anteprime mostrate nel selettore dei widget.

I file prodotti finiscono in android-icons/res/ e vengono copiati nel progetto
Android durante la build (vedi .github/workflows/build-android.yml).

Uso:  python3 android-icons/genera_icone.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
SRC = os.path.join(REPO, "www", "icon-512.png")
SRC_MASK = os.path.join(REPO, "www", "icon-512-maskable.png")
RES = os.path.join(ROOT, "res")

# Densita' Android: nome cartella -> moltiplicatore
DENSITIES = [("mdpi", 1.0), ("hdpi", 1.5), ("xhdpi", 2.0), ("xxhdpi", 3.0), ("xxxhdpi", 4.0)]

# Colori del tema (coerenti con l'app)
GREEN_DARK = (12, 74, 63)
GREEN = (20, 99, 86)
GREEN_LIGHT = (27, 137, 117)
SURFACE = (30, 35, 31)
INK = (236, 240, 235)
INK_SOFT = (167, 175, 166)
ACCENT = (58, 174, 143)
TRACK = (46, 53, 47)

FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def ensure(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def extract_glyph(img):
    """Isola il simbolo bianco dallo sfondo verde, restituendolo su trasparente."""
    img = img.convert("RGBA")
    w, h = img.size
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    src = img.load()
    dst = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = src[x, y]
            if a == 0:
                continue
            # Quanto e' "bianco" il pixel: il verde ha una componente minima bassa.
            whiteness = min(r, g, b) / 255.0
            v = (whiteness - 0.18) / 0.82
            if v <= 0:
                continue
            if v > 1:
                v = 1.0
            dst[x, y] = (255, 255, 255, int(round(v * a)))
    return out


def crop_to_content(img):
    bbox = img.getbbox()
    return img.crop(bbox) if bbox else img


def round_mask(size):
    m = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(m).ellipse((0, 0, size * 4 - 1, size * 4 - 1), fill=255)
    return m.resize((size, size), Image.LANCZOS)


def make_launcher_icons():
    base = Image.open(SRC).convert("RGBA")
    mask_src = Image.open(SRC_MASK).convert("RGBA")
    glyph = crop_to_content(extract_glyph(mask_src))

    made = []
    for name, mult in DENSITIES:
        d = os.path.join(RES, "mipmap-" + name)
        ensure(d)

        # 1) Icona classica (Android 7 e precedenti): 48dp
        size = int(round(48 * mult))
        base.resize((size, size), Image.LANCZOS).save(os.path.join(d, "ic_launcher.png"))
        made.append("mipmap-%s/ic_launcher.png (%dpx)" % (name, size))

        # 2) Icona tonda: ritaglio circolare della versione piena
        rnd = mask_src.resize((size, size), Image.LANCZOS)
        circ = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        circ.paste(rnd, (0, 0), round_mask(size))
        circ.save(os.path.join(d, "ic_launcher_round.png"))
        made.append("mipmap-%s/ic_launcher_round.png (%dpx)" % (name, size))

        # 3) Primo piano per l'icona adattiva: tela 108dp, simbolo entro il 60%
        #    (Android ritaglia i bordi: fuori dalla zona centrale non e' garantito)
        canvas = int(round(108 * mult))
        safe = int(canvas * 0.60)
        fg = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
        gw, gh = glyph.size
        scale = min(safe / float(gw), safe / float(gh))
        nw, nh = max(1, int(gw * scale)), max(1, int(gh * scale))
        fg.paste(glyph.resize((nw, nh), Image.LANCZOS),
                 ((canvas - nw) // 2, (canvas - nh) // 2))
        fg.save(os.path.join(d, "ic_spendy_foreground.png"))
        made.append("mipmap-%s/ic_spendy_foreground.png (%dpx)" % (name, canvas))
    return made


def rounded_card(w, h, radius, color):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, fill=color + (255,))
    return img


def make_widget_previews():
    """Anteprime mostrate nel selettore dei widget di Android."""
    d = os.path.join(RES, "drawable-nodpi")
    ensure(d)
    fb = ImageFont.truetype(FONT_B, 26)
    fbs = ImageFont.truetype(FONT_B, 19)
    fr = ImageFont.truetype(FONT_R, 15)
    frs = ImageFont.truetype(FONT_R, 14)
    made = []

    # --- Anteprima widget semplice ---
    w, h = 320, 150
    img = rounded_card(w, h, 34, SURFACE)
    dr = ImageDraw.Draw(img)
    dr.text((26, 30), "lug", font=frs, fill=INK_SOFT)
    dr.text((26, 54), "1.240,00 €", font=fb, fill=INK)
    dr.text((26, 96), "Speso: 385,00 €", font=fr, fill=ACCENT)
    img.save(os.path.join(d, "widget_preview_simple.png"))
    made.append("drawable-nodpi/widget_preview_simple.png")

    # --- Anteprima widget completo ---
    w, h = 460, 240
    img = rounded_card(w, h, 34, SURFACE)
    dr = ImageDraw.Draw(img)
    dr.text((26, 24), "lug", font=frs, fill=INK_SOFT)
    dr.text((26, 46), "1.240,00 €", font=fb, fill=INK)
    dr.text((300, 56), "Speso: 385 €", font=frs, fill=ACCENT)
    dr.text((26, 96), "Spesa · 172 / 250 €", font=frs, fill=INK_SOFT)
    dr.rounded_rectangle((26, 118, 434, 130), radius=6, fill=TRACK + (255,))
    dr.rounded_rectangle((26, 118, 26 + int(408 * 0.69), 130), radius=6, fill=ACCENT + (255,))
    rows = [("Conad", "−32,40 €"), ("Stipendio", "+1.500,00 €"), ("Bar", "−4,20 €")]
    y = 150
    for name, amt in rows:
        dr.text((26, y), name, font=frs, fill=INK)
        tw = dr.textlength(amt, font=frs)
        dr.text((434 - tw, y), amt, font=frs, fill=INK_SOFT)
        y += 26
    img.save(os.path.join(d, "widget_preview_rich.png"))
    made.append("drawable-nodpi/widget_preview_rich.png")

    # --- Anteprima widget spesa rapida ---
    w, h = 460, 180
    img = rounded_card(w, h, 34, SURFACE)
    dr = ImageDraw.Draw(img)
    dr.text((26, 24), "Spesa rapida", font=fbs, fill=INK)
    bw, bh, gap = 128, 82, 14
    labels = [("🛒", "Spesa"), ("🍽", "Cibo"), ("＋", "Altro")]
    x = 26
    for i, (emo, lab) in enumerate(labels):
        col = ACCENT if i == 2 else TRACK
        dr.rounded_rectangle((x, 66, x + bw, 66 + bh), radius=18, fill=col + (255,))
        tw = dr.textlength(lab, font=frs)
        dr.text((x + (bw - tw) / 2, 66 + bh - 30), lab, font=frs,
                fill=(13, 16, 14) if i == 2 else INK)
        x += bw + gap
    img.save(os.path.join(d, "widget_preview_quick.png"))
    made.append("drawable-nodpi/widget_preview_quick.png")
    return made


def main():
    ensure(RES)
    made = make_launcher_icons() + make_widget_previews()
    print("Generati %d file:" % len(made))
    for m in made:
        print("  ·", m)


if __name__ == "__main__":
    main()
