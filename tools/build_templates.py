"""Écrit templates/index.json et templates/product.json (textes de la marque).

Le texte est saisi ici en français courant ; tools/typo_theme.py applique
ensuite la microtypographie (espaces fines, apostrophes, guillemets).
Les images générées sont référencées dans Shopify > Contenu > Fichiers
(shopify://shop_images/…) ; un cadre sans image affiche sa didascalie.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTETE = """/*
 * ------------------------------------------------------------
 * IMPORTANT: The contents of this file are auto-generated.
 *
 * This file may be updated by the Shopify admin theme editor
 * or related systems. Please exercise caution as any changes
 * made to this file may be overwritten.
 * ------------------------------------------------------------
 */
"""


def blocs(prefixe, items):
    """items : liste de (type, settings) -> (blocks, block_order)."""
    blocks, order = {}, []
    for i, (t, s) in enumerate(items, 1):
        bid = f"{prefixe}_{i}"
        blocks[bid] = {"type": t, "settings": s}
        order.append(bid)
    return blocks, order


def section(t, settings, items=None, prefixe="b"):
    sec = {"type": t, "settings": settings}
    if items:
        sec["blocks"], sec["block_order"] = blocs(prefixe, items)
    return sec


def img(nom):
    return f"shopify://shop_images/{nom}"


FAQ_COMMUNE = [
    ("question", {"question": "Quelle différence entre Essentiel et Studio ?",
                  "reponse": "<p>L'Essentiel contient le mini-reformer, 4 élastiques, les poignées et le programme « 28 jours d'aplomb ». Le Studio ajoute des chaussettes grip, une housse en toile avec sangle de rangement, 4 patins feutre, une bande forte et un programme de 8 semaines avec une visio collective par mois.</p>"}),
    ("question", {"question": "Quand sera-t-il expédié ?",
                  "reponse": "<p>[DATE D'EXPÉDITION]. Les personnes inscrites sur la liste d'attente sont prévenues en premier.</p>"}),
    ("question", {"question": "La réservation prioritaire, c'est quoi ?",
                  "reponse": "<p>19 € pour réserver votre mini-reformer avant l'ouverture des ventes. Ils sont déduits du prix final et remboursables à tout moment, sur simple demande.</p>"}),
    ("question", {"question": "Puis-je le renvoyer ?",
                  "reponse": "<p>Oui. Vous disposez de 14 jours après réception pour changer d'avis. Les conditions figurent sur la page Livraison & retours.</p>"}),
    ("question", {"question": "Est-ce adapté si je débute ?",
                  "reponse": "<p>Oui. La première semaine du programme est consacrée à l'alignement, sans enchaînement difficile. Douleurs, grossesse ou post-partum : demandez l'avis de votre médecin ou kiné.</p>"}),
]


def index():
    sections = {
        "hero": section("hero-feuille", {
            "label_gauche": "Feuille de salle n° 1",
            "label_droite": "Pré-lancement · Paris",
            "titre": "Le mini-reformer à chariot,",
            "titre_italique": "pensé pour l'appartement.",
            "sous_titre": "Plateau bois, rails acier, chariot sur roues silencieuses. Se range debout derrière une porte.",
            "afficher_dessin": True,
            "legende_dessin": "Planche 01 — vue de dessus et élévation. Faites défiler : le chariot glisse sur ses rails.",
        }, [
            ("preuve", {"texte": "Un vrai chariot sur rails acier"}),
            ("preuve", {"texte": "Élastiques plutôt que ressorts"}),
            ("preuve", {"texte": "Le prix de quatre séances en studio"}),
            ("sommaire", {"num": "I.", "titre": "Le chariot", "ancre": "#chariot", "folio": "2"}),
            ("sommaire", {"num": "II.", "titre": "L'appartement", "ancre": "#appartement", "folio": "3"}),
            ("sommaire", {"num": "III.", "titre": "Le programme", "ancre": "#programme", "folio": "4"}),
            ("sommaire", {"num": "—", "titre": "Entracte : le quiz", "ancre": "#entracte", "folio": "5"}),
            ("sommaire", {"num": "IV.", "titre": "La maison", "ancre": "#maison", "folio": "6"}),
        ], "hero"),
        "chariot": section("acte-chariot", {
            "ancre": "chariot", "num": "I.", "titre": "Le chariot", "folio": "2",
            "intro": "Le cœur de L'Aplomb : un chariot qui roule sur deux rails d'acier, comme au studio.",
            "honnete": "Un vrai chariot sur rails, avec des élastiques plutôt que des ressorts de studio.",
            "afficher_dessin": True,
            "titre_dessin": "Planche 02 · nomenclature",
            "titre_comparatif": "Trois façons de faire du reformer",
            "col_board": "Board plastique 5-en-1", "col_aplomb": "L'Aplomb", "col_studio": "Reformer de studio",
        }, [
            ("ligne", {"critere": "Mouvement", "board": "Plateau fixe, sans chariot", "aplomb": "Chariot sur rails acier, roues PU", "studio": "Chariot sur rails"}),
            ("ligne", {"critere": "Résistance", "board": "Élastiques", "aplomb": "Élastiques", "studio": "Ressorts"}),
            ("ligne", {"critere": "Matière", "board": "Plastique", "aplomb": "Plateau bois, rails acier", "studio": "Cadre bois ou métal"}),
            ("ligne", {"critere": "Rangement", "board": "À plat", "aplomb": "Plié, debout derrière une porte", "studio": "Une pièce dédiée"}),
            ("ligne", {"critere": "Coût", "board": "—", "aplomb": "179 € ou 229 €, une fois", "studio": "25 à 45 € la séance"}),
        ], "ligne"),
        "appartement": section("acte-faits", {
            "ancre": "appartement", "num": "II.", "titre": "L'appartement", "folio": "3",
            "intro": "Pensé pour un deux-pièces, pas pour une salle de sport.",
            "frise": True,
        }, [
            ("fait", {"titre": "Rangé debout", "texte": "<p>Plié en deux sur sa charnière, il tient debout derrière une porte ou dans un placard. Pas besoin d'une pièce en plus.</p>"}),
            ("fait", {"titre": "Le bruit", "texte": "<p>Des roues en polyuréthane roulent sur des rails en acier. La vidéo du plan 03 est tournée avec le son réel : vous jugerez sur pièce.</p>"}),
            ("fait", {"titre": "Le parquet", "texte": "<p>Quatre patins en feutre isolent le plateau du sol. Ils sont livrés avec l'édition Studio.</p>"}),
            ("cadre", {"ratio": "4/5", "plan": "05", "legende": "rangé debout contre une moulure", "generee": True,
                       "didascalie": "Le mini-reformer plié, debout contre une porte à moulures. Un pan de rideau en velours forest dans le champ."}),
            ("cadre", {"ratio": "3/2", "plan": "08", "legende": "les feutres sur le parquet", "generee": True,
                       "didascalie": "Au ras du sol : les patins feutre sous le plateau, sur le point de Hongrie. Lumière rasante."}),
        ], "fait"),
        "programme": section("acte-programme", {
            "ancre": "programme", "num": "III.", "titre": "Le programme", "folio": "4",
            "intro": "« 28 jours d'aplomb » : 4 semaines, 4 séances de 20 minutes par semaine. Accès par QR code.",
            "encart_titre": "Édition Studio",
            "encart_texte": "Le programme se prolonge sur 8 semaines, avec une visio collective chaque mois.",
            "plan": "06", "legende": "la discipline privée, gainage latéral", "generee": True, "ratio": "4/5",
            "image": img("plan-06-posture-provisoire.jpg"),
            "didascalie": "Trois postures, de profil, à hauteur de sol. Corps aligné, visage calme.",
        }, [
            ("semaine", {"numero": "S1", "titre": "Alignement", "texte": "Trouver l'axe : bassin, cage thoracique, épaules."}),
            ("semaine", {"numero": "S2", "titre": "Centre", "texte": "Le travail profond de la sangle abdominale, chariot lent."}),
            ("semaine", {"numero": "S3", "titre": "Chaîne postérieure", "texte": "Fessiers, ischio-jambiers, dos : pousser loin, revenir sans à-coup."}),
            ("semaine", {"numero": "S4", "titre": "Flow complet", "texte": "Les enchaînements des trois semaines, en une séance fluide."}),
        ], "semaine"),
        "entracte": section("entracte-quiz", {
            "ancre": "entracte", "label": "Entracte", "titre": "Quelle édition pour vous ?",
            "texte": "Cinq questions, deux minutes. Le résultat présélectionne l'édition ; l'e-mail reste facultatif.",
            "email": True,
            "note": "Douleurs, grossesse ou post-partum : demandez l'avis de votre médecin ou kiné.",
        }),
        "maison": section("acte-maison", {
            "ancre": "maison", "num": "IV.", "titre": "La maison", "folio": "6",
            "texte": "<p>L'Aplomb est né à Paris d'un constat simple : le reformer a changé notre façon de bouger, mais il ne tient ni dans un budget ni dans un deux-pièces. Nous avons gardé l'essentiel, un chariot qui glisse sur des rails, et retiré le reste. Pour pratiquer avec justesse, chez soi, avec aplomb.</p>",
            "transparence": "Sélectionné et contrôlé à Paris, fabriqué par une usine partenaire. Le nom et l'adresse du fabricant figurent sur la page Sécurité produit.",
            "soir_label": "La maison, le soir",
            "soir_titre": "L'élégance publique.",
            "soir_titre_2": "La discipline privée.",
        }, [
            ("cadre", {"image": img("plan-09-soiree.jpg"), "generee": True, "ratio": "3/2", "plan": "09",
                       "legende": "l'élégance publique, une soirée, de dos"}),
        ], "soir"),
        "faq": section("faq", {"ancre": "faq", "titre": "Questions", "folio": "7"}, FAQ_COMMUNE, "q"),
        "rappel": section("rappel-liste", {
            "ancre": "rappel", "titre": "La liste d'attente est ouverte.",
            "intro": "Nous vous écrivons à l'ouverture des réservations, et pas avant.",
        }),
    }
    order = ["hero", "chariot", "appartement", "programme", "entracte", "maison", "faq", "rappel"]
    return {"sections": sections, "order": order}


def product():
    plans = [
        ("plan", {"ratio": "1/1", "taille": "moitie", "plan": "02", "legende": "rails et roues, en macro", "generee": True,
                  "didascalie": "Macro. Mise au point sur une roue, le rail fuit en diagonale."}),
        ("plan", {"ratio": "16/9", "taille": "moitie", "plan": "03", "son": True, "generee": False,
                  "legende": "le chariot en mouvement, son réel",
                  "didascalie": "Le chariot fait un aller-retour sur toute sa course. Micro près des rails, aucune musique."}),
        ("plan", {"ratio": "4/5", "taille": "tiers", "plan": "04", "legende": "le pliage, premier temps", "generee": True,
                  "didascalie": "Vu du dessus : le mini-reformer déplié, deux mains posées sur la charnière."}),
        ("plan", {"ratio": "4/5", "taille": "tiers", "plan": "04", "legende": "le pliage, deuxième temps", "generee": True,
                  "didascalie": "Même cadrage : le plateau à moitié replié sur sa charnière."}),
        ("plan", {"ratio": "4/5", "taille": "tiers", "plan": "04", "legende": "le pliage, troisième temps", "generee": True,
                  "didascalie": "Même cadrage : plié, prêt à être rangé debout."}),
        ("plan", {"ratio": "4/5", "taille": "moitie", "plan": "05", "legende": "rangé debout contre une moulure", "generee": True,
                  "didascalie": "Plié, debout contre une porte à moulures. Un pan de rideau en velours forest dans le champ."}),
        ("plan", {"ratio": "4/5", "taille": "moitie", "plan": "06", "legende": "la discipline privée, gainage latéral", "generee": True,
                  "image": img("plan-06-posture-provisoire.jpg")}),
        ("plan", {"ratio": "3/2", "taille": "large", "plan": "07", "legende": "le coffret, dorure laiton, carte gaufrée", "generee": True,
                  "image": img("plan-07-coffret.jpg")}),
        ("plan", {"ratio": "3/2", "taille": "moitie", "plan": "08", "legende": "les feutres sur le parquet", "generee": True,
                  "didascalie": "Au ras du sol : les patins feutre sous le plateau, sur le point de Hongrie. Lumière rasante."}),
        ("plan", {"ratio": "3/2", "taille": "moitie", "plan": "10", "legende": "la housse de l'édition Studio", "generee": True,
                  "didascalie": "La housse en toile et sa sangle, suspendues à une patère en laiton, sur une porte laquée."}),
    ]
    sections = {
        "main": section("produit-principal", {
            "surtitre": "Pré-lancement · Paris",
            "sous_titre": "Plateau bois, rails acier, chariot sur roues silencieuses. Se range debout derrière une porte.",
            "contenu_essentiel": "Le mini-reformer, 4 élastiques, les poignées, le programme « 28 jours d'aplomb ».",
            "contenu_studio": "L'Essentiel, plus chaussettes grip, housse en toile avec sangle de rangement, 4 patins feutre, 1 bande forte, programme 8 semaines.",
            "prix_studio": "Une séance de reformer à Paris coûte 25 à 45 €. L'Aplomb, c'est le prix de quatre séances.",
            "legende_dessin": "Planche 01 — vue de dessus et élévation. Les cotes s'affichent quand la fiche technique est remplie.",
        }, [
            ("preuve", {"texte": "Un vrai chariot sur rails acier"}),
            ("preuve", {"texte": "Se range debout derrière une porte"}),
            ("preuve", {"texte": "Programme « 28 jours d'aplomb » inclus"}),
        ] + plans, "p"),
        "benefices": section("benefices", {"titre": "Ce qu'il change", "ancre": "benefices"}, [
            ("benefice", {"titre": "Le travail du reformer, à la maison",
                          "texte": "Le chariot glisse, le corps travaille contre les élastiques : le principe du reformer, sans le trajet ni le créneau."}),
            ("benefice", {"titre": "20 minutes, sans sortir",
                          "texte": "Chaque séance du programme dure 20 minutes. Vous la faites quand la journée le permet."}),
            ("benefice", {"titre": "Rangé en 10 secondes",
                          "texte": "Plié sur sa charnière, il se range debout derrière une porte. Le salon redevient un salon."}),
        ], "ben"),
        "etapes": section("etapes", {"titre": "Comment ça marche", "ancre": "comment"}, [
            ("etape", {"titre": "Dépliez", "texte": "Posez le plateau au sol et ouvrez la charnière.", "plan": "04", "legende": "déplier",
                       "didascalie": "Vu du dessus : deux mains ouvrent la charnière sur le parquet."}),
            ("etape", {"titre": "Accrochez", "texte": "Choisissez vos élastiques et fixez-les à la barre d'ancrage.", "plan": "02", "legende": "accrocher",
                       "didascalie": "Gros plan : un élastique accroché à la barre d'ancrage."}),
            ("etape", {"titre": "Glissez", "texte": "Flashez le QR code et lancez la séance du jour.", "plan": "06", "legende": "glisser",
                       "didascalie": "De profil : le chariot en fin de course, le corps aligné."}),
        ], "et"),
        "negations": section("negations", {
            "titre": "Ce que ce n'est pas", "ancre": "honnetete",
            "honnete": "Un vrai chariot sur rails, avec des élastiques plutôt que des ressorts de studio.",
        }, [
            ("negation", {"non": "Pas de ressorts", "explication": "La résistance vient d'élastiques interchangeables. Elle est plus douce en début de course, plus franche en fin de course."}),
            ("negation", {"non": "Pas un appareil de deux mètres", "explication": "Un plateau qui se plie et se range debout, conçu pour un appartement."}),
            ("negation", {"non": "Pas un board en plastique", "explication": "Un vrai chariot sur roues, qui roule sur des rails en acier."}),
            ("negation", {"non": "Pas une promesse de silhouette", "explication": "Un travail juste et régulier, 20 minutes à la fois."}),
        ], "neg"),
        "specs": section("specs", {
            "titre": "Fiche technique", "ancre": "fiche-technique",
            "intro": "Les mesures s'affichent dès qu'elles sont vérifiées. Aucun chiffre n'est publié avant.",
        }, [
            ("role", {"role": "Plateau", "nom": "bois"}),
            ("role", {"role": "Rails", "nom": "acier"}),
            ("role", {"role": "Chariot", "nom": "roues PU silencieuses"}),
            ("role", {"role": "Résistance", "nom": "élastiques"}),
            ("role", {"role": "Pliage", "nom": "charnière centrale"}),
        ], "spec"),
        "programme": section("acte-programme", {
            "ancre": "programme", "titre": "Le programme inclus",
            "intro": "« 28 jours d'aplomb » : 4 semaines, 4 séances de 20 minutes par semaine. Accès par QR code.",
            "encart_titre": "Édition Studio",
            "encart_texte": "Le programme se prolonge sur 8 semaines, avec une visio collective chaque mois.",
        }, [
            ("semaine", {"numero": "S1", "titre": "Alignement", "texte": "Trouver l'axe : bassin, cage thoracique, épaules."}),
            ("semaine", {"numero": "S2", "titre": "Centre", "texte": "Le travail profond de la sangle abdominale, chariot lent."}),
            ("semaine", {"numero": "S3", "titre": "Chaîne postérieure", "texte": "Fessiers, ischio-jambiers, dos : pousser loin, revenir sans à-coup."}),
            ("semaine", {"numero": "S4", "titre": "Flow complet", "texte": "Les enchaînements des trois semaines, en une séance fluide."}),
        ], "sem"),
        "quiz": section("entracte-quiz", {
            "ancre": "entracte", "label": "Entracte", "titre": "Quelle édition pour vous ?",
            "texte": "Cinq questions, deux minutes. Le résultat présélectionne l'édition ci-dessus ; l'e-mail reste facultatif.",
            "email": True,
            "note": "Douleurs, grossesse ou post-partum : demandez l'avis de votre médecin ou kiné.",
        }),
        "objections": section("faq", {"ancre": "objections", "titre": "Ce qui pourrait vous retenir"}, [
            ("question", {"question": "Est-ce que ça remplace un cours en studio ?",
                          "reponse": "<p>Non, et ce n'est pas le but. Le chariot glisse comme en studio, mais la résistance vient d'élastiques et non de ressorts. Il complète vos cours, ou vous permet de pratiquer entre deux.</p>"}),
            ("question", {"question": "Et les voisins du dessous ?",
                          "reponse": "<p>Les roues sont en polyuréthane et roulent sur des rails en acier. Nous publierons une mesure en décibels quand elle aura été faite par un laboratoire ; d'ici là, la vidéo du plan 03 est tournée avec le son réel.</p>"}),
            ("question", {"question": "Mon parquet va-t-il souffrir ?",
                          "reponse": "<p>Le plateau repose sur des patins en feutre (livrés avec l'édition Studio, vendus à part pour l'Essentiel).</p>"}),
            ("question", {"question": "Quel poids peut-il supporter ?",
                          "reponse": "<p>La charge maximale testée sera publiée dans la fiche technique dès réception du rapport d'essai. Nous n'annonçons aucun chiffre avant.</p>"}),
        ], "obj"),
        "temoignages": section("temoignages", {"ancre": "beta", "titre": "Les premières à l'avoir essayé",
                                               "intro": "Des bêta-testeuses réelles, à qui nous avons prêté le produit. Leurs mots, sans retouche."}),
        "faq": section("faq", {"ancre": "faq", "titre": "Questions"}, FAQ_COMMUNE, "q"),
        "garanties": section("garanties", {
            "ancre": "garanties", "titre": "Garanties",
            "encadre": "<p>[ENCADRÉ GARANTIE LÉGALE — décret 2022-424]</p>",
        }, [
            ("garantie", {"titre": "Garantie légale de conformité, 2 ans", "texte": "Un défaut de conformité dans les deux ans suivant la livraison : réparation ou remplacement.", "mode": "tous"}),
            ("garantie", {"titre": "14 jours pour changer d'avis", "texte": "Droit de rétractation à compter de la réception.", "mode": "tous"}),
            ("garantie", {"titre": "Réservation remboursable", "texte": "Les 19 € de réservation sont remboursables à tout moment et déduits du prix final.", "mode": "reservation"}),
            ("garantie", {"titre": "Paiement sécurisé", "texte": "Le paiement est traité par Shopify ; vos données bancaires ne transitent pas par L'Aplomb.", "mode": "tous"}),
        ], "gar"),
        "gpsr": section("gpsr", {"ancre": "securite", "titre": "Sécurité du produit",
                                 "intro": "Informations du règlement européen sur la sécurité générale des produits (GPSR)."}),
    }
    order = ["main", "benefices", "etapes", "negations", "specs", "programme", "quiz", "objections",
             "temoignages", "faq", "garanties", "gpsr"]
    return {"sections": sections, "order": order}


if __name__ == "__main__":
    for nom, data in [("index", index()), ("product", product())]:
        with open(os.path.join(ROOT, "templates", f"{nom}.json"), "w", encoding="utf-8") as fh:
            fh.write(ENTETE + json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        print("templates/%s.json" % nom)
