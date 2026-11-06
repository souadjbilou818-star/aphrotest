"""Microtypographie française pour les fichiers HTML/Liquid d'Aplomb.

Ne touche qu'aux nœuds de texte (jamais au contenu de <style>, <script>,
aux balises Liquid {% %} / {{ }} ni aux attributs, sauf alt, title,
aria-label, placeholder et content).

Règles appliquées :
- apostrophe droite entre deux lettres -> ’
- « … » : espace fine insécable (U+202F) à l'intérieur
- ; ! ? : espace fine insécable (U+202F) avant
- :      : espace insécable (U+00A0) avant
- nombre + unité (€, %, mm, cm, kg, min…) : espace insécable
- espace avant un tiret cadratin : insécable
- ... -> …
"""
import re
import sys

NNBSP = "\u202f"
NBSP = "\u00a0"

UNITS = r"(€|%|mm|cm|m|kg|g|min|minutes|secondes|séances|semaines|jours|questions|élastiques|patins|h)\b"


ENTITY_RE = re.compile(r"(&#?\w+;)")


def fix_text(s: str) -> str:
    """Applique les règles en laissant intactes les entités HTML (&amp;, &nbsp;…)."""
    if not s.strip():
        return s
    if "&" in s:
        return "".join(part if ENTITY_RE.fullmatch(part) else _fix(part) for part in ENTITY_RE.split(s))
    return _fix(s)


def _fix(s: str) -> str:
    # apostrophes
    s = re.sub(r"(?<=\w)'(?=\w)", "’", s)
    # guillemets
    s = re.sub(r"«[ \u00a0\u202f]*", "«" + NNBSP, s)
    s = re.sub(r"[ \u00a0\u202f]*»", NNBSP + "»", s)
    # ponctuation haute
    s = re.sub(r"[ \u00a0\u202f]+([;!?])", NNBSP + r"\1", s)
    s = re.sub(r"(?<=[\w»)])([;!?])(?=\s|$|<)", NNBSP + r"\1", s)
    # deux-points (pas dans les heures 10:30 ni les URL)
    s = re.sub(r"[ \u00a0\u202f]+:(?=\s|$)", NBSP + ":", s)
    # nombres + unités
    s = re.sub(r"(\d)[ \u00a0\u202f]+" + UNITS, r"\1" + NBSP + r"\2", s)
    # tiret cadratin
    s = re.sub(r" — ", NBSP + "— ", s)
    s = s.replace("...", "…")
    return s


ATTR_RE = re.compile(r'(\s(?:alt|title|aria-label|placeholder|content)=")([^"]*)(")')
TOKEN_RE = re.compile(r"(<!--.*?-->|<[^>]+>|\{%-?.*?-?%\}|\{\{-?.*?-?\}\})", re.S)


def fix_html(src: str) -> str:
    out = []
    skip = None  # 'style' | 'script' | 'raw'
    for tok in TOKEN_RE.split(src):
        if not tok:
            continue
        if TOKEN_RE.fullmatch(tok):
            low = tok.lower()
            if skip:
                if (skip == "style" and low.startswith("</style")) or (
                    skip == "script" and low.startswith("</script")
                ) or (skip == "raw" and re.match(r"\{%-?\s*(endschema|endjavascript|endstylesheet|endraw)", low)):
                    skip = None
                out.append(tok)
                continue
            if low.startswith("<style"):
                skip = "style"
            elif low.startswith("<script"):
                skip = "script"
            elif re.match(r"\{%-?\s*(schema|javascript|stylesheet|raw)\b", low):
                skip = "raw"
            if tok.startswith("<") and not tok.startswith("<!--"):
                tok = ATTR_RE.sub(
                    lambda m: m.group(0) if ("{{" in m.group(2) or "{%" in m.group(2))
                    else m.group(1) + fix_text(m.group(2)) + m.group(3),
                    tok,
                )
            out.append(tok)
        else:
            out.append(tok if skip else fix_text(tok))
    return "".join(out)


if __name__ == "__main__":
    for path in sys.argv[1:]:
        with open(path, encoding="utf-8") as fh:
            data = fh.read()
        fixed = fix_html(data)
        if fixed != data:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(fixed)
            print("typo:", path)
