# Catalogue et correspondances

Tous les produits sont en **BROUILLON**. Les prix sont **provisoires** : sourcing et logistique ne sont pas encore validés. Ils restent dans les fourchettes du brief.

| Famille | Produit (handle) | Modèle | Variantes et prix provisoires | Collection | Metafields remplis |
|---|---|---|---|---|---|
| 02 Coulisse | COULISSE 01 (`coulisse-01`) | `product` (défaut) | Essentielle 149 € · Studio 189 € | `coulisse` | accroche, famille, complements (chaussettes, patins), `contenu` par variante |
| 01 Les Essentiels | La Trousse (`la-trousse`) | `product.essentiels` | 89 € | `les-essentiels` | accroche, famille |
| 03 Reformers Atelier | ATELIER Chêne (`atelier-chene`) | `product.atelier` | 1 490 € | `reformers-atelier` | accroche, famille, **liste_attente = vrai** |
| Accessoires | Les chaussettes L’Aplomb (`chaussettes`) | `product` | 18 € | `accessoires` | famille |
| Accessoires | Les patins feutre (`patins-feutre`) | `product` | 15 € | `accessoires` | famille |
| Service | Réservation prioritaire (`reservation-prioritaire`) | `product` | 19 € (sans expédition, stock non suivi) | — | — |

Fourchettes du brief :

| Famille | Fourchette | Produit en ligne |
|---|---|---|
| Les Essentiels | 69 à 129 € | La Trousse, 89 € |
| Coulisse | 129 à 189 € | COULISSE 01, 149 et 189 € |
| Reformers Atelier | 990 à 1 590 € | ATELIER Chêne, 1 490 € |

Les accessoires sont gardés hors des familles. Sinon, le « dès 15 € » d’un accessoire fausserait le prix d’entrée affiché pour Les Essentiels.

## Où le thème lit chaque donnée

| Donnée | Source | Affichée dans |
|---|---|---|
| Prix, « dès … » | `product.price_min`, prix de la variante | Cartes, fiche, vedette, quiz, comparatif (prix minimum de chaque collection) |
| Disponibilité | `variant.available` et état commercial (`snippets/etat-produit.liquid`) | Fiche (« Disponible », « Épuisé », « Pas encore en vente »), cartes |
| État commercial | Réglage `launch_mode` et metafield `aplomb.liste_attente` | Bouton d’achat, réservation ou liste d’attente |
| Famille | `aplomb.famille`, ou à défaut le type de produit | Surtitre de la fiche, cartes |
| Accroche | `aplomb.accroche`, ou à défaut le réglage de section | Fiche, cartes |
| Contenu d’une édition | `aplomb.contenu` de la variante | Sous chaque choix d’édition |
| Compléments | `aplomb.complements` (liste de produits) | Cases à cocher sous le bouton d’achat, seulement s’ils sont en vente et disponibles |
| Cotes du dessin A à E | `aplomb.longueur_mm`, `largeur_mm`, `course_mm`, `longueur_plie_mm`, `hauteur_mm` | Dessin technique et liste des cotes (produit vedette) |
| Fiche technique | `aplomb.dimensions_deplie`, `dimensions_plie`, `poids`, `charge_max`, `materiaux`, `resistance_elastiques`, `contenu_coffret` | Section Fiche technique, faits du quiz. **Aucune ligne ne s’affiche si le champ est vide.** |
| Sécurité (GPSR) | `gpsr.fabricant`, `adresse`, `email`, `reference`, `avertissements`, `notice_url` | Section Sécurité du produit, masquée si tout est vide |
| Numéro de famille | `aplomb.numero` (collection) | En-tête de la page collection |
| Médias | Médias du produit (images, vidéos) | Galerie, cartes, résultat du quiz |

## Recommandations du quiz

Dans le modèle de l’accueil et dans `page.pilates-quiz` :

| Famille | Produit recommandé |
|---|---|
| Les Essentiels | `la-trousse` |
| Coulisse | `coulisse-01` |
| Reformers Atelier | `atelier-chene` |

Pour en changer : éditeur de thème > section Quiz > Recommandations.

## Variantes du libellé CTA

Le bouton d’achat s’affiche « Ajouter au panier — 149 € ». Le prix suit la variante choisie. Sur mobile, la barre collante dit « Ajouter au panier » et envoie le même formulaire.
