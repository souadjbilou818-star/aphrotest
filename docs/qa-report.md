# Rapport QA : L’Aplomb v3

Date : 6 novembre 2026. Thème testé : dépôt au commit courant, et thème Shopify non publié `210406211921`.
Tous les chiffres ci-dessous viennent d’exécutions réelles. Les fichiers bruts sont dans `docs/qa/resultats.json` et `design/captures/`.

## 1. Contrôles statiques

| Contrôle | Résultat |
|---|---|
| Shopify Theme Check (CLI) | **77 fichiers, 0 problème** |
| Analyse Liquid stricte (gem `liquid` 5.14, `error_mode: :strict`) | **0 erreur**. Cette analyse a trouvé une erreur que Theme Check laissait passer : une chaîne `'{n}'` dans une balise `{{ }}` du quiz. Shopify refusait le ZIP à cause d’elle ; elle est corrigée. |
| Schémas des sections (JSON) | Valides, 32 sections lues |
| Import du thème par Shopify (`themeCreate`) | Accepté. 91 fichiers ; sommes MD5 identiques au dépôt sur les fichiers vérifiés. |

## 2. Tests de parcours automatisés

Script : `tools/tests/parcours.js`, avec Playwright et Chromium, sur le serveur d’aperçu local `tools/apercu/serveur.js`. Ce serveur fait le rendu Liquid et simule le catalogue et l’API panier (`/cart/add.js`, `/cart/change.js`, Section Rendering).

**19 tests sur 19 réussis :**

1. Quiz :
   - message d’erreur sans réponse, avec le focus sur la première réponse ;
   - avance automatique au toucher, mais pas aux flèches du clavier ;
   - « Retour » garde les réponses ;
   - résultat COULISSE, avec arguments et récapitulatif ;
   - les 4 étapes et les 4 événements de mesure ;
   - le résultat est restauré après un rechargement ;
   - « Recommencer » efface les réponses.
2. Quiz : « studio » avec « petit espace » donne COULISSE, et l’écart des Reformers Atelier est expliqué.
3. Quiz : « kit simple » donne Les Essentiels.
4. Quiz en page dédiée : le bouton Retour du navigateur revient d’une question, sans quitter la page. Un seul `h1`.
5. Ajout au panier depuis la recommandation : le tiroir s’ouvre, le compteur passe à 1 et le clic est mesuré.
6. Fiche produit :
   - la variante Studio met à jour le prix, l’URL `?variant=` et le libellé du bouton ;
   - le complément épuisé n’est pas proposé ;
   - produit et complément arrivent ensemble dans le panier, total 207 €.
7. Panier :
   - les boutons « + » et « − » fonctionnent ;
   - la limite de stock affiche un message d’erreur lisible, et le panier se resynchronise ;
   - retirer un article remet le compteur à 0 ;
   - le passage au paiement passe par le formulaire natif `/cart` (`name=checkout`) puis par `/checkout`.
8. Page panier : quantité modifiée sans rechargement, paiement.
9. Barre collante sur mobile : elle apparaît après le bloc d’achat, même après un défilement brusque, et ajoute au panier.
10. Galerie :
    - flèches et compteur ;
    - visionneuse avec zoom, clavier et Échap ;
    - le focus revient à l’image ;
    - la mention « Image générée » est présente.
11. Produit marqué liste d’attente en mode Vente (ATELIER) : aucun bouton d’achat, formulaire tagué `atelier-chene`.
12. Collection : la mention « Épuisé » est affichée et la famille courante est signalée.
13. Liste d’attente, produits en brouillon et collections non publiées (le cas réel actuel) :
    - aucun bouton d’achat, aucun prix « 0 € » ;
    - aucun lien vers une page 404, aucun menu vide ;
    - quiz avec liste d’attente taguée `quiz,coulisse` ;
    - pas de mention « Expédié depuis la France » ;
    - aucune erreur dans la console.
14. à 19. Largeurs **320, 375, 390, 768, 1024 et 1440 px**, sur 6 pages (accueil, deux fiches produit, quiz, collection, panier) : **aucun débordement horizontal, aucune erreur dans la console**. Captures à 390 et 1440 px dans `design/captures/storefront/`.

**Ce que ces tests ne prouvent pas.** Le panier simulé reproduit l’API de Shopify, mais pas tout son comportement : remises, taxes, limites réelles. Le vrai tunnel de paiement n’a pas été testé, parce qu’aucun produit n’est actif (et l’activer demande votre accord). Voir la section 6.

## 3. Vérification sur Shopify (aperçu du thème non publié)

Testé dans Chromium sur `?preview_theme_id=210406211921`, sans compte connecté, à 390 et 1440 px :

- le thème servi est bien le v3 (`Shopify.theme.id = 210406211921`) ;
- aucun débordement horizontal, **aucune erreur JavaScript venant du thème**, aucune image cassée. Les erreurs de console viennent de scripts Shopify : `shop.app/pay/hop` (CSP), `monorail`, `api/collect` ;
- le quiz va jusqu’au bout et recommande COULISSE avec une liste d’attente. Les 7 événements `aplomb_*` sont émis ;
- le bandeau cookies natif de Shopify est présent.

Trois anomalies vues **uniquement sur Shopify**, toutes corrigées et redéployées :

1. Une collection non publiée reste lisible en Liquid, mais sa page renvoie une 404. Correctif : le thème vérifie `published_at`.
2. Un réglage produit qui pointe vers un brouillon renvoie un objet creux : lien vide, « 0 € ». Correctif : le thème vérifie le handle.
3. Les réglages globaux absents de `settings_data.json` ne prennent pas leur valeur par défaut : devise et méta-description étaient vides. Correctif : tous les réglages sont écrits explicitement.

Captures : `design/captures/shopify-v3/`.

## 4. Performance et accessibilité (Lighthouse 12.6, mobile, réseau simulé)

**Serveur local.** Pas de compression, pas de redimensionnement d’image, pas de cache : c’est la pire situation pour les ressources du thème.

| Page | Perf. | Access. | Bonnes pratiques | SEO | LCP | CLS | TBT |
|---|---|---|---|---|---|---|---|
| Accueil | 94 | 100 | 100 | 100 | 2,9 s | 0 | 0 ms |
| COULISSE 01 | 96 | 100 | 100 | 100 | 2,6 s | 0,011 | 50 ms |
| Quiz | 96 | 100 | 100 | 100 | 2,7 s | 0 | 0 ms |
| Collection | 97 | 100 | 100 | 100 | 2,6 s | 0 | 20 ms |
| La Trousse (3 images) | 79 | 100 | 100 | 100 | 5,6 s | 0 | 20 ms |

Pour La Trousse, l’écart vient du serveur local. Il envoie l’image JPEG d’origine (1536 px) au lieu de la version WebP redimensionnée du CDN de Shopify. Le thème demande bien `srcset` de 480 à 1600 px et `fetchpriority="high"` sur la première image.

**Aperçu Shopify (accueil)** : performance 67, accessibilité 97, bonnes pratiques 75, SEO 92 (avant le correctif de la méta-description). LCP 4,6 s, TBT 520 ms, 167 requêtes.

Le temps de calcul principal vient des scripts de la plateforme :

| Script | Temps de calcul |
|---|---|
| Web Pixels Manager | 447 ms |
| perf-kit | 156 ms |
| Shop Pay (shop-js) | 68 ms |
| Bannière de consentement | 38 ms |
| Barre d’aperçu | 40 ms |

L’échec `frame-title` vient de l’iframe de la barre d’aperçu, qui n’existe pas sur la boutique publiée. Le LCP mesuré est un paragraphe du bandeau cookies.

**Ces chiffres ne valent pas mesure réelle.** Les objectifs du brief (LCP ≤ 2,5 s, INP ≤ 200 ms, CLS ≤ 0,1 au 75e centile) se vérifient sur la boutique publiée, avec les vrais visiteurs. Où les lire : Shopify > Analyse > Vitesse de la boutique web.

**Accessibilité vérifiée :**

- un seul `h1` par page et une hiérarchie de titres respectée ;
- lien d’évitement ;
- focus visible ;
- étiquettes de formulaires ;
- erreurs annoncées (`role="alert"`) ;
- progression du quiz annoncée (`aria-live`) ;
- tiroir et visionneuse en `<dialog>` modal, avec retour du focus ;
- barre collante en `inert` quand elle est cachée ;
- `prefers-reduced-motion` respecté (dessin figé, vidéos en pause, transitions coupées) ;
- contrastes vérifiés (voir `assets/aplomb-tokens.css`).

## 5. Conformité (contrôles de contenu)

- Ni « reformer de studio » ni « reformer professionnel » pour nos produits. COULISSE 01 est décrit partout comme **n’étant pas un reformer**.
- Rien n’est inventé : ni avis, ni note, ni chiffre de vente, ni compte à rebours, ni prix barré, ni stock limité, ni certification. La section Avis reste masquée tant qu’elle n’a pas d’avis réels.
- Aucune charge maximale, mesure ni dB affichés tant que les metafields sont vides.
- « Expédié depuis la France » n’apparaît qu’en mode Vente.
- Les mots « acompte » et « arrhes » ne sont pas employés.
- Les images générées portent la mention « Image générée », et aucune ne montre un produit.
- Les placeholders entre crochets ([SIREN], [ADRESSE], [DATE D’EXPÉDITION]…) restent masqués sur la boutique. Ils ne figurent que dans les pages légales non publiées.

## 6. Blocages et points ouverts

| # | Blocage | Pourquoi | Qui le lève |
|---|---|---|---|
| 1 | **Le thème public est l’ancienne version, et la boutique n’a pas de mot de passe** | Le thème `210400575825` est passé MAIN. Il montre un « mini-reformer » à chariot qui ne correspond plus à COULISSE 01. | Vous : remettre le mot de passe, ou publier le v3 |
| 2 | Pas de test du vrai tunnel de paiement | Produits en brouillon. Les activer est une action commerciale qui demande votre accord. | Vous |
| 3 | Pas de photos réelles des produits | Pas d’échantillons validés | Sourcing |
| 4 | Prix, contenus des éditions et composition de La Trousse provisoires | Sourcing non validé | Vous / fournisseur |
| 5 | Mentions légales, GPSR, encadré de garantie légale, IDU Ecologic | Informations de l’entreprise manquantes | Vous |
| 6 | Mesures (cotes, poids, charge) | À mesurer sur échantillon | Sourcing |
| 7 | Le dossier `C:\Users\ASUS ROG\Downloads\betterme-clone` n’a pas pu être lu | La session tourne dans le cloud. Seuls les 5 fichiers HTML envoyés ont été analysés (voir `docs/reference-audit.md`). | — |
| 8 | Le pixel GA4/Meta n’est pas installé | Pas d’identifiant. Une installation non autorisée enfreindrait la consigne. | Vous |
| 9 | Le dépôt GitHub est public | Il expose `strategie/` (marges, coûts) | Vous : passer le dépôt en privé |
