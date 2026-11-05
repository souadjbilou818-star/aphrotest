"""Génère assets/espace-fine.woff2 : une police d'un seul glyphe pour U+202F
(espace fine insécable), absente des sous-ensembles latins de nos polices.
Déclarée avec unicode-range: U+202F sous le même nom de famille que chaque police."""
import sys
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

ADVANCE = 170  # 0,17 em : proche de l'espace fine typographique
fb = FontBuilder(1000, isTTF=True)
glyphs = [".notdef", "uni202F"]
fb.setupGlyphOrder(glyphs)
fb.setupCharacterMap({0x202F: "uni202F"})
# .notdef reçoit un contour (une table glyf vide est rejetée par le
# validateur OTS des navigateurs) ; l'espace reste vide.
pen = TTGlyphPen(None)
pen.moveTo((50, 0)); pen.lineTo((50, 700)); pen.lineTo((450, 700)); pen.lineTo((450, 0)); pen.closePath()
notdef = pen.glyph()
empty = TTGlyphPen(None).glyph()
fb.setupGlyf({".notdef": notdef, "uni202F": empty})
fb.setupHorizontalMetrics({".notdef": (500, 0), "uni202F": (ADVANCE, 0)})
fb.setupHorizontalHeader(ascent=800, descent=-200)
fb.setupNameTable({"familyName": "Aplomb Espace Fine", "styleName": "Regular"})
fb.setupOS2(sTypoAscender=800, sTypoDescender=-200, usWinAscent=800, usWinDescent=200)
fb.setupPost()
fb.font.flavor = "woff2"
fb.save(sys.argv[1])
