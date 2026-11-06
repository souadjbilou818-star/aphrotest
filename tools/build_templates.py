"""Écrit les modèles JSON du thème (textes de la marque).

templates/index.json                accueil
templates/product.json              COULISSE 01 (modèle par défaut des produits)
templates/product.essentiels.json   famille 01, Les Essentiels
templates/product.atelier.json      famille 03, Reformers Atelier
templates/page.pilates-quiz.json    page du quiz
templates/collection.json           pages de famille

Le texte est saisi ici en français courant ; tools/typo_theme.py applique
ensuite la microtypographie (espaces fines, apostrophes, guillemets).
Aucune donnée inventée : pas d'avis, pas de chiffre de vente, pas de mesure.
Les mesures viennent des metafields du produit, quand elles sont vérifiées.
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

# Handles des produits à créer dans Shopify (docs/product-mapping.md)
H_COULISSE = "coulisse-01"
H_ESSENTIELS = "la-trousse"
H_ATELIER = "atelier-chene"


def blocs(prefixe, items):
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


def q(question, reponse):
    return ("question", {"question": question, "reponse": f"<p>{reponse}</p>"})


FAQ = {
    "reformer": q("COULISSE 01, est-ce un reformer ?",
                  "Non. C'est une planche compacte : deux plateaux rembourrés coulissent sur des rails intégrés, "
                  "un sur chaque moitié. Il n'y a ni chariot, ni ressorts, ni barre de pieds. Pour un reformer "
                  "complet, à chariot, voyez la famille Reformers Atelier."),
    "fonctionne": q("Comment fonctionne la planche ?",
                    "Vous posez les pieds, les genoux ou les mains sur les plateaux. L'un glisse pendant que l'autre "
                    "tient, ou les deux s'écartent ensemble : c'est le travail en glissé. Les cordons à poignées, "
                    "accrochés aux extrémités, ajoutent une résistance pour les bras et le dos."),
    "debutant": q("Est-ce adapté si je débute ?",
                  "Oui. Commencez lentement, plateaux proches, amplitude courte. En cas de douleur, de blessure, "
                  "de grossesse ou après un accouchement, demandez l'avis d'un professionnel de santé avant de commencer."),
    "place": q("Quelle place faut-il ?",
               "Pendant la séance : la planche dépliée, et de quoi allonger les bras et les jambes autour. "
               "Les dimensions exactes de chaque produit figurent dans sa fiche technique dès qu'elles sont vérifiées ; "
               "nous ne publions aucune mesure avant."),
    "rangement": q("Se range-t-elle facilement ?",
                   "Elle se plie en deux, en son milieu : pliée, elle fait la moitié de sa longueur. "
                   "Ses dimensions pliées figurent dans la fiche technique."),
    "inclus": q("Qu'est-ce qui est inclus ?",
                "Le contenu exact de chaque édition est écrit sur la fiche du produit, sous le choix de l'édition, "
                "et dans sa fiche technique."),
    "livraison": q("Comment se passe la livraison ?",
                   "Les délais et les frais s'affichent avant le paiement, selon votre adresse. "
                   "Vous recevez un e-mail à l'expédition."),
    "casse": q("Et si quelque chose casse ?",
               "Vous bénéficiez de la garantie légale de conformité pendant 2 ans à compter de la livraison : "
               "réparation ou remplacement, sans frais. Écrivez-nous, avec une photo si possible."),
    "retour": q("Puis-je retourner mon achat ?",
                "Oui. Vous disposez de 14 jours après réception pour exercer votre droit de rétractation. "
                "Les conditions et les frais de retour figurent sur la page Livraison et retours."),
}

COMPARATIF_LIGNES = [
    ("ligne", {"libelle": "Ce que c'est", "essentiels": "Un kit d'accessoires pour le tapis",
               "coulisse": "Une planche pliable à deux plateaux coulissants",
               "atelier": "Un reformer complet, à chariot"}),
    ("ligne", {"libelle": "Ce qui bouge", "essentiels": "Vous, sur le tapis",
               "coulisse": "Deux plateaux, chacun sur ses rails",
               "atelier": "Un chariot sur rails"}),
    ("ligne", {"libelle": "Résistance", "essentiels": "Bandes élastiques",
               "coulisse": "Cordons à poignées et glissé des plateaux",
               "atelier": "Résistance réglable du reformer"}),
    ("ligne", {"libelle": "Pendant la séance", "essentiels": "La place d'un tapis",
               "coulisse": "La planche dépliée",
               "atelier": "La place d'un reformer"}),
    ("ligne", {"libelle": "Rangement", "essentiels": "Une pochette",
               "coulisse": "Pliée en deux",
               "atelier": "Selon le modèle"}),
    ("ligne", {"libelle": "Pour qui", "essentiels": "Débuter, compléter une pratique",
               "coulisse": "Une pratique régulière, dans peu de place",
               "atelier": "Une pratique proche du studio, avec un espace dédié"}),
]


def quiz(mode):
    def question(cle, texte, poids, options, aide=""):
        s = {"cle": cle, "question": texte, "poids": poids, "aide": aide}
        for i, (libelle, oriente, argument, exclut) in enumerate(options, 1):
            s[f"option_{i}"] = libelle
            s[f"oriente_{i}"] = oriente
            s[f"argument_{i}"] = argument
            s[f"exclut_{i}"] = exclut
        return ("question", s)

    questions = [
        question("objectif", "Qu'aimeriez-vous améliorer dans votre pratique ?", 1, [
            ("Renforcement et tonicité", "coulisse atelier", "Vous cherchez du renforcement : le travail en glissé et en résistance s'y prête.", "aucune"),
            ("Mobilité et souplesse", "essentiels coulisse", "Pour la mobilité, des mouvements amples et contrôlés suffisent.", "aucune"),
            ("Reprendre une activité régulière", "essentiels coulisse", "Pour reprendre, mieux vaut un équipement simple à sortir chaque jour.", "aucune"),
            ("Installer une routine Pilates chez soi", "coulisse", "Pour une routine, un appareil toujours prêt, qui ne prend pas la pièce.", "aucune"),
        ]),
        question("niveau", "Quel est votre niveau actuel ?", 1, [
            ("Je débute", "essentiels coulisse", "Vous débutez : on commence simple, sans réglage compliqué.", "aucune"),
            ("J'ai déjà pratiqué", "coulisse", "Vous avez déjà pratiqué : vous retrouverez le travail en glissé.", "aucune"),
            ("Je pratique régulièrement", "coulisse atelier", "Vous pratiquez régulièrement : il vous faut de quoi progresser.", "aucune"),
        ]),
        question("equipement", "Quel type d'équipement vous correspond ?", 3, [
            ("Un kit simple et accessible", "essentiels", "Vous voulez un kit simple : rien à installer, rien à régler.", "aucune"),
            ("Un appareil compact et polyvalent", "coulisse", "Vous voulez un appareil compact : deux plateaux, des cordons, une planche qui se plie.", "aucune"),
            ("Une expérience proche d'un studio", "atelier", "Vous voulez retrouver le studio : un chariot sur rails, une résistance réglable.", "aucune"),
        ]),
        question("espace", "De quel espace disposez-vous ?", 2, [
            ("Un petit espace", "essentiels coulisse", "Peu de place : un kit tient dans une pochette, la planche se plie en deux.", "atelier"),
            ("Une pièce polyvalente", "coulisse atelier", "Une pièce polyvalente : un appareil qui se range après la séance.", "aucune"),
            ("Un espace dédié", "atelier", "Un espace dédié : la place d'un reformer complet.", "aucune"),
        ]),
    ]
    settings = {
        "mode": mode,
        "ancre": "quiz",
        "quiz_id": "choix-equipement",
        "surtitre": "Quatre questions · une minute",
        "titre": "Trouvez votre équipement",
        "intro": "Aucune donnée personnelle demandée. Vos réponses restent dans ce navigateur, le temps de la visite.",
        "produit_essentiels": H_ESSENTIELS,
        "produit_coulisse": H_COULISSE,
        "produit_atelier": H_ATELIER,
        "raison_essentiels": "Un kit d'accessoires pour installer une routine sur le tapis, sans appareil à ranger.",
        "raison_coulisse": "Deux plateaux qui coulissent l'un sans l'autre : le travail en glissé d'un appareil, dans le format d'une planche qui se plie.",
        "raison_atelier": "Un vrai chariot sur rails, avec une résistance réglable : la pratique la plus proche du studio, pour qui a la place.",
        "note": "Ce quiz oriente un achat ; il ne remplace pas un avis médical. En cas de douleur, de blessure ou de grossesse, demandez conseil avant de commencer.",
    }
    return section("aplomb-quiz", settings, questions, "q")


def garanties(num):
    return section("garanties", {"ancre": "garanties", "num": num, "folio": "", "encadre": "", "titre": "Ce qui vous protège",
                                 "intro": "Vos droits, écrits simplement. Rien de plus, rien de moins."}, [
        ("garantie", {"titre": "14 jours pour changer d'avis",
                      "texte": "À compter de la réception. Les conditions de retour sont sur la page Livraison et retours.",
                      "mode": "tous"}),
        ("garantie", {"titre": "Garantie légale de conformité, 2 ans",
                      "texte": "Réparation ou remplacement sans frais si le produit présente un défaut.",
                      "mode": "tous"}),
        ("garantie", {"titre": "Sécurité du produit",
                      "texte": "Fabricant identifié, avertissements et notice : tout est sur la page Sécurité produit.",
                      "mode": "tous"}),
        ("garantie", {"titre": "Paiement natif Shopify",
                      "texte": "Vous payez sur la page de paiement Shopify ; nous ne voyons jamais votre carte.",
                      "mode": "vente"}),
    ], "g")


def index():
    sections = {
        "hero": section("aplomb-hero", {
            "surtitre": "Pilates à domicile · Paris",
            "titre": "Le Pilates chez soi, avec aplomb.",
            "titre_accent": "avec aplomb",
            "texte": "Trois familles d'équipement, du kit d'accessoires au reformer à chariot. En tête : COULISSE 01, "
                     "une planche pliable dont les deux plateaux coulissent l'un sans l'autre.",
            "cta_produit": "Découvrir COULISSE 01",
            "cta_quiz": "Trouver mon équipement",
            "ordre_cta": "produit",
            "ancre_produit": "coulisse",
            "visuel": "dessin",
            "legende_dessin": "COULISSE 01, vue de dessus et élévation. Faites défiler : les plateaux coulissent l'un après l'autre.",
        }, [
            ("fait", {"texte": "Deux plateaux rembourrés, indépendants"}),
            ("fait", {"texte": "Se plie en deux pour le rangement"}),
            ("fait", {"texte": "Cordons de résistance et poignées"}),
        ], "f"),
        "familles": section("aplomb-familles", {
            "ancre": "familles",
            "titre": "Trois familles, une même exigence",
            "intro": "Choisissez selon votre pratique et votre place.",
            "famille_avant": "coulisse",
            "texte_voir": "Voir",
            "texte_attente": "En préparation",
        }, [
            ("famille", {"famille": "essentiels", "numero": "01", "nom": "Les Essentiels",
                         "texte": "Des kits d'accessoires pour pratiquer sur le tapis, sans appareil à ranger."}),
            ("famille", {"famille": "coulisse", "numero": "02", "nom": "Coulisse",
                         "texte": "Une planche pliable à deux plateaux coulissants : le travail en glissé, dans peu de place."}),
            ("famille", {"famille": "atelier", "numero": "03", "nom": "Reformers Atelier",
                         "texte": "De vrais reformers à chariot, pour une pratique proche du studio, avec un espace dédié."}),
        ], "fa"),
        "vedette": section("aplomb-vedette", {
            "ancre": "coulisse",
            "produit": H_COULISSE,
            "surtitre": "02 — Coulisse · le produit phare",
            "titre": "COULISSE 01",
            "texte": "<p>Une planche compacte, pliable en son milieu. Sur chaque moitié, un plateau rembourré coulisse sur "
                     "ses rails, indépendamment de l'autre : écarts, fentes, gainage en glissé. Des cordons à poignées "
                     "s'accrochent aux extrémités pour le haut du corps.</p>",
            "nomenclature": "Plateau coulissant gauche\nPlateau coulissant droit\nRails intégrés\nCharnière de pliage\n"
                            "Cordons de résistance\nPoignées\nPatins antidérapants",
            "tag_attente": "coulisse-01",
        }, [
            ("point", {"texte": "Deux plateaux rembourrés, chacun sur ses rails"}),
            ("point", {"texte": "Se plie en deux, en son milieu"}),
            ("point", {"texte": "Cordons de résistance et poignées"}),
        ], "p"),
        "demo": section("aplomb-demo", {
            "ancre": "demonstration", "num": "I.", "titre": "Comment ça coulisse",
            "intro": "Un plateau sous chaque pied, ou sous chaque main. L'un glisse, l'autre tient : c'est tout le travail.",
            "produit": H_COULISSE, "ratio": "16/9",
            "legende_dessin": "Faites défiler : le plateau gauche s'écarte d'abord, puis le droit.",
        }, [
            ("mouvement", {"titre": "L'écart", "texte": "Un pied sur chaque plateau. Vous écartez, puis vous ramenez, lentement.",
                           "travail": "Adducteurs · gainage"}),
            ("mouvement", {"titre": "La fente glissée", "texte": "Un pied sur un plateau qui recule, puis revient, pendant que l'autre tient.",
                           "travail": "Fessiers · cuisses · équilibre"}),
            ("mouvement", {"titre": "La planche glissée", "texte": "Mains au sol, pieds sur les plateaux : vous ramenez les genoux vers la poitrine.",
                           "travail": "Abdominaux · épaules"}),
        ], "m"),
        "comparatif": section("aplomb-comparatif", {
            "ancre": "comparatif", "num": "II.", "titre": "Laquelle vous correspond",
            "intro": "Trois familles, trois façons de pratiquer. Aucune n'est meilleure dans l'absolu.",
            "nom_essentiels": "Les Essentiels", "nom_coulisse": "COULISSE 01", "nom_atelier": "Reformers Atelier",
            "colonne_avant": "coulisse", "ligne_prix": True, "libelle_prix": "Prix", "prix_attente": "Bientôt",
            "honnete": "COULISSE 01 n'est pas un reformer : ni chariot, ni ressorts. Pour un reformer complet, voyez les Reformers Atelier.",
        }, COMPARATIF_LIGNES, "l"),
        "quiz": quiz("integre"),
        "programme": section("acte-programme", {
            "ancre": "programme", "num": "III.", "folio": "", "plan": "", "titre": "Le programme",
            "intro": "Vingt minutes, quatre semaines, chez vous.",
            "chapeau": "Quatre semaines pour installer la routine, sans brûler les étapes. Trois séances de vingt minutes par semaine.",
            "encart_titre": "Le rythme",
            "encart_texte": "Trois séances par semaine. Le reste du temps, l'appareil se range.",
            "image": img("plan-06-posture-provisoire.jpg"), "ratio": "4/5", "generee": True,
            "legende": "posture de gainage latéral, sur tapis",
        }, [
            ("semaine", {"numero": "Sem. 1", "titre": "L'alignement", "texte": "Placer le bassin, respirer, trouver l'axe."}),
            ("semaine", {"numero": "Sem. 2", "titre": "Le centre", "texte": "Gainage, mouvements lents, amplitude courte."}),
            ("semaine", {"numero": "Sem. 3", "titre": "Le glissé", "texte": "Plus d'amplitude, plus de contrôle."}),
            ("semaine", {"numero": "Sem. 4", "titre": "L'aplomb", "texte": "Enchaîner, tenir, recommencer."}),
        ], "s"),
        "garanties": garanties("IV."),
        "maison": section("acte-maison", {
            "ancre": "maison", "num": "V.", "folio": "", "titre": "La maison",
            "texte": "<p>L'Aplomb est né à Paris d'un constat simple : le Pilates se pratique mieux avec un appareil, "
                     "mais l'appareil doit tenir dans un appartement. Trois familles, du kit d'accessoires au reformer "
                     "à chariot, choisies pour leur justesse plutôt que pour leur nombre.</p>",
            "transparence": "Sélectionné et contrôlé à Paris, fabriqué par une usine partenaire. Le nom et l'adresse du fabricant figurent sur la page Sécurité produit.",
            "soir_label": "La maison, le soir",
            "soir_titre": "L'élégance publique.",
            "soir_titre_2": "La discipline privée.",
        }, [
            ("cadre", {"image": img("plan-09-soiree.jpg"), "generee": True, "ratio": "3/2", "plan": "",
                       "legende": "l'élégance publique, une soirée à Paris"}),
        ], "c"),
        "faq": section("faq", {"ancre": "faq", "num": "VI.", "titre": "Vos questions",
                               "intro": "Les réponses courtes aux questions qu'on nous pose le plus."},
                       [FAQ[k] for k in ("reformer", "fonctionne", "debutant", "place", "rangement", "inclus", "livraison", "casse", "retour")], "q"),
        "cloture": section("aplomb-cloture", {
            "ancre": "cloture",
            "titre_attente": "La liste d'attente est ouverte.",
            "texte_attente": "Nous vous écrivons à l'ouverture, avec les prix définitifs et les délais de livraison. Pas avant.",
            "titre": "Votre pratique, chez vous, dès cette semaine.",
            "texte": "COULISSE 01 pour commencer, ou quatre questions pour choisir.",
            "cta_produit": "Voir COULISSE 01",
            "cta_quiz": "Trouver mon équipement",
        }),
    }
    order = ["hero", "familles", "vedette", "demo", "comparatif", "quiz", "programme", "garanties", "maison", "faq", "cloture"]
    return {"sections": sections, "order": order}


def produit_commun(accroche, preuves, benefices, faq_cles, num_debut=1, avec_demo=False, avec_negations=None, etapes=None):
    romains = ["I.", "II.", "III.", "IV.", "V.", "VI.", "VII.", "VIII."]
    n = iter(romains[num_debut - 1:])
    sections = {
        "main": section("produit-principal", {
            "accroche": accroche,
            "titre_description": "Description",
        }, [("preuve", {"texte": t}) for t in preuves], "p"),
    }
    order = ["main"]
    if avec_demo:
        sections["demo"] = section("aplomb-demo", {
            "ancre": "demonstration", "num": next(n), "titre": "Comment ça coulisse",
            "intro": "Un plateau sous chaque pied, ou sous chaque main. L'un glisse, l'autre tient.",
            "ratio": "16/9", "legende_dessin": "Faites défiler : le plateau gauche s'écarte d'abord, puis le droit.",
        }, [
            ("mouvement", {"titre": "L'écart", "texte": "Un pied sur chaque plateau. Vous écartez, puis vous ramenez, lentement.", "travail": "Adducteurs · gainage"}),
            ("mouvement", {"titre": "La fente glissée", "texte": "Un pied sur un plateau qui recule, puis revient, pendant que l'autre tient.", "travail": "Fessiers · cuisses · équilibre"}),
            ("mouvement", {"titre": "La planche glissée", "texte": "Mains au sol, pieds sur les plateaux : vous ramenez les genoux vers la poitrine.", "travail": "Abdominaux · épaules"}),
        ], "m")
        order.append("demo")
    sections["benefices"] = section("benefices", {"ancre": "benefices", "num": next(n), "titre": "Ce qu'il change"},
                                    [("benefice", {"titre": t, "texte": x}) for t, x in benefices], "b")
    order.append("benefices")
    if etapes:
        sections["etapes"] = section("etapes", {"ancre": "comment", "num": next(n), "titre": "Comment ça marche"},
                                     [("etape", {"titre": t, "texte": x, "didascalie": d, "generee": False}) for t, x, d in etapes], "e")
        order.append("etapes")
    if avec_negations:
        sections["negations"] = section("negations", {"ancre": "honnetete", "num": next(n), "titre": "Ce que ce n'est pas",
                                                      "honnete": avec_negations[0]},
                                        [("negation", {"non": a, "explication": b}) for a, b in avec_negations[1]], "n")
        order.append("negations")
    sections["specs"] = section("specs", {"ancre": "fiche-technique", "num": next(n), "titre": "Fiche technique",
                                          "intro": "Les mesures s'affichent dès qu'elles sont vérifiées. Aucun chiffre n'est publié avant."})
    order.append("specs")
    sections["comparatif"] = section("aplomb-comparatif", {
        "ancre": "comparatif", "num": next(n), "titre": "Les trois familles, côte à côte",
        "nom_essentiels": "Les Essentiels", "nom_coulisse": "COULISSE 01", "nom_atelier": "Reformers Atelier",
        "colonne_avant": "coulisse", "ligne_prix": True, "libelle_prix": "Prix", "prix_attente": "Bientôt",
        "honnete": "COULISSE 01 n'est pas un reformer : ni chariot, ni ressorts.",
    }, COMPARATIF_LIGNES, "l")
    order.append("comparatif")
    sections["temoignages"] = section("temoignages", {"ancre": "avis", "titre": "Avis",
                                                      "intro": "Uniquement des avis réels, publiés avec l'accord de leurs auteurs."})
    order.append("temoignages")
    sections["garanties"] = garanties(next(n))
    order.append("garanties")
    sections["gpsr"] = section("gpsr", {"ancre": "securite", "titre": "Sécurité du produit",
                                        "intro": "Informations exigées par le règlement européen sur la sécurité générale des produits."})
    order.append("gpsr")
    sections["faq"] = section("faq", {"ancre": "faq", "titre": "Vos questions"}, [FAQ[k] for k in faq_cles], "q")
    order.append("faq")
    return {"sections": sections, "order": order}


def product():
    return produit_commun(
        accroche="Une planche pliable, deux plateaux qui coulissent l'un sans l'autre, des cordons à poignées.",
        preuves=["Deux plateaux rembourrés, indépendants", "Rails intégrés à la planche", "Se plie en deux, en son milieu"],
        benefices=[
            ("Un travail en glissé, à la maison", "Le glissé demande du contrôle à chaque centimètre : c'est là que le centre travaille."),
            ("Deux côtés, deux rythmes", "Chaque plateau bouge seul. Vous travaillez un côté pendant que l'autre tient."),
            ("Rangée en un geste", "La planche se plie en son milieu. Pliée, elle fait la moitié de sa longueur."),
        ],
        etapes=[
            ("Dépliez", "Posez la planche à plat, sur un sol dur ou un tapis fin.", "la planche se déplie sur un parquet"),
            ("Placez-vous", "Pieds, genoux ou mains sur les plateaux, selon le mouvement.", "deux pieds sur les plateaux, vue de profil"),
            ("Coulissez", "Un plateau glisse, l'autre tient. Lentement, puis plus loin.", "un plateau s'écarte, l'autre reste en place"),
        ],
        avec_negations=("Une planche à deux plateaux coulissants, pas un reformer.", [
            ("Pas un reformer", "Ni chariot, ni ressorts, ni barre de pieds. Pour cela, voyez les Reformers Atelier."),
            ("Pas un appareil médical", "Il ne soigne rien. En cas de douleur, demandez l'avis d'un professionnel de santé."),
            ("Pas un abonnement", "Vous achetez l'appareil, une fois. Aucun paiement récurrent."),
        ]),
        faq_cles=("reformer", "fonctionne", "debutant", "place", "rangement", "inclus", "livraison", "casse", "retour"),
        avec_demo=True,
    )


def product_essentiels():
    return produit_commun(
        accroche="Un kit d'accessoires pour installer une routine sur le tapis, sans appareil à ranger.",
        preuves=["Tout tient dans une pochette", "Pour débuter ou compléter une pratique"],
        benefices=[
            ("Rien à installer", "Vous sortez la pochette, vous déroulez le tapis, vous commencez."),
            ("De quoi varier", "Chaque accessoire change l'appui ou la résistance d'un même mouvement."),
            ("Le complément d'un appareil", "Les Essentiels accompagnent aussi COULISSE 01 et les Reformers Atelier."),
        ],
        faq_cles=("debutant", "inclus", "livraison", "casse", "retour"),
    )


def product_atelier():
    return produit_commun(
        accroche="Un reformer complet, à chariot, pour une pratique proche du studio.",
        preuves=["Un vrai chariot sur rails", "Pliable ou à poste fixe, selon le modèle"],
        benefices=[
            ("Le geste du studio", "Le chariot, la résistance réglable, l'amplitude complète des mouvements."),
            ("Une pratique qui progresse", "Vous augmentez la résistance au fil des semaines."),
            ("Un objet qui a sa place", "Choisi pour sa tenue et ses matières, il reste dans la pièce."),
        ],
        faq_cles=("debutant", "place", "inclus", "livraison", "casse", "retour"),
    )


def page_quiz():
    return {"sections": {"quiz": quiz("page")}, "order": ["quiz"]}


def collection():
    return {"sections": {"main": section("collection", {
        "par_page": 12, "libelle_familles": "Les familles",
        "texte_vide": "Cette famille arrive bientôt. Inscrivez-vous à la liste d'attente depuis l'accueil.",
        "texte_quiz": "Vous hésitez ? Quatre questions pour choisir",
    })}, "order": ["main"]}


def ecrire(nom, data):
    chemin = os.path.join(ROOT, "templates", f"{nom}.json")
    with open(chemin, "w", encoding="utf-8") as fh:
        fh.write(ENTETE)
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(f"templates/{nom}.json")


if __name__ == "__main__":
    ecrire("index", index())
    ecrire("product", product())
    ecrire("product.essentiels", product_essentiels())
    ecrire("product.atelier", product_atelier())
    ecrire("page.pilates-quiz", page_quiz())
    ecrire("collection", collection())
