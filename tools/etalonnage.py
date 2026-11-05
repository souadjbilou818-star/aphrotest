"""Étalonnage maison L'Aplomb : donne la même lumière à toutes les images.

1. Plage tonale tenue dans la palette : noirs légèrement remontés vers ink
   (#1B1D22), blancs plafonnés à chalk (#F3EFE7). Jamais de blanc pur.
2. Légère désaturation (les rouges et verts IA sont souvent trop riches),
   courbe douce pour garder la profondeur, hautes lumières un peu chaudes.
3. Grain argentique fin, identique sur toutes les images (graine fixe) :
   il casse le lissé « IA » de la peau et des matières.
4. Recadrage au ratio du cadre, export JPEG progressif.

Usage : python tools/etalonnage.py entree.png sortie.jpg 3/2 [largeur_max] [focus]
"""
import sys

import numpy as np
from PIL import Image

INK = np.array([27, 29, 34], dtype=np.float32)
CHALK = np.array([243, 239, 231], dtype=np.float32)


def etalonner(im, lift=0.25, contraste=1.08, saturation=0.94, grain=2.4, chaud=0.015, seed=7):
    """Réglages validés sur la soirée (variante C) : profondeur conservée."""
    a = np.asarray(im.convert("RGB"), dtype=np.float32) / 255.0
    lum = (a * np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)).sum(axis=2, keepdims=True)
    a = lum + (a - lum) * saturation                    # désaturation douce
    a = np.clip(0.5 + (a - 0.5) * contraste, 0, 1)      # légère courbe
    lo, hi = INK * lift / 255.0, CHALK / 255.0          # noirs vers ink, blancs plafonnés à chalk
    a = lo + a * (hi - lo)
    a = a + np.clip(lum - 0.55, 0, 1) * np.array([chaud, chaud * 0.4, -chaud * 0.6], dtype=np.float32)
    rng = np.random.default_rng(seed)                   # grain identique partout
    noise = rng.normal(0.0, grain / 255.0, a.shape[:2]).astype(np.float32)[..., None]
    a = a + noise * np.clip(1.0 - np.abs(lum - 0.5) * 1.2, 0.25, 1.0)
    return Image.fromarray(np.clip(a * 255.0 + 0.5, 0, 255).astype(np.uint8))


def recadrer(im, ratio, focus=0.5):
    w, h = im.size
    if w / h > ratio:
        nw = int(h * ratio)
        x = int((w - nw) * focus)
        return im.crop((x, 0, x + nw, h))
    nh = int(w / ratio)
    y = int((h - nh) * focus)
    return im.crop((0, y, w, y + nh))


if __name__ == "__main__":
    src, dst, ratio = sys.argv[1], sys.argv[2], sys.argv[3]
    num, den = (float(x) for x in ratio.split("/"))
    largeur = int(sys.argv[4]) if len(sys.argv) > 4 else 1600
    focus = float(sys.argv[5]) if len(sys.argv) > 5 else 0.5
    im = recadrer(Image.open(src), num / den, focus)
    if im.width > largeur:
        im = im.resize((largeur, round(largeur * im.height / im.width)), Image.LANCZOS)
    etalonner(im).save(dst, "JPEG", quality=82, optimize=True, progressive=True)
    print(dst, im.size)
