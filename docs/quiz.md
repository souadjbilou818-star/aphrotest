# Le quiz « Trouver mon équipement »

Section : `sections/aplomb-quiz.liquid`. Script : `assets/aplomb-quiz.js`, chargé seulement par cette section.
On le trouve à deux endroits : sur l’accueil (disposition « Intégré ») et sur la page `trouver-mon-equipement`, qui utilise le modèle `page.pilates-quiz` (disposition « Page dédiée »).

## Ce que voit la visiteuse

1. Quatre questions, une à la fois. La barre de progression a 4 segments et le texte « Question n sur 4 » est annoncé aux lecteurs d’écran.
2. **Au toucher ou au clic**, choisir une réponse passe à la question suivante après 220 ms, sans délai si l’utilisateur a demandé moins de mouvement.
3. **Au clavier**, les flèches changent la réponse sans rien valider. Entrée ou le bouton « Continuer » valide.
4. « Continuer » sans réponse affiche un message (`role="alert"`) et place le focus sur la première réponse.
5. « Retour » revient à la question précédente sans perdre les réponses.
6. Le lien « Passer et voir la boutique » reste visible à chaque étape. Le quiz n’est jamais obligatoire.
7. Le résultat affiche :
   - le produit recommandé, avec son prix réel ;
   - le bouton d’achat ou la liste d’attente, selon l’état du produit ;
   - les arguments tirés des réponses ;
   - les faits vérifiés : dimensions et poids, si les metafields sont remplis ;
   - le récapitulatif des réponses ;
   - « Refaire le quiz » ;
   - une note médicale.

## Mémoire et historique

- Les réponses sont gardées dans `sessionStorage` (clé `aplomb-quiz:<identifiant>`) jusqu’à la fermeture de l’onglet. Aucune donnée personnelle n’y est enregistrée.
- Au rechargement, la visiteuse retrouve son étape, ou son résultat.
- **En page dédiée**, chaque étape crée une entrée d’historique, et le bouton Retour du navigateur revient à la question précédente.
- **En disposition intégrée**, le quiz ne touche pas à l’historique.

## Recommandation

Chaque réponse oriente vers une ou deux familles. La question a un poids de 1 à 3. Une réponse qui oriente vers une famille donne `2 × poids` points à cette famille. Si elle oriente vers deux familles, chacune reçoit `poids` points.

- **Égalité.** On départage par la famille de la question au poids le plus fort. Si l’égalité persiste, COULISSE l’emporte.
- **Écart.** Une réponse peut écarter une famille. Par défaut, « Un petit espace » écarte les Reformers Atelier. Si la famille écartée arrivait en tête, on recommande la suivante, et le résultat explique pourquoi.

Réglages par défaut (`tools/build_templates.py`) :

| Question (poids) | Réponse | Oriente vers | Écarte |
|---|---|---|---|
| Objectif (1) | Renforcement et tonicité | Coulisse + Atelier | — |
| | Mobilité et souplesse | Essentiels + Coulisse | — |
| | Reprendre une activité régulière | Essentiels + Coulisse | — |
| | Installer une routine Pilates chez soi | Coulisse | — |
| Niveau (1) | Je débute | Essentiels + Coulisse | — |
| | J’ai déjà pratiqué | Coulisse | — |
| | Je pratique régulièrement | Coulisse + Atelier | — |
| Équipement (3) | Un kit simple et accessible | Essentiels | — |
| | Un appareil compact et polyvalent | Coulisse | — |
| | Une expérience proche d’un studio | Atelier | — |
| Espace (2) | Un petit espace | Essentiels + Coulisse | Atelier |
| | Une pièce polyvalente | Coulisse + Atelier | — |
| | Un espace dédié | Atelier | — |

Cas testés (`tools/tests/parcours.js`) :

- « compact » donne COULISSE ;
- « kit simple » donne Les Essentiels ;
- « studio » avec « petit espace » donne COULISSE, avec l’explication de l’écart.

## Modifier le quiz dans l’éditeur de thème

- Chaque question est un bloc, jusqu’à 6. Pour chacune, on règle l’identifiant de mesure, la question, l’aide et le poids.
- Chaque bloc a jusqu’à 4 réponses. Pour chaque réponse, on règle le libellé, l’orientation, l’argument affiché dans le résultat et ce qu’elle écarte.
- Dans les réglages de la section, on choisit le produit recommandé pour chaque famille et le texte « pourquoi ».
- **Un produit en brouillon** n’existe pas pour la boutique. Le résultat affiche alors le nom de la famille et une liste d’attente taguée `quiz,<famille>`.

## Mesure

Événements publiés par `window.aplomb.suivre`. Le détail est dans `docs/analytics.md`.

| Événement | Quand | Données |
|---|---|---|
| `aplomb_quiz_started` | Première réponse choisie | `quiz_id`, `mode` |
| `aplomb_quiz_step_completed` | Étape validée (une seconde fois si on revient en arrière) | `etape`, `question`, `reponse` |
| `aplomb_quiz_completed` | Résultat calculé | `reponses` (libellés) |
| `aplomb_recommendation_displayed` | Résultat affiché | `famille`, `produit_id`, `produit_titre`, `famille_ecartee` |
| `aplomb_recommendation_cta` | Clic sur un bouton ou lien du résultat | `famille`, `action` (`produit`, `famille`, `panier`, `liste_attente`) |
| `aplomb_quiz_exit` | Clic sur « voir la boutique » | `etape` |
| `aplomb_quiz_restarted` | « Refaire le quiz » | — |
