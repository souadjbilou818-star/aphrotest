"""Microtypographie française sur tout le thème (idempotent).

- .liquid : nœuds de texte (via typo_fr.fix_html) + chaînes du {% schema %}
- templates/*.json, sections/*-group.json : valeurs de réglages textuels
- locales/*.json : toutes les chaînes
- config/settings_schema.json : libellés et valeurs par défaut des champs texte

Ne touche jamais aux identifiants, types, valeurs d'options ni aux URL.
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from typo_fr import fix_html, fix_text  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLES_TEXTE = {"default", "label", "info", "content", "name", "placeholder"}
NE_PAS_TOUCHER = {"type", "id", "value", "unit", "ancre", "ratio", "taille", "mode", "image", "video", "menu"}


def propre(s):
    if not isinstance(s, str) or not s.strip():
        return s
    if s.startswith(("shopify://", "http", "#", "/")):
        return s
    return fix_html(s) if ("<" in s or "{{" in s or "{%" in s) else fix_text(s)


def schema(obj, parent_type=None):
    if isinstance(obj, dict):
        t = obj.get("type", parent_type)
        out = {}
        for k, v in obj.items():
            if k in CLES_TEXTE and isinstance(v, str) and not (k == "default" and t in ("select", "radio", "link_list", "checkbox")):
                out[k] = propre(v)
            else:
                out[k] = schema(v, t if k != "options" else "options")
        return out
    if isinstance(obj, list):
        return [schema(v, parent_type) for v in obj]
    return obj


def reglages(obj, cle=None):
    if isinstance(obj, dict):
        return {k: (v if k in NE_PAS_TOUCHER else reglages(v, k)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [reglages(v, cle) for v in obj]
    if isinstance(obj, str) and cle not in ("type",):
        return propre(obj)
    return obj


def toutes_chaines(obj):
    if isinstance(obj, dict):
        return {k: toutes_chaines(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [toutes_chaines(v) for v in obj]
    return propre(obj) if isinstance(obj, str) else obj


def lire_json(path):
    raw = open(path, encoding="utf-8").read()
    m = re.match(r"\s*(/\*.*?\*/)\s*", raw, re.S)
    entete = m.group(1) + "\n" if m else ""
    return entete, json.loads(raw[m.end():] if m else raw)


def ecrire_json(path, entete, data):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(entete + json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def liquid(path):
    src = open(path, encoding="utf-8").read()
    out = fix_html(src)

    def sch(m):
        data = json.loads(m.group(2))
        return m.group(1) + json.dumps(schema(data), ensure_ascii=False, indent=2) + "\n" + m.group(3)

    out = re.sub(r"(\{%-?\s*schema\s*-?%\}\s*)(.*?)(\{%-?\s*endschema\s*-?%\})", sch, out, flags=re.S)
    if out != src:
        open(path, "w", encoding="utf-8").write(out)
        return True
    return False


if __name__ == "__main__":
    modifies = []
    for p in glob.glob(os.path.join(ROOT, "sections", "*.liquid")) + glob.glob(os.path.join(ROOT, "snippets", "*.liquid")) \
            + glob.glob(os.path.join(ROOT, "layout", "*.liquid")) + glob.glob(os.path.join(ROOT, "blocks", "*.liquid")) \
            + glob.glob(os.path.join(ROOT, "templates", "*.liquid")):
        if liquid(p):
            modifies.append(p)
    for p in glob.glob(os.path.join(ROOT, "templates", "*.json")) + glob.glob(os.path.join(ROOT, "sections", "*-group.json")):
        entete, data = lire_json(p)
        nouveau = reglages(data)
        if nouveau != data:
            ecrire_json(p, entete, nouveau)
            modifies.append(p)
    for p in glob.glob(os.path.join(ROOT, "locales", "*.json")):
        entete, data = lire_json(p)
        nouveau = toutes_chaines(data)
        if nouveau != data:
            ecrire_json(p, entete, nouveau)
            modifies.append(p)
    p = os.path.join(ROOT, "config", "settings_schema.json")
    entete, data = lire_json(p)
    nouveau = schema(data)
    if nouveau != data:
        ecrire_json(p, entete, nouveau)
        modifies.append(p)
    for m in modifies:
        print("typo:", os.path.relpath(m, ROOT))
