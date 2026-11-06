# Configuration Shopify

Boutique : `m6cyrf-fz.myshopify.com`.

## État au 6 novembre 2026

### Ce que j’ai créé, rien n’est publié

| Élément | Détail |
|---|---|
| Thème | **« L’Aplomb v3 — trois familles (non publié) »**, id `210406211921`, rôle `UNPUBLISHED`. Les 91 fichiers ont été vérifiés par somme MD5. |
| Produits (6, tous en **BROUILLON**) | `coulisse-01`, `la-trousse`, `atelier-chene`, `chaussettes`, `patins-feutre`, `reservation-prioritaire`. Détail dans `docs/product-mapping.md`. |
| Collections (4, **non publiées**) | `les-essentiels` (n° 01), `coulisse` (n° 02), `reformers-atelier` (n° 03), `accessoires` |
| Pages (5, **non publiées**) | `trouver-mon-equipement` (modèle `page.pilates-quiz`), `notre-histoire`, `livraison-et-retours`, `securite-produit`, `mentions-legales-aplomb` |
| Menu | `aplomb-pied`, pour le pied de page du thème v3. Le menu `main-menu` et le menu `footer` existants n’ont pas été modifiés. |
| Définitions de metafields (24) | `aplomb.*` sur les produits (accroche, famille, liste_attente, complements, cotes A à E en mm, fiche technique), `aplomb.contenu` sur les variantes, `aplomb.numero` sur les collections, `gpsr.*` sur les produits |

### Ce qui n’a pas été touché

- **Le thème en ligne.** Le thème `210400575825` (« L’Aplomb — feuille de salle ») a le rôle **MAIN** : c’est lui que voient les visiteurs. **La boutique n’est pas protégée par mot de passe.** Il n’a été ni publié ni modifié pendant cette session. Il montre l’ancienne version : le « mini-reformer » à chariot unique, qui ne correspond plus à COULISSE 01. Voir « Décisions à prendre ».
- Les pages `veille-*`, le thème « VEILLE — Atelier saisonnier » et les metafields `atelier.*`. Ils semblent appartenir à un autre chantier : rien n’y a été modifié.

## Aperçu du thème v3

Admin > Boutique en ligne > Thèmes > « L’Aplomb v3 » > Aperçu. On peut aussi ouvrir `https://m6cyrf-fz.myshopify.com/?preview_theme_id=210406211921`.

Ce qu’on voit tant que tout est en brouillon :

- le mode **Liste d’attente** ;
- les familles marquées « En préparation » ;
- le produit vedette avec un formulaire de liste d’attente tagué `coulisse-01` ;
- un quiz qui recommande une famille et propose la liste d’attente.

Aucun prix n’est affiché, et aucun lien ne mène à une page 404.

## Décisions à prendre (aucune n’a été exécutée)

1. **Le thème public actuel.** Deux choix possibles :
   - remettre le mot de passe de la boutique, dans Préférences > Accès à la boutique ;
   - publier le thème v3 après relecture, en un clic dans Thèmes > Publier.
2. **Le nom de la boutique.** « Ma boutique 3 » apparaît dans le titre des pages. Il se change dans Paramètres > Détails de la boutique.
3. **Le format monétaire.** Paramètres > Détails de la boutique > Devise > Formatage :
   - « HTML avec devise » : `{{amount_with_comma_separator}} €` ;
   - « HTML sans devise » : `{{amount_with_comma_separator}} €` ;
   - et de même pour les e-mails.
   
   Le thème formate déjà ses prix lui-même (« 1 490 € »), mais le paiement et les e-mails utilisent ce format.
4. **Le double opt-in.** Paramètres > Notifications > Marketing client > « Demander aux clients de confirmer leur abonnement ».
5. **Le bandeau cookies.** Paramètres > Confidentialité des clients > Bannière de cookies, pour l’Union européenne. Il est déjà visible sur l’aperçu.

## Activer la vente, quand vous l’autoriserez

Les étapes, dans l’ordre :

1. Remplir les placeholders des pages légales : [SIREN], [ADRESSE], [IDU ECOLOGIC], [ENCADRÉ GARANTIE LÉGALE — décret 2022-424], [E-MAIL DU SERVICE CLIENT], fabricant GPSR. Remplir aussi les metafields `gpsr.*` de chaque produit.
2. Valider les prix : ils sont provisoires (tag `prix-provisoire`). Renseigner le stock. Les variantes suivent l’inventaire par défaut : sans stock, le produit s’affiche « Épuisé ».
3. Remplir les mesures vérifiées : metafields `aplomb.longueur_mm`, `largeur_mm`, `course_mm`, `longueur_plie_mm`, `hauteur_mm`, ainsi que la fiche technique. Les cotes du dessin et la fiche technique s’affichent automatiquement.
4. Ajouter les vraies photos aux médias des produits (voir `docs/media-requirements.md`).
5. Passer les produits en **Actif** et les publier sur le canal Boutique en ligne. Publier les collections et les pages.
6. Dans le thème, Personnaliser > Réglages du thème > Lancement : passer le mode à **Vente**. Ou à **Réservation**, si l’on vend d’abord la réservation prioritaire à 19 €.
7. Pour un produit encore indisponible en mode Vente (les Reformers Atelier) : cocher le metafield « Liste d’attente (même en mode Vente) ». Il est déjà coché pour ATELIER Chêne.
8. Installer le pixel personnalisé de `docs/analytics.md`, puis vérifier avec le débogueur de pixels.
9. Passer une commande test avec la passerelle de test de Shopify Payments, puis la rembourser.

## Réglages du thème (Personnaliser > Réglages du thème)

| Groupe | Réglage | Valeur actuelle |
|---|---|---|
| Lancement | Mode | Liste d’attente |
| Lancement | Produit principal / Réservation | `coulisse-01` / `reservation-prioritaire` |
| Lancement | Date d’expédition | [DATE D’EXPÉDITION] : masquée tant qu’elle contient des crochets |
| Boutique | Familles 01, 02, 03 | `les-essentiels`, `coulisse`, `reformers-atelier` |
| Boutique | Page du quiz, page livraison | `trouver-mon-equipement`, `livraison-et-retours` |
| Boutique | Livraison, retours, garantie, paiement | Phrases vraies sans chiffre inventé (modifiables) |
| Boutique | Tiroir de panier après ajout | oui |
| Marque | Police des titres | Cormorant Garamond (Bodoni Moda en option) |
| Marque | Mention « Image générée » | oui |

## Re-déployer depuis le dépôt

Le dépôt GitHub est public. Les fichiers sont envoyés au thème non publié par `themeFilesUpsert`, depuis leurs URL `raw.githubusercontent.com` à un commit précis, puis vérifiés par somme MD5.

Avec Shopify CLI connecté :

```
shopify theme push --theme 210406211921
```

Ne jamais ajouter `--live` ni `--publish`.
