"""Dessin technique du mini-reformer L’Aplomb (SVG + calques HTML).

Une seule source pour la style tile et, plus tard, snippets/dessin-reformer.liquid.
Repère : viewBox 0 0 1200 760 ; vue de dessus en haut, élévation en bas.
Le chariot (et ce qui l'accompagne) est animé par la variable CSS --p (0 -> 1)
sur une course de COURSE unités. Les élastiques s'étirent depuis l'ancrage.

Aucune cote chiffrée : les cotes portent des lettres (A-D). Les valeurs
viendront des metafields de la fiche technique, si elles sont renseignées.
"""

W, H = 1200, 760
COURSE = 420
ANCRE_X = 136
CHARIOT_X = 200
REPOS = CHARIOT_X - ANCRE_X  # longueur des élastiques au repos


def f(v):
    return f"{v:g}"


def line(x1, y1, x2, y2, cls):
    return f'<line class="{cls}" x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}"/>'


def rect(x, y, w, h, cls, rx=0):
    r = f' rx="{f(rx)}"' if rx else ""
    return f'<rect class="{cls}" x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}"{r}/>'


def circle(cx, cy, r, cls):
    return f'<circle class="{cls}" cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}"/>'


def tick(x, y):
    return line(x - 6, y + 6, x + 6, y - 6, "d-c d-c--tick")


def cote_h(x1, x2, y, ext_from):
    """Cote horizontale ; lignes d'attache depuis ext_from (au-dessus ou en dessous)."""
    d = 8 if ext_from < y else -8
    out = [line(x1, ext_from, x1, y + d, "d-c"), line(x2, ext_from, x2, y + d, "d-c"), line(x1, y, x2, y, "d-c")]
    out += [tick(x1, y), tick(x2, y)]
    return "".join(out)


def cote_v(y1, y2, x, ext_from):
    d = 8 if ext_from < x else -8
    out = [line(ext_from, y1, x + d, y1, "d-c"), line(ext_from, y2, x + d, y2, "d-c"), line(x, y1, x, y2, "d-c")]
    out += [tick(x, y1), tick(x, y2)]
    return "".join(out)


def lcg(seed):
    while True:
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        yield seed / 0x7FFFFFFF


def fil_du_bois(x1, x2, ys, seed):
    """Fil du bois : traits fins interrompus."""
    rnd = lcg(seed)
    out = []
    for y in ys:
        x = x1 + next(rnd) * 40
        while x < x2 - 30:
            seg = 80 + next(rnd) * 260
            end = min(x + seg, x2 - 8)
            out.append(line(round(x), y, round(end), y, "d-f"))
            x = end + 18 + next(rnd) * 60
    return "".join(out)


ELEV_DY = {"simple": -160, "full": -90}  # le hero resserre l'élévation sous la vue de dessus


def svg(detail="simple", uid="d"):
    dy = ELEV_DY[detail]
    h = H + dy
    plan, elev = [], []
    # ---------- VUE DE DESSUS ----------
    plan.append(rect(100, 70, 1000, 240, "d-o d-fill"))
    plan.append(fil_du_bois(108, 1092, [84, 98, 112, 146, 176, 204, 232, 268, 284, 298], 7))
    plan.append(line(80, 190, 1120, 190, "d-ax"))  # axe longitudinal
    for y in (127, 133, 247, 253):
        plan.append(line(150, y, 1050, y, "d-t"))
    for x in (146, 1046):
        for y in (122, 242):
            plan.append(rect(x, y, 8, 16, "d-t d-fill"))
    plan.append(rect(110, 104, 26, 172, "d-o d-fill"))  # barre d'ancrage
    plan.append(rect(590, 74, 20, 14, "d-t d-fill"))
    plan.append(rect(590, 292, 20, 14, "d-t d-fill"))
    plan.append(line(600, 56, 600, 324, "d-ax"))  # axe de pliage
    plan_el = "".join(line(ANCRE_X, y, CHARIOT_X, y, "d-e") for y in (160, 220))
    plan_cr = "".join(circle(ANCRE_X, y, 3.5, "d-t d-fill") for y in (160, 220))
    plan_ch = [rect(200, 96, 240, 188, "d-o d-fill", 10), rect(214, 110, 212, 160, "d-f2", 6)]
    plan_ch += [circle(x, y, 8, "d-h") for x in (230, 410) for y in (130, 250)]

    # ---------- ÉLÉVATION ----------
    elev.append(line(60, 660, 1140, 660, "d-o"))
    elev.append("".join(line(x, 660, x - 12, 672, "d-f") for x in range(78, 1141, 18)))
    elev.append(rect(130, 650, 46, 10, "d-t d-fill"))
    elev.append(rect(1024, 650, 46, 10, "d-t d-fill"))
    elev.append(rect(100, 626, 1000, 24, "d-o d-fill"))
    elev.append(fil_du_bois(106, 1094, [633, 640, 645], 11))
    elev.append(rect(150, 616, 900, 10, "d-t d-fill"))
    elev.append(rect(144, 604, 12, 22, "d-t d-fill"))
    elev.append(rect(1044, 604, 12, 22, "d-t d-fill"))
    elev.append(rect(110, 560, 26, 66, "d-o d-fill"))  # montant d'ancrage
    elev.append(circle(600, 650, 5, "d-t d-fill"))
    elev.append(line(600, 596, 600, 676, "d-ax"))
    elev_el = "".join(line(ANCRE_X, y, CHARIOT_X, y, "d-e") for y in (584, 592))
    elev_cr = "".join(circle(ANCRE_X, y, 3.5, "d-t d-fill") for y in (584, 592))
    elev_ch = [
        rect(200, 566, 240, 36, "d-o d-fill", 8),
        rect(212, 602, 216, 6, "d-t d-fill"),
        circle(236, 608, 8, "d-o d-fill"),
        circle(404, 608, 8, "d-o d-fill"),
        circle(236, 608, 1.8, "d-dot"),
        circle(404, 608, 1.8, "d-dot"),
    ]

    # ---------- COTES (oxblood) ----------
    cote_plan = cote_v(70, 310, 1150, 1104)                       # B largeur
    cote_elev = (cote_h(100, 1100, 712, 654)                      # A longueur dépliée
                 + cote_h(CHARIOT_X, CHARIOT_X + COURSE, 536, 560)  # C course du chariot
                 + cote_v(560, 660, 72, 106))                     # D hauteur hors tout

    lead_plan, lead_elev, lead_mob = [], [], []
    if detail == "full":
        for (x1, y1, x2, y2) in [(900, 253, 900, 345), (168, 220, 168, 345), (600, 306, 600, 345)]:
            lead_plan.append(line(x1, y1, x2, y2, "d-l") + circle(x1, y1, 2.4, "d-dot"))
        for (x1, y1, x2, y2) in [(880, 640, 900, 580), (123, 560, 123, 500), (1060, 655, 1110, 590)]:
            lead_elev.append(line(x1, y1, x2, y2, "d-l") + circle(x1, y1, 2.4, "d-dot"))
        for (x1, y1, x2, y2) in [(330, 96, 330, 40), (410, 122, 410, 40)]:
            lead_mob.append(line(x1, y1, x2, y2, "d-l") + circle(x1, y1, 2.4, "d-dot"))

    title = "Dessin technique du mini-reformer L’Aplomb"
    desc = ("Vue de dessus et élévation. Un plateau en bois porte deux rails en acier ; "
            "le chariot roule sur ces rails, retenu par des élastiques fixés à une barre d'ancrage. "
            "Le plateau se plie en son milieu. Cotes : A longueur dépliée, B largeur, "
            "C course du chariot, D hauteur hors tout.")
    return (
        f'<svg class="dessin__svg" viewBox="0 0 {W} {h}" role="img" aria-labelledby="{uid}-t {uid}-d" focusable="false">'
        f'<title id="{uid}-t">{title}</title><desc id="{uid}-d">{desc}</desc>'
        f'<g class="d-vue d-vue--dessus">{"".join(plan)}'
        f'<g class="d-elastiques">{plan_el}</g>{plan_cr}'
        f'<g class="d-chariot">{"".join(plan_ch)}{"".join(lead_mob)}</g>'
        f'<g class="d-cotes">{cote_plan}</g><g class="d-leaders">{"".join(lead_plan)}</g></g>'
        f'<g class="d-vue d-vue--elevation" transform="translate(0 {dy})">{"".join(elev)}'
        f'<g class="d-elastiques">{elev_el}</g>{elev_cr}'
        f'<g class="d-chariot">{"".join(elev_ch)}</g>'
        f'<g class="d-cotes">{cote_elev}</g><g class="d-leaders">{"".join(lead_elev)}</g></g>'
        "</svg>"
    )


def pos(x, y, h=H):
    return f"left:{x / W * 100:.3f}%;top:{y / h * 100:.3f}%"


def calques(detail="simple"):
    dy = ELEV_DY[detail]
    h = H + dy
    # (lettre, x, y, vue) ; vue "e" = élévation, décalée de dy
    cotes = [("A", 600, 698, "e"), ("B", 1176, 190, "p"), ("C", 410, 520, "e"), ("D", 44, 610, "e")]
    out = ['<div class="dessin__calques" aria-hidden="true">']
    for lettre, x, y, v in cotes:
        yy = y + (dy if v == "e" else 0)
        out.append(f'<span class="cote" data-cote="{lettre}" style="{pos(x, yy, h)}">{lettre}</span>')
    if detail == "full":
        fixes = [(1, 900, 580, "e"), (2, 900, 345, "p"), (5, 168, 345, "p"), (6, 123, 500, "e"),
                 (7, 600, 345, "p"), (8, 1110, 590, "e")]
        for n, x, y, v in fixes:
            yy = y + (dy if v == "e" else 0)
            out.append(f'<span class="bulle" style="{pos(x, yy, h)}">{n}</span>')
        out.append('<div class="dessin__mobile">')
        for n, x, y in [(3, 330, 40), (4, 410, 40)]:
            out.append(f'<span class="bulle" style="{pos(x, y, h)}">{n}</span>')
        out.append("</div>")
    out.append("</div>")
    return "".join(out)


def dessin(detail="simple", timeline="view", uid="d"):
    return (
        f'<aplomb-dessin class="dessin" data-timeline="{timeline}" data-detail="{detail}">'
        f'<div class="dessin__plan">{svg(detail, uid)}{calques(detail)}</div>'
        "</aplomb-dessin>"
    )


CSS_VARS = {
    "--course-cq": f"{COURSE / W * 100:.4f}cqw",
    "--etirement": f"{COURSE / REPOS:.4f}",
}

if __name__ == "__main__":
    print(dessin("full", "view"))
