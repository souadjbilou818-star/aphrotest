# Bible des images générées — L’Aplomb

Objectif : des images générées qu’on prend pour une vraie séance photo, et qui disent vrai sur le produit.
Une image qui ne passe pas la liste de contrôle (§ 8) ne va pas sur le site.

---

## 1. Ce qui est permis, ce qui ne l’est pas

| Sujet | Génération | Pourquoi |
|---|---|---|
| Ambiance sans produit (soirée, lumière sur le parquet, velours, coffret) | IA libre | Aucun risque de tromper sur le produit. |
| Tout plan où le produit apparaît | IA **à partir de photos du produit réel** (image de référence + retouche locale) | Une image qui montre un produit différent de celui vendu est une pratique commerciale trompeuse (art. L121-2 du Code de la consommation). |
| Plan 03, vidéo « son réel » | **Tournage réel obligatoire** | Une vidéo générée ne peut pas porter la mention « son réel ». |
| Visage présenté comme cliente, bêta-testeuse ou avis | **Jamais** | Faux avis. |

**Fidélité produit.** Le mini-reformer L’Aplomb, c’est : un plateau bois, deux rails acier, un chariot rembourré sur roues PU, des élastiques (pas de ressorts), une barre d’ancrage, une charnière centrale, et des patins feutre pour l’édition Studio.
N’apparaissent jamais, sauf s’ils existent sur le produit réel : une barre de pieds, des montants, des cordes ou des poulies, des cales d’épaules, des ressorts, des roulettes de transport, un cadre sur pieds.
Le nombre d’élastiques, la teinte du bois, la couleur du chariot et la finition des rails doivent correspondre au produit livré.

**Mention obligatoire.** Chaque image générée porte « Image générée » dans sa légende, en petites capitales, comme un crédit photo de programme.
Raison : le règlement européen sur l’IA (art. 50) impose depuis le 2 août 2026 de signaler les images réalistes générées qui montrent des personnes ou des lieux.

**Alcool.** Pas de coupe sur les visuels de produit. Sur la soirée, préférer une version sans coupe : associer pilates et alcool brouille le message.

---

## 2. La muse (une seule, sur toutes les images)

Femme française d’une trentaine d’années, peau olive, cheveux brun foncé en chignon bas et souple avec quelques mèches libres, sourcils naturels, maquillage minimal, lèvres rosées, petites boucles d’oreilles pendantes, regard calme, long cou, port de danseuse.

- Générer d’abord une **planche de personnage** (face, trois-quarts, profil, dos), puis s’en servir comme **référence de personnage** dans chaque image : `--oref` ou `--cref` sur Midjourney, référence d’image sur Flux Kontext, ou un petit LoRA entraîné sur la planche.
- La soirée du plan 09 sert de base au visage.

Garde-robe : justaucorps à manches longues, encolure dégagée, oxblood (#5B1A1E) ou forest (#1F3A2F) ; chaussettes antidérapantes ivoire. Aucun logo visible, aucune transpiration.

## 3. L’appartement (un seul, toujours le même)

Haussmannien, troisième étage, Paris.

- **Parquet :** chêne posé en **point de Hongrie**, c’est-à-dire en lames coupées en biais qui se rejoignent sur une ligne droite. Ce n’est pas du bâton rompu, où les lames se croisent en escalier.
- **Murs et plafond :** moulures et boiseries peintes en ivoire, une cheminée en marbre clair.
- **Fenêtres :** hautes fenêtres à la française, garde-corps en fer forgé noir.
- **Matières :** voilages de lin, un fauteuil en velours forest. Aucun désordre, aucune plante au sol.
- **Lumière :** soleil d’hiver rasant, une seule source (la fenêtre), longues ombres de croisillons sur le sol.

## 4. Style photo

Plein format, 35 ou 50 mm (100 mm macro pour les détails), f/2.8, ISO 400.
Lumière naturelle uniquement, rendu Kodak Portra 400, grain fin, peau avec son vrai grain.
Pas de HDR, pas de flou en bulles, pas de saturation forcée.

Après génération, chaque image passe par l’étalonnage maison (`tools/etalonnage.py`) : noirs vers ink, blancs plafonnés à chalk, couleurs légèrement désaturées, grain identique sur toutes les images.

## 5. Technique

- **Définition :** au moins 3 000 px sur le grand côté, sRGB. Générer en haute définition ou agrandir avec un outil qui recrée le détail. Un simple agrandissement ne suffit pas.
- **Ratios :** 3:2, 4:5, 1:1 ou 16:9, selon le cadre (voir § 7).
- **Zone de texte :** garder un tiers vide du côté indiqué quand un titre se pose dessus.
- **Logo :** jamais généré par l’IA, qui le déforme. Il est posé ensuite, en dorure (`tools/dorure.py`) ou en gaufrage.
- **Fichiers :** `plan-NN-sujet.jpg`, JPEG qualité 85 à 90, 2 Mo au plus, envoyés dans Shopify > Contenu > Fichiers.

## 6. Négatif (à ajouter à chaque prompt)

```
--no text, letters, logo, watermark, signage, extra fingers, fused fingers, deformed hands, plastic skin, airbrushed skin, sweat, gym, mirror, neon, LED strip, herringbone parquet, carpet, clutter, footbar, uprights, ropes, pulleys, springs, legs under the board, frame on legs, HDR, bokeh balls, oversaturated colors
```

Bloc de style, à coller à la fin de chaque prompt :

```
editorial interior photograph, Parisian Haussmann apartment, oak point de Hongrie chevron parquet with planks cut at 45 degrees meeting on a straight centre line, ivory-painted wall mouldings, tall French windows with black wrought-iron railing, low winter sunlight raking across the floor, long soft window shadows, quiet luxury, restrained, palette of chalk #F3EFE7, stone #DDD5C7, ink #1B1D22, forest velvet #1F3A2F, oxblood #5B1A1E, full-frame camera, 50mm lens, f/2.8, natural light only, Kodak Portra 400, fine film grain, true-to-life textures
```

## 7. Plans et prompts

`[PRODUIT]` désigne l’image de référence du produit réel. Elle est obligatoire pour les plans marqués « d’après photo ».

### Plan 01 — Le mini-reformer sur parquet, plongée à 45° · d’après photo · 3:2
```
top-down 45-degree view of [PRODUIT] lying on the parquet, light oak board, two brushed steel rails, padded carriage on small polyurethane wheels, resistance bands clipped to the anchor bar, nobody in frame, empty floor on the left third for a headline, [STYLE]
```
Image de référence à forte influence ; ne retoucher que le sol et la lumière.

### Plan 02 — Rails et roues, en macro · d’après photo · 1:1
```
macro photograph, focus on one polyurethane wheel resting on a brushed steel rail of [PRODUIT], the rail recedes diagonally out of focus, oak grain visible, warm raking light, 100mm macro f/4, [STYLE]
```

### Plan 03 — Le chariot en mouvement, son réel · tournage réel
Téléphone en 4K, posé au sol. Un aller-retour complet du chariot en 10 à 12 secondes, micro près des rails, aucune musique, aucun montage sonore.

### Plan 04 — Le pliage en trois temps · d’après photo · 3 × 4:5
Même cadrage pour les trois images : déplié, à moitié plié sur la charnière, plié. On ne voit que les mains de la muse et le bas de ses manches oxblood.
```
overhead view, the muse's hands folding [PRODUIT] at its central hinge, step [1|2|3] of 3, oxblood long sleeves, identical framing, [STYLE]
```

### Plan 05 — Rangé debout contre une moulure · d’après photo · 4:5
```
[PRODUIT] folded and standing upright behind a tall panelled door with ornate mouldings, the edge of a forest velvet curtain in frame, daylight, nobody, [STYLE]
```

### Plan 06 — Trois postures · d’après photo + muse · 3 × 4:5
Les trois postures du programme, validées par une professeure de Pilates avant génération : S1 Alignement, S2 Centre, S3 Chaîne postérieure. Corps aligné, visage calme, aucune grimace.
```
the muse practising [posture] on [PRODUIT], long aligned spine, calm face, oxblood long-sleeve unitard, ivory grip socks, side view at floor height, [STYLE]
```
L’image actuelle (gainage latéral sur tapis) reste **provisoire** : parquet droit et non en point de Hongrie, mur décrépi, pas de produit.

### Plan 07 — Le coffret · IA libre si l’emballage réel lui ressemble · 3:2
Toile forest, ruban de satin bordeaux, carte crème, socle de travertin. Le logo est posé ensuite en dorure laiton, le monogramme est gaufré à sec sur la carte.
Si l’emballage livré est un carton brun, ce visuel devient une promesse : le réserver aux réseaux sociaux.

### Plan 08 — Les feutres sur le parquet · d’après photo · 3:2
```
floor-level close-up, felt pads under the oak board of [PRODUIT] resting on point de Hongrie parquet, no scratches, raking light, [STYLE]
```

### Plan 09 — L’élégance publique · IA libre · 3:2
Base : la soirée actuelle. La régénérer en haute définition avec la même muse. Remplacer la coupe par une pochette du soir, ou ne rien mettre dans sa main. Garder l’Opéra, les chandelles et le velours rouge.
```
candid evening photograph, the muse in an oxblood satin halter gown seen from the back, looking over her shoulder with a quiet smile, a Parisian salon with gilded mouldings, candlelight, red velvet curtains, the Eiffel Tower glowing through a tall window, guests in black tie softly out of focus, 35mm f/1.8, Kodak Portra 800, fine grain
```

### Plan 10 — La housse de l’édition Studio · d’après photo de la housse · 4:5
La vraie housse en toile avec sa sangle, suspendue à une patère en laiton, sur une porte laquée oxblood.
Le sac et les gants de la référence actuelle ne font pas partie de l’offre : réserver cette image aux réseaux sociaux.

### Plan 11 — Lumière d’hiver · IA libre · 16:9 et 4:5
```
empty Haussmann room, point de Hongrie oak parquet, low winter sun through French windows casting long window-frame shadows across the floor, nothing else in the room, [STYLE]
```
Sert d’ouverture d’acte ou de fond derrière le dessin technique.

### Plan 12 — Velours et laiton · IA libre · 4:5
```
detail, forest green velvet curtain gathered with a brass tieback, ivory moulding, soft side light, [STYLE]
```

## 8. Contrôle qualité, image par image

1. Mains : cinq doigts, ongles nets, aucune articulation impossible.
2. Visage : yeux alignés, boucles d’oreilles identiques, dents naturelles, cheveux sans mèches qui fondent dans le décor.
3. Corps : posture réaliste et sûre, validée pour les plans d’exercice.
4. Produit : conforme à la liste du § 1, pièce par pièce.
5. Parquet : point de Hongrie (pas de bâton rompu), lames régulières, joint central droit.
6. Architecture : moulures symétriques, fenêtres à la française, garde-corps continu, aucune perspective qui ploie.
7. Lumière : une seule source, ombres cohérentes avec la fenêtre.
8. Aucun texte parasite, aucune fausse signature, aucun filigrane.
9. Définition d’au moins 3 000 px, étalonnage maison appliqué, logo posé ensuite (jamais généré).
10. Légende rédigée et mention « Image générée » présente.

## 9. Verdict sur les images fournies le 5 novembre 2026

| Image | Verdict | À faire |
|---|---|---|
| Soirée, robe bordeaux | Utilisable pour IV. La maison | Régénérer à 3 000 px ou plus ; version sans coupe ; reprendre le drapé à gauche. |
| Coffret toile verte | Utilisable (dorure et gaufrage ajoutés) | Seulement si le coffret réel ressemble à celui-ci. |
| Gainage latéral sur tapis | Provisoire | À refaire sur le produit réel, sur un parquet en point de Hongrie, devant un mur net. |
| Sac et gants, porte laquée | Réseaux sociaux seulement | Le sac ne fait pas partie de l’offre ; plan 10 à refaire avec la vraie housse. |
| Reformer des planches (barre de pieds, cordes, poulies) | Exclu | Ce n’est pas le produit vendu. |
