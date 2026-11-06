"""Dessin technique de COULISSE 01 (SVG + calques HTML).

COULISSE 01 est une planche compacte et pliable : deux plateaux rembourrés
coulissent indépendamment sur des rails intégrés, un sur chaque moitié ; des
cordons de résistance à poignées s'accrochent aux deux extrémités. Ce n'est
pas un reformer : pas de chariot unique, pas de ressorts, pas de barre de pieds.

Repère : viewBox 0 0 1200 H. Vue de dessus en haut, élévation au milieu,
vue pliée en bas (variante « full » seulement).

Animation : la variable CSS --p (0 -> 1) pilote deux courses décalées.
--pg (plateau gauche) va de 0 à 1 sur p ∈ [0 ; 0,625], --pd (plateau droit)
sur p ∈ [0,375 ; 1]. Les deux plateaux bougent donc l'un sans l'autre.

Aucune cote chiffrée dans le dessin : les cotes portent des lettres (A-E).
Les valeurs viennent des metafields aplomb.*_mm quand ils sont remplis.
"""

W = 1260  # largeur du viewBox (origine décalée de OX)
OX = -30
COURSE = 240  # course d'un plateau, en unités du viewBox
PLAT_W, PLAT_H = 180, 170
GX = 400  # plateau gauche au repos (x de gauche)
DX = 620  # plateau droit au repos
Y0, Y1 = 80, 300  # planche, vue de dessus
CY = (Y0 + Y1) / 2
EL = 0  # décalage vertical de l'élévation (variante)
HAUTEURS = {"simple": 620, "full": 790}


def f(v):
    return f"{v:g}"


def line(x1, y1, x2, y2, cls):
    return f'<line class="{cls}" x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}"/>'


def rect(x, y, w, h, cls, rx=0):
    r = f' rx="{f(rx)}"' if rx else ""
    return f'<rect class="{cls}" x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}"{r}/>'


def circle(cx, cy, r, cls):
    return f'<circle class="{cls}" cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}"/>'


def path(d, cls):
    return f'<path class="{cls}" d="{d}"/>'


def tick(x, y):
    return line(x - 6, y + 6, x + 6, y - 6, "d-c d-c--tick")


def cote_h(x1, x2, y, ext_from):
    d = 8 if ext_from < y else -8
    out = [line(x1, ext_from, x1, y + d, "d-c"), line(x2, ext_from, x2, y + d, "d-c"), line(x1, y, x2, y, "d-c")]
    return "".join(out) + tick(x1, y) + tick(x2, y)


def cote_v(y1, y2, x, ext_from):
    d = 8 if ext_from < x else -8
    out = [line(ext_from, y1, x + d, y1, "d-c"), line(ext_from, y2, x + d, y2, "d-c"), line(x, y1, x, y2, "d-c")]
    return "".join(out) + tick(x, y1) + tick(x, y2)


def plateau_dessus(x):
    """Plateau rembourré, vue de dessus : coussin, surpiqûre, zone d'appui."""
    y = CY - PLAT_H / 2
    out = [rect(x, y, PLAT_W, PLAT_H, "d-o d-fill", 14)]
    out.append(rect(x + 12, y + 12, PLAT_W - 24, PLAT_H - 24, "d-f2", 8))
    for i in range(1, 4):
        yy = y + 12 + i * (PLAT_H - 24) / 4
        out.append(line(x + 26, yy, x + PLAT_W - 26, yy, "d-f"))
    return "".join(out)


def plateau_elevation(x, base):
    """Plateau en élévation : coussin, semelle, galets sur le rail."""
    out = [rect(x, base - 30, PLAT_W, 22, "d-o d-fill", 9)]
    out.append(rect(x + 10, base - 8, PLAT_W - 20, 6, "d-t d-fill"))
    for gx in (x + 34, x + PLAT_W - 34):
        out.append(circle(gx, base - 1, 5, "d-o d-fill"))
        out.append(circle(gx, base - 1, 1.4, "d-dot"))
    return "".join(out)


def poignee(cx, cy):
    """Poignée en D, posée hors de la planche."""
    return path(
        f"M{f(cx - 10)} {f(cy - 22)} h20 a10 10 0 0 1 10 10 v24 a10 10 0 0 1 -10 10 h-20 a10 10 0 0 1 -10 -10 v-24 a10 10 0 0 1 10 -10 z",
        "d-o d-fill",
    ) + line(cx - 4, cy - 12, cx - 4, cy + 12, "d-t")


def svg(detail="simple", uid="d"):
    h = HAUTEURS[detail]
    fixe, gauche, droite = [], [], []

    # ---------- VUE DE DESSUS ----------
    fixe.append(rect(100, Y0, 1000, Y1 - Y0, "d-o d-fill", 18))
    fixe.append(line(80, CY, 1120, CY, "d-ax"))
    # rails intégrés, deux par moitié
    for (xa, xb) in ((146, 584), (616, 1054)):
        for y in (CY - 62, CY - 56, CY + 56, CY + 62):
            fixe.append(line(xa, y, xb, y, "d-t"))
        for x in (xa, xb - 6):
            for y in (CY - 66, CY + 52):
                fixe.append(rect(x, y, 6, 14, "d-t d-fill"))
    # embouts et points d'ancrage des cordons
    for x in (100, 1062):
        fixe.append(rect(x, Y0 + 10, 38, Y1 - Y0 - 20, "d-t", 10))
    for x in (119, 1081):
        for y in (CY - 40, CY + 40):
            fixe.append(circle(x, y, 6, "d-t d-fill"))
            fixe.append(circle(x, y, 1.6, "d-dot"))
    # charnière de pliage
    fixe.append(line(600, Y0 - 18, 600, Y1 + 18, "d-ax"))
    fixe.append(rect(592, Y0 + 2, 16, 26, "d-t d-fill", 3))
    fixe.append(rect(592, Y1 - 28, 16, 26, "d-t d-fill", 3))
    # cordons et poignées, de part et d'autre
    for (ax, hx, sens) in ((119, 44, -1), (1081, 1156, 1)):
        for y in (CY - 40, CY + 40):
            hy = CY + (y - CY) * 1.55
            fixe.append(path(f"M{f(ax)} {f(y)} C{f(ax + sens * 40)} {f(y)} {f(hx - sens * 36)} {f(hy)} {f(hx - sens * 14)} {f(hy)}", "d-e"))
            fixe.append(poignee(hx, hy))

    gauche.append(plateau_dessus(GX))
    droite.append(plateau_dessus(DX))

    # ---------- ÉLÉVATION ----------
    sol = 560
    fixe.append(line(60, sol, 1140, sol, "d-o"))
    fixe.append("".join(line(x, sol, x - 12, sol + 12, "d-f") for x in range(78, 1141, 18)))
    for x in (124, 1036):
        fixe.append(rect(x, sol - 8, 40, 8, "d-t d-fill"))  # patins antidérapants
    fixe.append(rect(100, sol - 30, 1000, 22, "d-o d-fill", 6))
    fixe.append(rect(146, sol - 36, 438, 6, "d-t d-fill"))
    fixe.append(rect(616, sol - 36, 438, 6, "d-t d-fill"))
    fixe.append(circle(600, sol - 19, 7, "d-o d-fill"))
    fixe.append(circle(600, sol - 19, 1.8, "d-dot"))
    fixe.append(line(600, sol - 70, 600, sol + 18, "d-ax"))
    gauche.append(plateau_elevation(GX, sol - 36))
    droite.append(plateau_elevation(DX, sol - 36))

    # ---------- VUE PLIÉE (full) ----------
    if detail == "full":
        pb = 700
        fixe.append(line(60, pb, 660, pb, "d-o"))
        fixe.append("".join(line(x, pb, x - 12, pb + 12, "d-f") for x in range(78, 661, 18)))
        fixe.append(rect(124, pb - 8, 40, 8, "d-t d-fill"))
        fixe.append(rect(100, pb - 30, 500, 22, "d-o d-fill", 6))
        fixe.append(rect(100, pb - 88, 500, 22, "d-o d-fill", 6))
        fixe.append(rect(146, pb - 66, 438, 36, "d-h", 4))  # plateaux rangés entre les moitiés
        fixe.append(path(f"M600 {pb - 77} a29 29 0 0 1 0 58", "d-o"))
        fixe.append(circle(611, pb - 48, 6, "d-t d-fill"))

    # ---------- COTES ----------
    cotes = cote_v(Y0, Y1, 1204, 1186)                                   # B largeur
    cotes += cote_h(GX - COURSE, GX, Y0 - 34, Y0 + 4)                     # C course d'un plateau
    cotes += cote_h(100, 1100, sol + 44, sol + 4)                         # A longueur dépliée
    cotes += cote_v(sol - 66, sol, 40, 96)                                # E hauteur hors tout
    if detail == "full":
        cotes += cote_h(100, 600, 744, 704)                               # D longueur pliée

    lead = []
    if detail == "full":
        leaders = [
            (300, CY + 59, 300, 352),      # 3 rails
            (600, Y1 - 15, 600, 352),      # 4 charnière
            (70, CY + 62, 70, 352),        # 5 cordons
            (1156, CY + 62 + 22, 1156, 352),  # 6 poignées
            (144, sol - 4, 144, 600),      # 7 patins
        ]
        for (x1, y1, x2, y2) in leaders:
            lead.append(line(x1, y1, x2, y2, "d-l") + circle(x1, y1, 2.4, "d-dot"))

    title = "Dessin technique de COULISSE 01"
    desc = (
        "Vue de dessus, élévation" + (" et vue pliée" if detail == "full" else "") + ". "
        "Une planche pliable en son milieu porte des rails intégrés ; sur chaque moitié, "
        "un plateau rembourré coulisse indépendamment de l’autre. Des cordons de résistance "
        "à poignées s’accrochent aux deux extrémités. Ce n’est pas un reformer à chariot. "
        "Cotes : A longueur dépliée, B largeur, C course d’un plateau, E hauteur"
        + (", D longueur pliée." if detail == "full" else ".")
    )
    return (
        f'<svg class="dessin__svg" viewBox="{OX} 0 {W} {h}" role="img" aria-labelledby="{uid}-t {uid}-d" focusable="false">'
        f'<title id="{uid}-t">{title}</title><desc id="{uid}-d">{desc}</desc>'
        f'<g class="d-fixe">{"".join(fixe)}</g>'
        f'<g class="d-plateau d-plateau--g">{"".join(gauche)}</g>'
        f'<g class="d-plateau d-plateau--d">{"".join(droite)}</g>'
        f'<g class="d-cotes">{cotes}</g><g class="d-leaders">{"".join(lead)}</g>'
        "</svg>"
    )


def pos(x, y, h):
    return f"left:{(x - OX) / W * 100:.3f}%;top:{y / h * 100:.3f}%"


def calques(detail="simple"):
    h = HAUTEURS[detail]
    sol = 560
    cotes = [("A", 600, sol + 44), ("B", 1204, CY), ("C", GX - COURSE / 2, Y0 - 34), ("E", 40, sol - 33)]
    if detail == "full":
        cotes.append(("D", 350, 744))
    out = ['<div class="dessin__calques" aria-hidden="true">']
    for lettre, x, y in cotes:
        v = " cote--v" if lettre in ("B", "E") else ""
        out.append(f'<span class="cote{v}" data-cote="{lettre}" style="{pos(x, y, h)}">{lettre}</span>')
    if detail == "full":
        for n, x, y in [(3, 300, 368), (4, 600, 368), (5, 70, 368), (6, 1156, 368), (7, 144, 616)]:
            out.append(f'<span class="bulle" style="{pos(x, y, h)}">{n}</span>')
        out.append(f'<div class="dessin__mobile dessin__mobile--g"><span class="bulle" style="{pos(GX + PLAT_W / 2, CY, h)}">1</span></div>')
        out.append(f'<div class="dessin__mobile dessin__mobile--d"><span class="bulle" style="{pos(DX + PLAT_W / 2, CY, h)}">2</span></div>')
    out.append("</div>")
    return "".join(out)


def dessin(detail="simple", timeline="view", uid="d"):
    return (
        f'<aplomb-dessin class="dessin" data-timeline="{timeline}" data-detail="{detail}">'
        f'<div class="dessin__plan">{svg(detail, uid)}{calques(detail)}</div>'
        "</aplomb-dessin>"
    )


# valeurs reprises par le CSS (assets/aplomb-components.css)
CSS_VARS = {
    "course": f"{COURSE}px",
    "course-cq": f"{COURSE / W * 100:.4f}cqw",
}

if __name__ == "__main__":
    print(CSS_VARS)
    print(dessin("full", "view"))
