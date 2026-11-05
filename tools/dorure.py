"""Dorure : pose le monogramme / logo L'APLOMB en laiton sur une image
(coffret, carte), en respectant la texture et la lumière de la surface.

- masque : le SVG du logo rendu en haute définition (Playwright)
- couleur : dégradé laiton, modulé par la luminance locale de la surface
  (la dorure passe dans les ombres de la fenêtre comme la toile)
- relief : léger embossage (ombre et reflet décalés d'un pixel)
- matière : un peu de la trame de la toile transparaît

Usage : python tools/dorure.py image.png masque.png sortie.png cx cy largeur
"""
import sys

import numpy as np
from PIL import Image, ImageFilter

LAITON_SOMBRE = np.array([122, 98, 58], np.float32)
LAITON = np.array([183, 155, 106], np.float32)
LAITON_CLAIR = np.array([226, 205, 156], np.float32)


def dorer(base, masque, cx, cy, largeur):
    base = base.convert("RGB")
    m = masque.convert("L")
    h = round(largeur * m.height / m.width)
    m = m.resize((largeur, h), Image.LANCZOS)
    x0, y0 = int(cx - largeur / 2), int(cy - h / 2)
    zone = base.crop((x0, y0, x0 + largeur, y0 + h))
    z = np.asarray(zone, np.float32)
    lum = (z @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None] / 255.0
    lum_flou = np.asarray(Image.fromarray((lum[..., 0] * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6)), np.float32)[..., None] / 255.0
    ref = np.median(lum_flou)
    lumiere = np.clip(lum_flou / max(ref, 1e-3), 0.45, 1.6)          # ombres de fenêtre
    yy, xx = np.mgrid[0:h, 0:largeur].astype(np.float32)
    t = ((xx / largeur) * 0.6 + (yy / h) * 0.4)[..., None]          # reflet en diagonale
    reflet = np.clip(1 - np.abs(t - 0.42) * 2.4, 0, 1)
    or_ = LAITON + (LAITON_CLAIR - LAITON) * reflet * 0.8
    or_ = or_ * (0.55 + 0.45 * lumiere) + (LAITON_SOMBRE - LAITON) * np.clip(1 - lumiere, 0, 1) * 0.6
    trame = (lum - lum_flou) * 255 * 0.35                             # texture de la toile
    or_ = or_ + trame
    a = np.asarray(m, np.float32)[..., None] / 255.0
    # embossage : ombre en bas à droite, reflet en haut à gauche
    ombre = np.roll(np.roll(a, 1, 0), 1, 1) * (1 - a)
    eclat = np.roll(np.roll(a, -1, 0), -1, 1) * (1 - a)
    out = z * (1 - a) + or_ * a
    out = out * (1 - ombre * 0.35) + np.array([255, 245, 220], np.float32) * eclat * 0.12
    base.paste(Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)), (x0, y0))
    return base


if __name__ == "__main__":
    img, masque, dst = sys.argv[1:4]
    cx, cy, largeur = (int(v) for v in sys.argv[4:7])
    dorer(Image.open(img), Image.open(masque), cx, cy, largeur).save(dst)
    print(dst)


def gaufrer(base, masque, cx, cy, largeur, force=0.22):
    """Gaufrage à sec (sans couleur) : seul le relief marque le papier."""
    base = base.convert("RGB")
    m = masque.convert("L")
    h = round(largeur * m.height / m.width)
    m = m.resize((largeur, h), Image.LANCZOS)
    x0, y0 = int(cx - largeur / 2), int(cy - h / 2)
    z = np.asarray(base.crop((x0, y0, x0 + largeur, y0 + h)), np.float32)
    a = np.asarray(m, np.float32)[..., None] / 255.0
    ombre = np.roll(np.roll(a, 1, 0), 1, 1) * (1 - a)
    eclat = np.roll(np.roll(a, -1, 0), -1, 1) * (1 - a)
    out = z * (1 - a * 0.04) * (1 - ombre * force) + np.array([255, 252, 244], np.float32) * eclat * force * 0.5
    base.paste(Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)), (x0, y0))
    return base
