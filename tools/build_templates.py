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
H_ATELIER = "atelier-pliable"


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
                  "Non. C'est une planche compacte : deux plateaux coulissent chacun sur son rail. Il n'y a ni chariot, "
                  "ni ressorts, ni barre de pieds. Pour un reformer complet, à chariot, voyez ATELIER Pliable."),
    "fonctionne": q("Comment fonctionne la planche ?",
                    "Vous posez les pieds, les genoux ou les mains sur les plateaux. L'un glisse pendant que l'autre "
                    "tient, ou les deux s'écartent ensemble : c'est le travail en glissé. Les poignées et le cordon de résistance "
                    "ajoutent un travail des bras et du dos."),
    "debutant": q("Est-ce adapté si je débute ?",
                  "Oui. Commencez lentement, plateaux proches, amplitude courte. En cas de douleur, de blessure, "
                  "de grossesse ou après un accouchement, demandez l'avis d'un professionnel de santé avant de commencer."),
    "place": q("Quelle place faut-il ?",
               "La planche mesure 105 × 40 cm (fiche fournisseur) : comptez autour d'elle de quoi allonger les bras et les jambes, "
               "soit à peu près la place d'un tapis de yoga."),
    "rangement": q("Se range-t-elle facilement ?",
                   "Oui. Elle fait 3 cm d'épaisseur : elle se range à plat, sous un lit, derrière un meuble ou contre un mur."),
    "inclus": q("Qu'est-ce qui est inclus ?",
                "La planche, les deux plateaux coulissants, les poignées et le cordon de résistance. "
                "Le détail figure dans la description du produit."),
    "livraison": q("Comment se passe la livraison ?",
                   "COULISSE 01 et Le Coffret Essentiel sont livrés gratuitement. Les délais et les éventuels frais s'affichent "
                   "avant le paiement, selon votre adresse. Vous recevez un e-mail à l'expédition."),
    "casse": q("Et si quelque chose casse ?",
               "Vous bénéficiez de la garantie légale de conformité pendant 2 ans à compter de la livraison : "
               "réparation ou remplacement, sans frais. Écrivez-nous, avec une photo si possible."),
    "retour": q("Puis-je retourner mon achat ?",
                "Oui. Vous disposez de 14 jours après réception pour exercer votre droit de rétractation. "
                "Les conditions figurent sur la page Livraison et retours."),
}

COMPARATIF_LIGNES = [
    ("ligne", {"libelle": "Ce que c'est", "essentiels": "Un kit d'accessoires pour le tapis",
               "coulisse": "Une planche à deux plateaux coulissants",
               "atelier": "Un reformer complet, à chariot"}),
    ("ligne", {"libelle": "Ce qui bouge", "essentiels": "Vous, sur le tapis",
               "coulisse": "Deux plateaux, chacun sur ses rails",
               "atelier": "Un chariot sur rails"}),
    ("ligne", {"libelle": "Résistance", "essentiels": "Bandes élastiques",
               "coulisse": "Cordons à poignées et glissé des plateaux",
               "atelier": "Résistance réglable du reformer"}),
    ("ligne", {"libelle": "Pendant la séance", "essentiels": "La place d'un tapis",
               "coulisse": "La planche, 105 × 40 cm",
               "atelier": "La place d'un reformer"}),
    ("ligne", {"libelle": "Rangement", "essentiels": "Une pochette",
               "coulisse": "À plat, 3 cm d'épaisseur",
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
            ("Un appareil compact et polyvalent", "coulisse", "Vous voulez un appareil compact : deux plateaux, des poignées, une planche qui se range à plat.", "aucune"),
            ("Une expérience proche d'un studio", "atelier", "Vous voulez retrouver le studio : un chariot sur rails, une résistance réglable.", "aucune"),
        ]),
        question("espace", "De quel espace disposez-vous ?", 2, [
            ("Un petit espace", "essentiels coulisse", "Peu de place : un kit tient dans un sac, la planche se range à plat.", "atelier"),
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
        "raison_coulisse": "Deux plateaux qui coulissent l'un sans l'autre : le travail en glissé d'un appareil, dans le format d'une planche qui se range à plat.",
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


TUILES = [("tuile", {"icone": "cadenas", "texte": "Paiement sécurisé"}),
          ("tuile", {"icone": "retour", "texte": "14 jours pour changer d'avis"}),
          ("tuile", {"icone": "bouclier", "texte": "Garantie légale 2 ans"})]


def produit_commun(accroche, preuves, benefices, faq_cles, num_debut=1, avec_demo=False, avec_negations=None, etapes=None):
    romains = ["I.", "II.", "III.", "IV.", "V.", "VI.", "VII.", "VIII."]
    n = iter(romains[num_debut - 1:])
    sections = {
        "main": section("produit-principal", {"accroche": accroche, "titre_associes": "À associer"},
                        TUILES + [("preuve", {"texte": t}) for t in preuves], "p"),
        "description": section("aplomb-description", {"ancre": "description", "titre": "Description"}),
    }
    order = ["main", "description"]
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


def carte(titre, texte, image=None, generee=False):
    d = {"titre": titre, "texte": texte, "image_generee": generee}
    if image:
        d["image"] = img(image)
    return ("carte", d)


def maison_valeurs():
    return section("aplomb-caracteristiques", {
        "ancre": "maison", "titre": "Une maison, trois engagements", "disposition": "grille", "colonnes": "3", "fond": "ivoire", "aligner": "centre",
        "intro": "Ce que vous pouvez attendre de L'Aplomb, avant comme après l'achat.",
    }, [
        carte("Choisir peu, choisir bien", "Trois familles d'équipement, choisies pour leur justesse plutôt que pour leur nombre.", "plan-06-posture-provisoire.jpg", True),
        carte("Dire vrai", "Pas de faux avis, pas de compte à rebours, pas de prix barré. Les mesures viennent des fiches de nos fournisseurs.", "atelier-pliable-0-ambiance.jpg", True),
        carte("Penser aux appartements", "Des équipements qui se rangent et se font oublier entre deux séances.", "coffret-1-coffret.jpg", True),
    ], "v")


# Fichiers d'images Shopify (photos fournisseur de COULISSE 01, déjà dans Fichiers)
IMG_COULISSE_ROSE = "0c2d1da44e298772ffb0f69115cd.jpg"
IMG_COULISSE_ROSE_2 = "e91889c646d686461ef85700d425.jpg"
IMG_COULISSE_ROSE_3 = "f2e29f8b47bd8b2e338339bf9902.jpg"
IMG_COULISSE_NOIR = "a17a7ed34c2b8a31c3c83caba9d0.jpg"
IMG_COULISSE_COLIS = "93040adb410abd48ee6f563c4581.jpg"

TUILES_OFFERTE = [("tuile", {"icone": "camion", "texte": "Livraison offerte"}),
                  ("tuile", {"icone": "retour", "texte": "14 jours pour changer d'avis"}),
                  ("tuile", {"icone": "cadenas", "texte": "Paiement sécurisé"})]


def confiance(fond="ivoire"):
    return section("aplomb-caracteristiques", {
        "ancre": "confiance", "titre": "Commander en confiance", "disposition": "grille", "colonnes": "4", "fond": fond,
        "intro": "Vos droits, écrits simplement.",
    }, [
        carte("Livraison offerte", "Sur COULISSE 01 et Le Coffret Essentiel. Les délais s'affichent avant le paiement, selon votre adresse."),
        carte("14 jours pour changer d'avis", "À compter de la réception, sans avoir à vous justifier. Remboursement sur le moyen de paiement utilisé."),
        carte("Garantie légale de 2 ans", "Réparation ou remplacement sans frais si le produit présente un défaut de conformité."),
        carte("Paiement sécurisé", "Vous payez sur la page de paiement Shopify : vos données de carte ne nous sont jamais transmises."),
    ], "k")


def index():
    sections = {
        "hero": section("aplomb-hero", {
            "surtitre": "Pilates à domicile",
            "titre": "Le Pilates chez soi, avec aplomb.",
            "titre_accent": "avec aplomb",
            "texte": "Une planche à plateaux coulissants, un coffret d'accessoires, un reformer qui se range : "
                     "tout pour pratiquer chez vous, sans studio et sans abonnement.",
            "cta_produit": "Voir la boutique",
            "lien_principal": "#boutique",
            "cta_quiz": "Trouver mon équipement",
            "ordre_cta": "produit",
            "visuel": "image",
            "image": img("atelier-pliable-0-ambiance.jpg"),
            "image_generee": True,
        }, [
            ("fait", {"texte": "Livraison offerte sur COULISSE 01 et le Coffret"}),
            ("fait", {"texte": "14 jours pour changer d'avis"}),
            ("fait", {"texte": "Paiement sécurisé"}),
        ], "f"),
        "boutique": section("aplomb-produits", {
            "ancre": "boutique", "titre": "La boutique", "collection": "frontpage", "nombre": 6, "colonnes": "3", "libelle_lien": "",
        }),
        "coulisse": section("aplomb-image-texte", {
            "ancre": "coulisse", "produit": H_COULISSE, "image": img(IMG_COULISSE_ROSE), "fond": "ivoire",
            "surtitre": "Le produit phare", "titre": "COULISSE 01",
            "texte": "<p>Deux plateaux qui coulissent chacun sur son rail, l'un sans l'autre. Un pied, un genou ou une main "
                     "sur chaque plateau : l'un glisse, l'autre tient. C'est le travail en glissé du Pilates, sur une planche "
                     "qui se range à plat.</p>",
            "cta_libelle": "Choisir mon coloris",
        }, [("point", {"texte": t}) for t in [
            "Deux plateaux coulissants indépendants",
            "Poignées et cordon de résistance inclus",
            "105 × 40 cm, 3 cm d'épaisseur : se glisse sous un lit",
            "Rose, lavande ou noir",
        ]], "c"),
        "atelier": section("aplomb-image-texte", {
            "ancre": "atelier", "produit": H_ATELIER, "image": img("atelier-pliable-0-ambiance.jpg"), "image_generee": True,
            "inverser": True, "fond": "sable",
            "surtitre": "Le reformer qui se range", "titre": "ATELIER Pliable",
            "texte": "<p>Un vrai reformer, avec son chariot sur rails et son cadre en acier, qui se replie après la séance.</p>",
            "cta_libelle": "Découvrir ATELIER Pliable",
        }, [("point", {"texte": t}) for t in [
            "Chariot rembourré sur rails, cadre en acier",
            "Plié : 108 × 55 × 29 cm (fiche fournisseur)",
            "Tapis de yoga inclus",
        ]], "a"),
        "coffret": section("aplomb-image-texte", {
            "ancre": "coffret", "produit": H_ESSENTIELS, "image": img("coffret-1-coffret.jpg"), "image_generee": True,
            "fond": "ivoire",
            "surtitre": "Pour commencer sur le tapis", "titre": "Le Coffret Essentiel",
            "texte": "<p>Treize pièces pour une séance complète sans appareil : chaque accessoire change l'appui ou la résistance "
                     "d'un même mouvement.</p>",
            "cta_libelle": "Choisir mon coffret",
        }, [("point", {"texte": t}) for t in [
            "Anneau de 33 cm, ballon de 25 cm, 5 bandes de résistance",
            "Sangle, bande en huit, chaussettes antidérapantes",
            "Tout se range dans un sac",
        ]], "e"),
        "quiz": quiz("integre"),
        "confiance": confiance("sable"),
        "faq": section("faq", {"ancre": "faq", "titre": "Questions fréquentes",
                               "intro": "Les réponses courtes aux questions qu'on nous pose le plus."},
                       [FAQ[k] for k in ("reformer", "debutant", "livraison", "retour", "casse", "place")], "q"),
    }
    order = ["hero", "boutique", "coulisse", "atelier", "coffret", "quiz", "confiance", "faq"]
    return {"sections": sections, "order": order}


def landing(principal, sections_milieu, faq_items, offre=None, rangee=None):
    """Fiche produit, structure de la fiche boutique de référence :
    achat ; description + détails et questions en accordéons ; exercices en vitrine ;
    autres produits (cartes compactes) ; photos clientes (masquées sans photo) ;
    engagements de la maison. Pas de faux avis, pas de compte à rebours."""
    sections = {"main": principal,
                "description": section("aplomb-description", {"ancre": "description", "titre": "Description du produit"},
                                       faq_items, "q")}
    order = ["main", "description"]
    for cle, sec in sections_milieu:
        sections[cle] = sec
        order.append(cle)
    sections["rangee"] = section("aplomb-produits", {"ancre": "completer", "titre": "Complétez votre espace",
                                                     "collection": "frontpage", "nombre": 8, "style_carte": "compacte",
                                                     "colonnes": "4", "libelle_lien": ""})
    sections["en_vrai"] = section("aplomb-galerie-reelle", {"ancre": "en-vrai", "titre": "En vrai, chez vous"})
    sections["temoignages"] = section("temoignages", {"ancre": "avis", "titre": "Avis",
                                                      "intro": "Uniquement des avis réels, publiés avec l'accord de leurs auteurs."})
    sections["maison"] = maison_valeurs()
    order += ["rangee", "en_vrai", "temoignages", "maison"]
    return {"sections": sections, "order": order}


AFFICHAGE_BOUTIQUE = {"afficher_famille": False, "afficher_accroche": False, "afficher_dispo": False,
                      "titre_associes": "Complétez votre pratique"}


def vitrine(ancre, titre, intro, cartes, numeroter=True):
    return section("aplomb-caracteristiques", {
        "ancre": ancre, "titre": titre, "intro": intro, "disposition": "vitrine", "colonnes": "4",
        "fond": "gris", "aligner": "centre", "numeroter": numeroter,
    }, cartes, "e")


LIVRAISON_OFFERTE = q("Comment se passe la livraison ?", "La livraison est offerte. Les délais s'affichent avant le paiement, selon votre adresse, et vous recevez un e-mail avec le suivi à l'expédition.")
RETOUR = q("Puis-je le retourner ?", "Oui. Vous disposez de 14 jours après réception pour exercer votre droit de rétractation. Les conditions figurent sur la page Livraison et retours.")


def product():
    """COULISSE 01 (modèle par défaut des produits)."""
    principal = section("produit-principal", {
        **AFFICHAGE_BOUTIQUE, "note_livraison": "Livraison offerte",
        "accroche": "Deux plateaux qui coulissent l'un sans l'autre : le travail en glissé du Pilates, chez vous.",
    }, TUILES_OFFERTE, "p")
    exercices = vitrine("exercices", "Vos premiers exercices avec COULISSE 01",
                        "Un plateau sous chaque pied, ou sous chaque main. Commencez lentement, plateaux proches, puis allongez le mouvement.", [
        carte("L'écart", "Debout, un pied sur chaque plateau : vous écartez les jambes, puis vous ramenez, lentement. Adducteurs et gainage."),
        carte("La fente glissée", "Un pied sur un plateau qui recule, puis revient, pendant que l'autre tient. Fessiers, cuisses, équilibre."),
        carte("La planche glissée", "Mains au sol, pieds sur les plateaux : vous ramenez les genoux vers la poitrine. Abdominaux, épaules."),
        carte("Les bras aux poignées", "Les poignées en main, vous tirez le cordon en gardant le dos long. Bras, dos, épaules."),
        carte("Le grimpeur", "En planche, vous ramenez un genou puis l'autre, plateaux alternés. Cardio et sangle abdominale."),
    ])
    faq_items = [FAQ[k] for k in ("reformer", "fonctionne", "debutant", "place", "rangement", "inclus", "casse")] + [LIVRAISON_OFFERTE, RETOUR]
    return landing(principal, [("exercices", exercices)], faq_items)


def product_atelier():
    principal = section("produit-principal", {**AFFICHAGE_BOUTIQUE,
        "accroche": "Un reformer complet, à chariot, qui se replie après la séance."}, TUILES, "p")
    exercices = vitrine("exercices", "Vos premiers exercices sur ATELIER",
                        "Cinq mouvements pour prendre le reformer en main. Commencez lentement, résistance faible.", [
        carte("Le travail de pieds", "Allongée sur le chariot, pieds sur la barre : vous poussez, vous revenez sans laisser claquer le chariot."),
        carte("Le pont", "Pieds sur la barre, vous déroulez le dos vertèbre par vertèbre, puis vous redescendez."),
        carte("Les bras aux cordes", "Assise, une poignée dans chaque main : vous tirez vers l'arrière en gardant le dos long."),
        carte("La sirène", "Assise de côté, une main sur la barre : vous poussez le chariot et allongez le flanc."),
        carte("Genou vers poitrine", "À genoux, mains sur la barre : vous repoussez le chariot avec une jambe, puis vous ramenez."),
    ])
    faq_items = [
        q("Le montage est-il difficile ?", "Le reformer se monte en quelques étapes, avec la notice fournie. Comptez une personne pour tenir le cadre pendant le serrage."),
        q("Le pliage est-il sûr ?", "Pliez toujours le reformer chariot vide et à l'arrêt, en suivant la notice. Ne le dépliez jamais avec quelqu'un dessus."),
        q("Est-il facile à ranger ?", "Plié, il mesure 108 × 55 × 29 cm selon la fiche du fournisseur : il se range contre un mur ou dans un placard profond."),
        q("Est-il lourd ?", "32,5 kg selon la fiche du fournisseur. Il se déplace plus facilement à deux."),
        q("Le cadre est-il solide ?", "Le cadre est en acier. La charge maximale sera publiée sur la fiche technique dès qu'elle aura été vérifiée."),
        q("ATELIER ou COULISSE 01 ?", "ATELIER est un reformer complet, à chariot. COULISSE 01 est une planche compacte à deux plateaux coulissants, sans chariot ni ressorts. Le quiz vous aide à choisir."),
        q("Comment se passe la livraison ?", "Les délais et les frais s'affichent avant le paiement, selon votre adresse. Vous recevez un e-mail à l'expédition."),
        RETOUR,
    ]
    return landing(principal, [("exercices", exercices)], faq_items)


def product_essentiels():
    principal = section("produit-principal", {
        **AFFICHAGE_BOUTIQUE, "note_livraison": "Livraison offerte",
        "accroche": "Une séance de Pilates complète sur le tapis, avec des accessoires rangés dans un sac.",
    }, TUILES_OFFERTE, "p")
    exercices = vitrine("exercices", "Une séance avec le coffret",
                        "Un accessoire après l'autre, pour travailler tout le corps sur un seul tapis.", [
        carte("Le ballon sous le dos", "Allongée, le ballon sous les omoplates : vous enroulez le buste, puis vous redescendez lentement.", "coffret-3-ballon.jpg", True),
        carte("L'anneau entre les mains", "Bras tendus, vous pressez l'anneau sans hausser les épaules, puis vous relâchez.", "coffret-4-anneau.jpg", True),
        carte("La sangle sous le pied", "Assise ou allongée, la sangle accompagne l'étirement de la jambe, sans forcer.", "coffret-5-sangle.jpg", True),
        carte("La bande aux genoux", "En pont ou debout, la bande au-dessus des genoux réveille fessiers et cuisses.", "coffret-6-bandes.jpg", True),
        carte("Tout le corps", "Enchaînez les accessoires pour une séance complète, à votre rythme.", "coffret-2-seances.jpg", True),
    ])
    faq_items = [
        q("Convient-il aux débutants ?", "Oui. Commencez par les bandes les plus souples et des mouvements lents. En cas de douleur, de blessure ou de grossesse, demandez l'avis d'un professionnel de santé avant de commencer."),
        q("Que contient exactement le coffret ?", "Un anneau de 33 cm, un ballon de 25 cm, cinq bandes de résistance, une bande en huit, une bande élastique de 180 cm, une sangle d'étirement en coton, une ceinture de résistance pour les fessiers, une poignée d'étirement pour les bras, une paire de chaussettes antidérapantes, un sac de rangement et un guide d'exercices illustré (en anglais)."),
        q("Comment gonfler le ballon ?", "Retirez le bouchon, insérez l'embout de gonflage, gonflez jusqu'à 25 cm environ, puis replacez le bouchon."),
        q("Les accessoires sont-ils solides ?", "Le ballon est en PVC souple anti-éclatement (fiche fournisseur). Rangez les bandes à l'abri du soleil pour qu'elles gardent leur élasticité."),
        q("Peut-on l'emporter ?", "Tout tient dans le sac de rangement : le coffret vous suit en voyage ou à la salle."),
        LIVRAISON_OFFERTE,
        RETOUR,
    ]
    return landing(principal, [("exercices", exercices)], faq_items)


def page_quiz():
    return {"sections": {"quiz": quiz("page")}, "order": ["quiz"]}


def collection():
    return {"sections": {"main": section("collection", {
        "par_page": 12, "libelle_familles": "Les familles",
        "texte_vide": "Cette famille arrive bientôt. En attendant, découvrez les autres familles.",
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
