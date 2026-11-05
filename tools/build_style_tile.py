"""Construit design/style-tile.html (dessin injecté, typographie française)
et, si un chemin est donné, une version autonome (polices et JS en ligne)
pour la publication en artefact."""
import base64
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from dessin import dessin  # noqa: E402
from typo_fr import fix_html  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "design", "style-tile.src.html")
OUT = os.path.join(ROOT, "design", "style-tile.html")


def logo(m):
    """<!--@LOGO variante [hidden]--> : insère design/logo/laplomb-<variante>.svg."""
    variant, hidden = m.group(1), bool(m.group(2))
    svg = open(os.path.join(ROOT, "design", "logo", f"laplomb-{variant}.svg"), encoding="utf-8").read().strip()
    svg = svg.replace(' xmlns="http://www.w3.org/2000/svg"', "")
    if hidden:  # dans un lien qui porte déjà son aria-label
        svg = re.sub(r' role="img" aria-label="[^"]*"', ' aria-hidden="true" focusable="false"', svg)
    return svg


def build():
    s = open(SRC, encoding="utf-8").read()
    s = re.sub(r"<!--@LOGO (\w+)( hidden)?-->", logo, s)
    s = s.replace("<!--@DESSIN hero-->", dessin("simple", "root", "dh"))
    s = s.replace("<!--@DESSIN planche-->", dessin("full", "view", "dp"))
    s = fix_html(s)
    open(OUT, "w", encoding="utf-8").write(s)
    return s


def standalone(s, out):
    base = os.path.join(ROOT, "design")

    def data_uri(m):
        path = os.path.normpath(os.path.join(base, m.group(1)))
        b64 = base64.b64encode(open(path, "rb").read()).decode()
        return f'url("data:font/woff2;base64,{b64}")'

    s = re.sub(r'url\("([^"]+\.woff2)"\)', data_uri, s)

    def img_uri(m):
        path = os.path.normpath(os.path.join(base, m.group(1)))
        b64 = base64.b64encode(open(path, "rb").read()).decode()
        return f'src="data:image/jpeg;base64,{b64}"'

    s = re.sub(r'src="(images-ia/[^"]+\.jpg)"', img_uri, s)
    s = re.sub(r'<link rel="preload"[^>]*>\n?', "", s)
    js = open(os.path.join(ROOT, "assets", "aplomb-dessin.js"), encoding="utf-8").read()
    s = s.replace('<script src="../assets/aplomb-dessin.js"></script>', "<script>\n" + js + "\n</script>")
    # l'hôte de l'artefact fournit doctype/html/head/body
    for pat in [r"<!doctype html>\n?", r"<html[^>]*>\n?", r"</?head>\n?", r"<body>\n?", r"</body>\n?", r"</html>\n?",
                r'<meta charset="utf-8">\n?', r'<meta name="viewport"[^>]*>\n?']:
        s = re.sub(pat, "", s, flags=re.I)
    open(out, "w", encoding="utf-8").write(s)


if __name__ == "__main__":
    html = build()
    print("ok:", OUT, len(html))
    if len(sys.argv) > 1:
        standalone(html, sys.argv[1])
        print("autonome:", sys.argv[1])
