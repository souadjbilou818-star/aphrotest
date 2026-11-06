# L’Aplomb : livraison de la boutique (v3)

Une boutique Shopify Online Store 2.0, en Liquid, CSS et JavaScript natifs, sans dépendance. Elle repose sur le thème Skeleton de Shopify : Dawn n’était pas installé sur la boutique, et le thème existant du projet a été adapté plutôt que remplacé.

## Documents

| Fichier | Contenu |
|---|---|
| `reference-audit.md` | Audit du tunnel BetterMe : observé, déduit, non vérifié |
| `quiz.md` | Comportement du quiz, logique de recommandation, édition |
| `analytics.md` | Plan de marquage, correspondance GA4 et Meta, pixel personnalisé |
| `shopify-config.md` | État de la boutique, décisions à prendre, étapes d’activation |
| `product-mapping.md` | Catalogue, handles, prix provisoires, metafields |
| `media-requirements.md` | Emplacements d’images et de vidéos, règles IA |
| `qa-report.md` | Résultats des tests, Lighthouse, conformité, **blocages** |
| `qa/resultats.json` | Sortie brute des tests de parcours |

## Structure du thème

```
layout/theme.liquid            jetons + composants, scripts différés, tiroir de panier
assets/
  aplomb-tokens.css            palette, typographie, espacements, mouvement
  aplomb-components.css        tous les composants (mobile d’abord)
  aplomb-interactions.js       mesure, variantes, galerie et zoom, barre collante
  aplomb-quiz.js               quiz (chargé par la section quiz seulement)
  aplomb-cart.js               panier AJAX (pas chargé en liste d’attente sans panier)
  aplomb-dessin.js             repli JS de l’animation du dessin
sections/
  header.liquid                familles, quiz, panier
  aplomb-hero.liquid           titre, double appel à l’action, dessin, photo ou vidéo
  aplomb-familles.liquid       les trois familles, prix réels « dès »
  aplomb-vedette.liquid        COULISSE 01 : dessin, nomenclature, cotes, achat
  aplomb-demo.liquid           démonstration (vidéo ou dessin animé) et mouvements
  aplomb-comparatif.liquid     comparatif des familles, prix des collections
  aplomb-quiz.liquid           quiz configurable (questions en blocs)
  aplomb-cloture.liquid        appel final, liste d’attente ou achat
  produit-principal.liquid     fiche : galerie, variantes, disponibilité, compléments
  panier-tiroir.liquid         tiroir (API Section Rendering)
  cart.liquid, collection.liquid
  benefices, etapes, negations, specs, temoignages, garanties, gpsr, faq,
  acte-programme, acte-maison, footer
snippets/
  achat.liquid                 vente, réservation ou liste d’attente selon l’état
  etat-produit.liquid          état commercial d’un produit
  selecteur-variantes.liquid   options et variantes, JSON des variantes
  galerie-produit.liquid       médias, visionneuse
  carte-produit.liquid         carte de collection
  panier-lignes.liquid         lignes du panier (tiroir et page)
  prix.liquid                  « 1 490 € »
  dessin-coulisse.liquid       dessin technique généré (tools/dessin.py)
  liens-familles, picto-famille, icone, cadre, waitlist-form, logo, frise, fonts, meta-tags
templates/
  index.json, product.json (COULISSE), product.essentiels.json, product.atelier.json,
  page.pilates-quiz.json, collection.json, cart.json
config/settings_schema.json    Lancement, Boutique, Marque
locales/fr.default.json        tous les textes de l’interface
```

## Outils

| Commande | Rôle |
|---|---|
| `python3 tools/build_snippets.py` | Régénère le dessin, le logo et la frise |
| `python3 tools/build_templates.py` | Régénère les modèles JSON et leurs textes |
| `python3 tools/typo_theme.py` | Microtypographie française (idempotent) |
| `MODE=vente PORT=8765 node tools/apercu/serveur.js` | Aperçu local avec panier simulé |
| `MODE=waitlist PRODUITS=absents PORT=8766 node tools/apercu/serveur.js` | Aperçu local de l’état actuel (brouillons) |
| `node tools/tests/parcours.js` | Les 19 tests de parcours, avec les deux serveurs lancés |

Le ZIP installable est dans `design/livraison/laplomb-theme-v3.zip`. Pour l’installer : Boutique en ligne > Thèmes > Ajouter un thème > Importer un fichier ZIP. **Ne pas le publier sans relecture.**

## Expériences préparées (à tester, sans vainqueur supposé)

| Hypothèse | Réglage déjà en place |
|---|---|
| Titre du hero | Hero > Titre. Variante proposée : « Le Pilates chez soi, sans studio ni compromis. » |
| Dessin, photo ou vidéo de démonstration dans le hero | Hero > Visuel |
| Bouton principal : produit ou quiz | Hero > Bouton principal |
| Première image produit ou image d’ambiance | Ordre des médias du produit dans Shopify |
| Présentation des compléments | Metafield `aplomb.complements` (0 à 3 produits) et libellé `aplomb.produit.complements` |
| Barre d’achat collante | Section Fiche produit : la barre suit le bloc d’achat. Pour la tester contre « pas de barre », dupliquer le modèle sans elle. |
| Longueur du quiz | Blocs Question (de 3 à 6) |
| Ordre des bénéfices sur la fiche | Ordre des sections et des blocs dans l’éditeur |

Shopify n’a pas d’A/B testing natif sur le thème. Deux façons de faire : dupliquer le thème et comparer sur des périodes équivalentes, ou passer par une application, ce qui demande votre accord si elle est payante. Les événements `aplomb_*` permettent de comparer les tunnels.
