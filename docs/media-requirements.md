# Médias : emplacements et exigences

## Règles communes

- **COULISSE 01 se montre tel qu’il est**. C’est une planche pliable avec deux plateaux rembourrés qui coulissent indépendamment, des rails intégrés, des cordons et des poignées. On ne la remplace jamais par un reformer à chariot, et aucune image générée ne doit inventer sa géométrie.
- **Signaler les images générées par IA.** Une image d’ambiance générée porte la mention « Image générée », comme l’exige l’AI Act (art. 50) :
  - dans une section : cocher « Image générée par IA » ;
  - dans les médias d’un produit : écrire « image générée » dans le texte alternatif.
- **Aucune image générée ne passe pour une photo du produit.** Tant qu’il n’y a pas de vraie photo, le thème affiche le dessin technique (COULISSE) ou un cadre « Photo à venir ».
- **Format.** JPEG ou PNG de haute qualité dans Shopify. Le CDN sert ensuite du WebP ou de l’AVIF, à la bonne taille (`image_url` et `srcset`, de 360 à 2400 px).
- **Chargement.** L’image du premier écran se charge immédiatement (`loading="eager"`, `fetchpriority="high"`). Toutes les autres se chargent en différé.
- **Texte alternatif.** Il décrit ce qu’on voit, en français, en 125 caractères au plus. Il ne répète pas « image de » et ne contient pas de mots-clés en liste.

## Emplacements

| Emplacement | But | Taille conseillée | Ratio | Ordinateur / mobile | Recadrage | Objectif de conversion |
|---|---|---|---|---|---|---|
| **Fiche produit, 1er média** (photo studio) | Montrer le produit entier, sans ambiguïté | 2000 × 2500 | 4:5 (5:4 en grand sur ordinateur) | Grand en tête de grille / premier écran du carrousel | Produit centré, 8 % de marge, fond ivoire ou sable uni | Compréhension immédiate |
| Fiche produit, médias 2 à 4 (détails) | Plateaux, rails, charnière, poignées | 2000 × 2500 | 4:5 | Grille 2 colonnes / carrousel | Gros plan, une pièce par image | Qualité perçue, objections « comment ça marche » |
| Fiche produit, en situation | Une personne sur la planche, mouvement réel | 2000 × 2500 | 4:5 | Idem | Corps entier visible, planche lisible | Se projeter |
| Fiche produit, plié | La planche pliée, rangée | 2000 × 2500 | 4:5 | Idem | Avec un repère d’échelle (porte, meuble) | Objection « où la ranger » |
| Vidéo produit (média Shopify) | Démontrer le glissé des deux plateaux | 1080 × 1350, 20 à 40 s, sous-titrée | 4:5 | Dans la galerie | Plan fixe, mouvement lent | Démonstration |
| Hero (option Photo) | Catégorie et désir au premier coup d’œil | 1600 × 2000 | 4:5 | Colonne droite / sous le texte | Produit et personne lisibles même petits | Clarté, désir. **À tester** contre le dessin animé. |
| Hero (option Vidéo) | Le mouvement en boucle, sans son | 1080 × 1350, 6 à 10 s, < 4 Mo | 4:5 | Idem ; mise en pause si l’utilisateur limite les animations | Boucle propre | Démonstration immédiate. **À tester.** |
| Démonstration (section) | Trois mouvements expliqués | 1920 × 1080 ou 1080 × 1350 | 16:9 ou 4:5 | Pleine colonne | — | Comprendre l’usage |
| Familles (cartes) | Identifier chaque famille | 1200 × 900 | 4:3 | 3 colonnes / carrousel horizontal | Produit seul, même fond pour les trois | Navigation par famille |
| Produit vedette (option photo) | COULISSE 01 en grand | 2000 × 1500 | 4:3 | Colonne gauche / sous le texte | Vue 3/4 plongeante | Mise en avant du produit phare |
| Étapes (comment ça marche) | Déplier, se placer, coulisser | 1200 × 1500 | 4:5 | 3 colonnes / empilées | Même cadrage pour les trois | Simplicité perçue |
| Programme | Une posture, l’ambiance d’une séance | 1200 × 1500 | 4:5 | Cadre étroit | — | Routine, régularité |
| Éditorial « La maison, le soir » | Univers de marque (photographie de soirée) | 2400 × 1600 | 3:2 | Bandeau sombre, seule zone foncée de la page | Sujet décentré, flash naturel | Désirabilité. Ne doit jamais cacher un produit. |
| Cartes produit (collection) | Lecture rapide du catalogue | 1200 × 1500 | 4:5 | Grille auto | Même fond, même échelle pour tous | Comparer, choisir |
| Réseaux sociaux (hors thème) | Publicité, organique | 1080 × 1350 et 1080 × 1920 | 4:5 et 9:16 | — | Zone de sécurité de 250 px en haut et en bas (9:16) | Acquisition. Mêmes règles : pas de fausse géométrie, mention IA. |

## Images disponibles aujourd’hui

Toutes sont dans Shopify > Contenu > Fichiers, et toutes sont **générées**.

| Fichier | Contenu | Usage actuel | Peut-on la mettre en fiche produit ? |
|---|---|---|---|
| `plan-09-soiree.jpg` | Soirée parisienne, robe bordeaux | Éditorial « La maison, le soir » | Non, c’est une ambiance |
| `plan-06-posture-provisoire.jpg` | Gainage latéral sur tapis | Section programme | Non, pas de produit |
| `plan-07-coffret.jpg` | Coffret vert, logo en dorure | Non utilisée sur la boutique | Non, l’emballage n’est pas réel |

**Manque, et bloque la vente :** les photos réelles de COULISSE 01, de La Trousse et d’ATELIER Chêne. Il faut des échantillons validés.
