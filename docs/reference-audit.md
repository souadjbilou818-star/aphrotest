# Audit de la référence BetterMe

Date : 6 novembre 2026. Objet : comprendre comment fonctionne le tunnel de conversion de BetterMe Pilates et en garder ce qui sert L’Aplomb. On ne copie pas son apparence.

## 1. Ce qui a pu être lu, et ce qui n’a pas pu l’être

| Source | Statut |
|---|---|
| `C:\Users\ASUS ROG\Downloads\betterme-clone` | **Inaccessible.** La session tourne dans un conteneur cloud et n’a aucun accès au disque Windows. Rien n’a été lu dans ce dossier. |
| betterme-pilates.com et store.betterme.world en direct | Non consultés. L’analyse s’appuie sur les instantanés fournis plutôt que sur un crawl du site en production. |
| 5 instantanés HTML envoyés dans la conversation | **Lus.** Il s’agit de pages rendues côté serveur par Next.js, avec le CSS inline. Les bundles JS et les images n’y sont pas. |

Les cinq fichiers :

1. `Home_Pilates_Workout_Studio.html` (833 Ko) : page d’entrée, avec le bandeau cookies OneTrust ouvert.
2. `Home_Pilates_Workout_Studio_…03_50.html` (285 Ko) : la même page d’entrée.
3. `Quiz…04_14.html` (330 Ko) : écran intermédiaire de preuve sociale.
4. `Quiz…04_29.html` (301 Ko) : question oui/non sur fond photo.
5. `Quiz…10_58.html` (203 Ko) : question à options avec icônes.

**Ce qui manque.** Aucune page produit, aucun panier, aucune page de résultat, d’offre ou de paiement de store.betterme.world. Tout ce qui suit le quiz (présentation du prix, ancrage, page de vente) **n’a donc pas été observé**. Dans la suite, ce qui en est dit est marqué « inféré ».

## 2. Le parcours observé

```
Annonce (paramètres utm_source=google, flow=2707)
  → Page d’entrée « Home Pilates Workout Studio — CHOOSE YOUR AGE »
      4 cartes photo : 18-29 / 30-39 / 40-49 / 50+
      mention légale : « By choosing your age and continuing you agree to… »
  → Écran de preuve : « Over 110,000 women in their 20s have already tried… »
      logos « As featured in », bouton CONTINUE
  → Question : « Have you tried Pilates workouts before? » Yes / No (photo en fond, fixe)
  → Question : « What's your main goal? » Lose weight / Maintain weight and get fit (icônes)
  → … (étapes suivantes non fournies)
  → [inféré] résultat personnalisé, puis offre d’abonnement, puis paiement
```

- **Les 3 premières secondes (observé).** Le titre nomme la catégorie (« Home Pilates Workout Studio »). La seule action possible est de choisir sa tranche d’âge. Il n’y a ni menu, ni lien vers une boutique, ni autre bouton. L’engagement commence dès le premier tap, qui sert à la fois d’accord légal et de réponse à la question 1.
- **En-tête du quiz (observé).** Flèche retour, libellé « My Profile », menu burger, barre de progression segmentée (`progress-bar_list` / `item` / `barFilled`).
- **Pied de page (observé).** FAQ, CGU, Confidentialité, Politique d’abonnement, Remboursement, Impressum, Garantie légale, Règlement des litiges UE, réglages e-Privacy, e-mail du support.
- **Fin du parcours.** Le produit, le prix, les objections et le passage au paiement ne figurent dans aucun fichier. Ils restent **non vérifiés**.

## 3. Jetons de design relevés (observé)

Ces valeurs viennent du CSS inline des instantanés (`--themePrimaryColor`, classes `*_hash`).

| Jeton | Valeur relevée |
|---|---|
| Polices | Gilroy (titres) et Inter (texte), via `--font` et `--secondaryFont`. **Gilroy est propriétaire, on ne la réutilise pas.** |
| Couleurs | Texte `#171717`. Fonds `#FFFCF5` (page), `#FFFEFA`, `#F7F1E8`. Primaire `#311E17`, accent `#816756`. Rouge d’action `#EE505A`/`#E15651`. Verts `#71A31D`/`#3AAE92`. |
| Rayons | Boutons 48 px (`--buttonRadius:24px` sur les petites tailles). Cartes 24/16/12/10 px. Option de quiz 16 px. |
| Tailles de texte | Corps 17 px. Titres 20/24/28/32/40 px. Graisses 400/500/600. Interlignage de 1,05 à 1,5. |
| Hauteurs | Boutons et champs de 48 et 56 px. Option de quiz `min-height:74px`. |
| Bordures | `box-shadow: inset 0 0 0 1px #171717` au repos, 2 px à la sélection. Bordure d’option `1px solid #EFF1F4`. |
| Espacements | Liste d’options `gap:12px` (mobile), 16 px (≥768), 24 px (≥1024). Padding d’option 16, 16/24 puis 24 px. Titre de question `margin:24px` / 40 / 64 px. |
| Grille | Mobile : 2 colonnes, gouttière 16 px, marges 20 px. ≥768 : 8 colonnes, gouttière 24 px. ≥1024 : 12 colonnes, contenu sur 6 colonnes, maximum 1128 px. |
| Points de rupture | 375, 425, 768, 1024, 1280, 1440. |
| Animations | À l’entrée d’une question : `translateY(200px→0)` en 300 ms `ease-in` et opacité en 500 ms (`--scrollDuration`, `--showDuration`). Remplissage de la barre de progression : `width .3s ease-in`. Appui sur une option : `scale(.98)` en 100 ms. Un `@media (prefers-reduced-motion)` est présent. |
| Accessibilité | Les options sont des `<button>`. **Aucun `aria-*` ni `role` dans le DOM du quiz**, en dehors du bandeau OneTrust. |

**Déduit (non observé).** Les questions à choix unique avancent automatiquement au tap : le DOM ne contient pas de bouton « Continuer » sur ces écrans, seulement sur l’écran de preuve. L’état du quiz vit dans le JS (bundles absents), et le rendu côté serveur est fait au premier affichage seulement.

## 4. Les mécanismes et ce qu’on en fait

| # | Mécanisme | Effet attendu | Pour L’Aplomb ? | Mise en œuvre | À tester plutôt que supposer |
|---|---|---|---|---|---|
| 1 | Première action = une réponse de quiz | Coût d’entrée très faible, engagement immédiat | **Oui, en partie.** Le brief interdit de forcer le quiz. | La 1re question est intégrée à l’accueil, à côté d’un accès direct au produit et aux familles. | Taux de démarrage du quiz contre clics directs sur le produit. |
| 2 | Avance automatique au choix | Moins de taps, rythme | **Oui** | Pour un choix unique, sélectionner une option passe à l’étape suivante. Retour et clavier toujours disponibles. Aucune validation bloquante possible. | Taux d’abandon par étape. |
| 3 | Barre de progression segmentée | Montre la fin proche | **Oui** | Quatre segments plus le texte « Question n sur 4 », annoncé aux lecteurs d’écran. | — |
| 4 | Écran de preuve chiffré (« 110 000 femmes ») | Preuve sociale | **Non, aucune donnée réelle.** Un chiffre inventé est interdit. | Remplacé par des faits vérifiables (dimensions, contenu, garanties légales). Le bloc avis reste masqué tant qu’il n’existe pas d’avis réels. | — |
| 5 | Logos « As featured in » | Autorité | **Non.** Aucune parution réelle. | Pas d’emplacement par défaut. | — |
| 6 | Accord légal au premier tap | Moins de friction | **Non.** Ce n’est pas un consentement RGPD valable pour le marketing. | Le quiz ne collecte aucune donnée personnelle. L’e-mail, facultatif, a sa propre case de consentement. | — |
| 7 | Mise en page sans menu pendant le quiz | Concentration | **Partiel** | La page quiz garde l’en-tête de marque. Un lien « Voir la boutique » reste visible à chaque étape. | Taux de fin de quiz avec et sans en-tête complet. |
| 8 | Fond clair et chaud, texte quasi noir, accent unique | Lisibilité, calme | **Oui**, transposé | Ivoire `#F6F2E9`, encre `#0B0F0E`, forêt pour l’action, bordeaux réservé à de rares accents. | — |
| 9 | Cibles tactiles de 56 à 74 px, rayons généreux | Confort au pouce | **Oui** pour les tailles. **Non** pour les rayons : l’identité de L’Aplomb est architecturale. | Options ≥ 64 px, CTA de 52 px, rayons 2 à 4 px. | — |
| 10 | Questions sur l’âge et le poids | Segmentation, personnalisation | **Non.** Ce sont des données sensibles, et elles n’aident pas à choisir l’équipement. | Questions sur l’objectif, le niveau, le type d’équipement et l’espace (brief). | — |
| 11 | Pied de page juridique complet, dont la garantie légale et le règlement des litiges UE | Confiance, conformité | **Oui** | Menu `footer` (mentions légales, CGV, confidentialité, livraison et retours, garantie légale, GPSR, médiation). | — |
| 12 | Offre et prix après le quiz (inféré) | Valeur avant prix | **Non observé.** | La recommandation montre le prix réel du produit Shopify, sans prix barré ni minuterie. | Prix affiché dans le résultat ou seulement sur la fiche produit. |

## 5. Ce qu’on garde comme architecture

- Une colonne de quiz sur mobile, d’au plus **560 px** de large (480 px chez BetterMe, un peu plus ici pour les titres en serif). Sur ordinateur, la question et sa justification tiennent sur 2 colonnes.
- Un en-tête de quiz avec retour, progression segmentée et sortie vers la boutique.
- Des transitions d’étape courtes (180 à 240 ms) en opacité et translation. Si l’utilisateur a demandé moins de mouvement, aucune transition.
- La 1re question vit sur l’accueil. Le quiz complet a sa page (`page.pilates-quiz`) et ses paramètres d’URL.
- Les réponses sont gardées dans `sessionStorage` pour la session seulement. Rien de personnel n’est stocké.

## 6. Ce qui n’a pas pu être vérifié

- Les pages produit, panier et paiement de store.betterme.world, et le comportement de leur CTA collant (dans le CSS fourni, `sticky` n’apparaît qu’une fois, dans une feuille du bandeau cookies).
- La logique de recommandation, l’écran de résultat et la présentation de l’offre.
- Le comportement JS réel : la navigation, l’historique et la validation sont déduits du DOM, pas lus dans le code.
- La disposition sur ordinateur, connue seulement par les règles CSS `min-width:768/1024`. Aucune capture ordinateur n’a été fournie.
