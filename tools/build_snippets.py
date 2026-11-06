"""Génère les snippets Liquid du thème à partir des sources Python :

- snippets/dessin-coulisse.liquid  (tools/dessin.py) : COULISSE 01, deux
  variantes, « simple » (hero) et « full » (fiche technique), cotes alimentées
  par les metafields aplomb.longueur_mm, largeur_mm, course_mm,
  longueur_plie_mm, hauteur_mm ;
- snippets/logo.liquid             (design/logo/*.svg) : principal,
  horizontal, compact, monogramme ;
- snippets/frise.liquid            : frise point de Hongrie.

Usage : python3 tools/build_snippets.py
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import dessin  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNIP = os.path.join(ROOT, "snippets")
GEN = "{% comment %} Fichier généré par tools/build_snippets.py : ne pas modifier à la main. {% endcomment %}\n"

COTES = {"A": "cote_a", "B": "cote_b", "C": "cote_c", "D": "cote_d", "E": "cote_e"}


def variante(detail):
    html = dessin.dessin(detail, "@@TIMELINE@@", "{{ uid }}")
    # libellés de cote : lettre, puis valeur si le metafield est rempli
    for lettre, var in COTES.items():
        html = html.replace(
            f'data-cote="{lettre}" style=',
            f'data-cote="{lettre}" style=',
        )
        html = re.sub(
            rf'(<span class="cote[^"]*" data-cote="{lettre}" style="[^"]*">){lettre}(</span>)',
            rf'\g<1>{lettre}{{% if {var} != blank %}} · {{{{ {var} }}}} mm{{% endif %}}\g<2>',
            html,
        )
    return html.replace('data-timeline="@@TIMELINE@@"', 'data-timeline="{{ timeline }}"')


def dessin_snippet():
    doc = """{% doc %}
  Dessin technique de COULISSE 01 : vue de dessus, élévation, vue pliée (full).
  Les deux plateaux coulissent l'un après l'autre au défilement
  (CSS scroll-driven, repli assets/aplomb-dessin.js).
  Les cotes A à E affichent leur valeur seulement si le metafield est rempli.

  @param {string} [detail] - 'simple' (hero) ou 'full' (repères et nomenclature)
  @param {string} [timeline] - 'root' (défilement de la page) ou 'view' (passage du dessin à l'écran)
  @param {object} [product] - produit dont on lit les metafields aplomb.*
  @param {string} [uid] - identifiant unique pour les attributs id du SVG
{% enddoc %}
"""
    liquid = """{%- liquid
  assign detail = detail | default: 'simple'
  assign timeline = timeline | default: 'view'
  assign uid = uid | default: 'dessin'
  assign cote_a = product.metafields.aplomb.longueur_mm.value
  assign cote_b = product.metafields.aplomb.largeur_mm.value
  assign cote_c = product.metafields.aplomb.course_mm.value
  assign cote_d = product.metafields.aplomb.longueur_plie_mm.value
  assign cote_e = product.metafields.aplomb.hauteur_mm.value
-%}
"""
    body = "{%- if detail == 'full' -%}\n" + variante("full") + "\n{%- else -%}\n" + variante("simple") + "\n{%- endif -%}\n"
    return GEN + doc + liquid + body


def logo_snippet():
    out = [GEN, """{% doc %}
  Logo L'Aplomb en SVG (tracés, aucune police nécessaire).

  @param {string} [variante] - 'principal', 'horizontal', 'compact' ou 'monogramme'
  @param {string} [class] - classe CSS ajoutée au SVG
  @param {boolean} [decoratif] - true quand le lien parent porte déjà le nom
{% enddoc %}
{%- liquid
  assign variante = variante | default: 'compact'
  if decoratif
    assign a11y = 'aria-hidden="true" focusable="false"'
  else
    assign signature = settings.signature | escape
    capture a11y
      echo 'role="img" aria-label="L’Aplomb, ' | append: signature | append: '"'
    endcapture
  endif
-%}
"""]
    variants = ["principal", "horizontal", "compact", "monogramme"]
    for i, v in enumerate(variants):
        svg = open(os.path.join(ROOT, "design", "logo", f"laplomb-{v}.svg"), encoding="utf-8").read().strip()
        svg = svg.replace(' xmlns="http://www.w3.org/2000/svg"', "")
        svg = re.sub(r' role="img" aria-label="[^"]*"', " {{ a11y }}", svg)
        svg = svg.replace(f'class="logo logo--{v}"', f'class="logo logo--{v} {{{{ class }}}}"')
        kw = "if" if i == 0 else "elsif"
        out.append(f"{{%- {kw} variante == '{v}' -%}}\n{svg}\n")
    out.append("{%- endif -%}\n")
    return "".join(out)


def frise_snippet():
    sp, h = 16, 40
    m = h // 2
    polys = []
    for x in range(-2 * sp, 2 * sp, sp):
        cls = "lame lame--a" if (x // sp) % 2 == 0 else "lame lame--b"
        polys.append(f'<polygon class="{cls}" points="{x},{m} {x + sp},{m} {x + sp + m},0 {x + m},0"/>')
        polys.append(f'<polygon class="{cls}" points="{x},{m} {x + sp},{m} {x + sp + m},{h} {x + m},{h}"/>')
    return GEN + """{% doc %}
  Frise point de Hongrie (parquet), purement décorative.

  @param {string} id - identifiant unique du motif
{% enddoc %}
<svg class="frise" aria-hidden="true" focusable="false"><defs><pattern id="frise-{{ id }}" width="32" height="40" patternUnits="userSpaceOnUse">""" + "".join(polys) + f"""</pattern></defs><rect x="-1" y="0" width="102%" height="{h}" fill="url(#frise-{{{{ id }}}})"/><line class="joint" x1="0" y1=".5" x2="100%" y2=".5"/><line class="joint" x1="0" y1="{h - .5}" x2="100%" y2="{h - .5}"/></svg>
"""


if __name__ == "__main__":
    for name, content in [("dessin-coulisse", dessin_snippet()), ("logo", logo_snippet()), ("frise", frise_snippet())]:
        with open(os.path.join(SNIP, f"{name}.liquid"), "w", encoding="utf-8") as fh:
            fh.write(content)
        print("snippets/%s.liquid" % name, len(content))
