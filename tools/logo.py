"""Logo L'APLOMB : monogramme A + logotype + signature, en contours SVG.

- Monogramme dessiné à la main (tracés ci-dessous) : jambage droit plein,
  jambage gauche en délié, barre remplacée par une courbe ample (un port de bras).
- Logotype « L’APLOMB » : Cormorant Garamond 500 (OFL), composé avec HarfBuzz
  (crénage) puis converti en contours. Aucune police n'est nécessaire à l'affichage.
- Signature « PILATES À DOMICILE » : Hanken Grotesk 500, capitales espacées.

Toutes les formes utilisent fill="currentColor" ; le monogramme peut recevoir
une couleur propre via la variable CSS --logo-mono (laiton sur fond sombre).

Usage : python tools/logo.py <dossier_sortie>   (écrit les .svg)
Import : from logo import logo_svg  ->  logo_svg("horizontal" | "compact" | "principal" | "monogramme")
"""
import io
import os
import sys

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")

# ---------- Monogramme (repère 92 × 80) ----------
MONO_W, MONO_H = 92, 80
MONO_PATHS = [
    # jambage droit, plein, avec départ de plume à droite au pied
    "M48.8 10C54.2 22.5 63.6 44.2 73.6 67.4C75.1 70.5 78.6 71.8 83.4 70.8"
    "C80.4 69.8 78.9 67.9 77.9 65.4C69.6 44.6 59.9 22.2 53.6 7.1"
    "C52.9 5.5 51.3 4.9 50.2 5.8L48.8 10Z",
    # crochet de tête, en délié
    "M50.8 5.3C48.3 5.5 45.8 7 43.9 9.7C46.1 7.7 48.5 6.6 50.7 6.6Z",
    # jambage gauche, délié
    "M49.3 8.3L50.3 8.7L28.3 77.3L27.3 77Z",
    # la courbe : délié aux extrémités, plein au sommet
    "M3.5 61.8C19.8 51.6 37.9 46.5 54 48.5C66.2 50.1 77.4 56.6 87.6 67.1"
    "C76.9 58.8 66.2 53.5 54 51.7C38.4 49.6 20.9 53.1 3.5 61.8Z",
]


def _ntos(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


_FONTS = {}


def _font(path, axes):
    key = (path, tuple(sorted(axes.items())))
    if key not in _FONTS:
        f = TTFont(path)
        f.flavor = None
        if "fvar" in f:
            f = instancer.instantiateVariableFont(f, axes)
        buf = io.BytesIO()
        f.save(buf)
        _FONTS[key] = (TTFont(io.BytesIO(buf.getvalue())), buf.getvalue())
    return _FONTS[key]


def text_outline(path, axes, text, size, tracking=0.0):
    """Retourne (d, largeur, hauteur_capitale) pour `text` composé à `size` unités."""
    font, data = _font(path, axes)
    face = hb.Face(data)
    hbfont = hb.Font(face)
    upem = face.upem
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hbfont, buf, {"kern": True, "liga": True})
    k = size / upem
    gs = font.getGlyphSet()
    order = font.getGlyphOrder()
    x, parts = 0, []
    infos, positions = buf.glyph_infos, buf.glyph_positions
    for i, (info, pos) in enumerate(zip(infos, positions)):
        pen = SVGPathPen(gs, ntos=_ntos)
        tp = TransformPen(pen, (k, 0, 0, -k, (x + pos.x_offset) * k, -pos.y_offset * k))
        gs[order[info.codepoint]].draw(tp)
        parts.append(pen.getCommands())
        x += pos.x_advance + (tracking * upem if i < len(infos) - 1 else 0)
    cap = font["OS/2"].sCapHeight * k if getattr(font["OS/2"], "sCapHeight", 0) else size * 0.65
    return " ".join(p for p in parts if p), x * k, cap


SERIF = os.path.join(ASSETS, "cormorant-garamond.woff2")
SANS = os.path.join(ASSETS, "hanken-grotesk.woff2")


def _mono(x, y, h, cls="logo__mono"):
    s = h / MONO_H
    paths = "".join(f'<path d="{d}"/>' for d in MONO_PATHS)
    return f'<g class="{cls}" transform="translate({_ntos(x)} {_ntos(y)}) scale({_ntos(s)})">{paths}</g>'


def logo_svg(variant="horizontal", title="L’Aplomb, Pilates à domicile", css_class="logo"):
    mot_d, mot_w, cap = text_outline(SERIF, {"wght": 500}, "L’APLOMB", 100, tracking=0.035)
    sig_d, sig_w, sig_cap = text_outline(SANS, {"wght": 500}, "PILATES À DOMICILE", 22, tracking=0.32)
    parts = []
    if variant == "monogramme":
        w, h = MONO_W, MONO_H
        parts.append(_mono(0, 0, MONO_H))
    elif variant == "principal":
        mono_h = cap * 2.1
        mono_w = MONO_W * mono_h / MONO_H
        w = max(mot_w, sig_w)
        top = 0
        parts.append(_mono((w - mono_w) / 2, top, mono_h))
        base = top + mono_h + 22 + cap
        parts.append(f'<path class="logo__mot" transform="translate({_ntos((w - mot_w) / 2)} {_ntos(base)})" d="{mot_d}"/>')
        sig_base = base + 34 + sig_cap
        parts.append(f'<path class="logo__sig" transform="translate({_ntos((w - sig_w) / 2)} {_ntos(sig_base)})" d="{sig_d}"/>')
        h = sig_base + 6
    elif variant in ("horizontal", "compact"):
        with_sig = variant == "horizontal"
        mono_h = cap * (1.8 if with_sig else 1.6)
        mono_w = MONO_W * mono_h / MONO_H
        gap = 26
        x_mot = mono_w + gap * 2 + 1
        if with_sig:
            base = cap
            h = cap + sig_cap + 26
            mono_y = (h - mono_h) / 2
        else:
            # compacte : le monogramme dépasse les capitales vers le haut ;
            # tout est décalé pour que rien ne sorte du viewBox
            mono_y = 0
            base = mono_h * 0.9
            h = max(base, mono_h)
        parts.append(_mono(0, mono_y, mono_h))
        filet_y = h * 0.08 if with_sig else base - cap * 1.05
        filet_h = h * 0.84 if with_sig else cap * 1.1
        parts.append(f'<rect class="logo__filet" x="{_ntos(mono_w + gap)}" y="{_ntos(filet_y)}" width="1.2" height="{_ntos(filet_h)}"/>')
        parts.append(f'<path class="logo__mot" transform="translate({_ntos(x_mot)} {_ntos(base)})" d="{mot_d}"/>')
        w = x_mot + max(mot_w, sig_w if with_sig else 0)
        if with_sig:
            parts.append(f'<path class="logo__sig" transform="translate({_ntos(x_mot + (mot_w - sig_w) / 2)} {_ntos(h)})" d="{sig_d}"/>')
    else:
        raise ValueError(variant)
    if variant == "horizontal":
        h += 4  # marge sous la signature
    vb = f"0 0 {_ntos(w)} {_ntos(h)}"
    return (f'<svg class="{css_class} {css_class}--{variant}" viewBox="{vb}" role="img" aria-label="{title}" '
            f'fill="currentColor" xmlns="http://www.w3.org/2000/svg">{"".join(parts)}</svg>')


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "design", "logo")
    os.makedirs(out, exist_ok=True)
    for v in ("principal", "horizontal", "compact", "monogramme"):
        with open(os.path.join(out, f"laplomb-{v}.svg"), "w", encoding="utf-8") as fh:
            fh.write(logo_svg(v))
        print("écrit", v)
