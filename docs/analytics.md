# Mesure et plan de marquage

## Principe

- **Shopify émet lui-même les événements standard** : `page_viewed`, `product_viewed`, `collection_viewed`, `product_added_to_cart`, `cart_viewed`, `checkout_started`, `checkout_completed`. Ils couvrent aussi les ajouts faits par le panier AJAX. Le thème ne les republie pas, donc il n’y a ni doublon ni achat compté deux fois.
- **Le thème publie ses propres événements**, préfixés `aplomb_`, avec `Shopify.analytics.publish(nom, données)`. Ils arrivent aux pixels personnalisés, qui appliquent le consentement de la Customer Privacy API (bandeau cookies natif de Shopify).
- **Les mêmes événements sont poussés dans `window.dataLayer`** de la page. C’est utile pour le débogage, mais le thème ne charge aucun script tiers et n’envoie rien de lui-même.
- **Aucune donnée personnelle** n’entre dans les événements du thème : ni e-mail, ni nom, ni réponse libre.

## Événements du thème

| Événement | Source | Données |
|---|---|---|
| `aplomb_cta_click` | Liens `data-suivi` du hero | `cta` (`hero_produit`, `hero_quiz`), `href` |
| `aplomb_quiz_started` | Quiz | `quiz_id`, `mode` |
| `aplomb_quiz_step_completed` | Quiz | `quiz_id`, `etape`, `question`, `reponse` |
| `aplomb_quiz_completed` | Quiz | `quiz_id`, `reponses` |
| `aplomb_recommendation_displayed` | Quiz | `quiz_id`, `famille`, `produit_id`, `produit_titre`, `famille_ecartee` |
| `aplomb_recommendation_cta` | Quiz | `quiz_id`, `famille`, `action` |
| `aplomb_quiz_exit` / `aplomb_quiz_restarted` | Quiz | `quiz_id`, `etape` |
| `aplomb_ajout_panier_contexte` | Panier AJAX | `contexte` (id du formulaire : `achat-produit-…`, `achat-quiz-coulisse-…`, `achat-vedette-…`), `variant_id`, `quantite`, `complements` |
| `aplomb_panier_ouvert` | Tiroir | — |

`aplomb_ajout_panier_contexte` ne remplace pas `product_added_to_cart`. Il dit seulement **d’où** vient l’ajout : fiche produit, quiz ou produit vedette.

## Correspondance GA4 et Meta

| Étape du tunnel | Événement Shopify ou thème | GA4 | Meta |
|---|---|---|---|
| Vue de page | `page_viewed` | `page_view` | `PageView` |
| Vue produit | `product_viewed` | `view_item` | `ViewContent` |
| Quiz commencé | `aplomb_quiz_started` | `quiz_start` (personnalisé) | `aplomb_quiz_started` (personnalisé) |
| Étape du quiz | `aplomb_quiz_step_completed` | `quiz_step` | — |
| Quiz terminé | `aplomb_quiz_completed` | `quiz_complete` | `CompleteRegistration` (facultatif) |
| Recommandation affichée | `aplomb_recommendation_displayed` | `view_promotion` ou `recommendation_view` | — |
| Ajout au panier | `product_added_to_cart` | `add_to_cart` | `AddToCart` |
| Début du paiement | `checkout_started` | `begin_checkout` | `InitiateCheckout` |
| Achat | `checkout_completed` (**une seule source**) | `purchase` | `Purchase` |

## Installer un pixel personnalisé

Le code se colle dans Shopify > Réglages > Événements clients > Ajouter un pixel personnalisé. L’installation est gratuite.

Pour les autorisations, choisir « Requis » pour l’analyse et pour le marketing. Shopify n’exécute alors le pixel qu’avec le consentement de la visiteuse.

```js
// Pixel personnalisé L’Aplomb : relaie événements standard et événements du thème.
// Remplacer G-XXXXXXX par l’identifiant GA4 quand il existe. Ne rien coller d’autre ici.
const GA4 = 'G-XXXXXXX';
const s = document.createElement('script');
s.async = true;
s.src = `https://www.googletagmanager.com/gtag/js?id=${GA4}`;
document.head.appendChild(s);
window.dataLayer = window.dataLayer || [];
function gtag() { dataLayer.push(arguments); }
gtag('js', new Date());
gtag('config', GA4, { send_page_view: false });

const prixArticle = (v) => ({ item_id: v?.product?.id, item_name: v?.product?.title, item_variant: v?.title, price: v?.price?.amount });

analytics.subscribe('page_viewed', () => gtag('event', 'page_view'));
analytics.subscribe('product_viewed', (e) => {
  const v = e.data.productVariant;
  gtag('event', 'view_item', { currency: v.price.currencyCode, value: v.price.amount, items: [prixArticle(v)] });
});
analytics.subscribe('product_added_to_cart', (e) => {
  const l = e.data.cartLine;
  gtag('event', 'add_to_cart', { currency: l.cost.totalAmount.currencyCode, value: l.cost.totalAmount.amount, items: [{ ...prixArticle(l.merchandise), quantity: l.quantity }] });
});
analytics.subscribe('checkout_started', (e) => {
  const c = e.data.checkout;
  gtag('event', 'begin_checkout', { currency: c.currencyCode, value: c.totalPrice?.amount });
});
analytics.subscribe('checkout_completed', (e) => {
  const c = e.data.checkout;
  gtag('event', 'purchase', { transaction_id: c.order?.id, currency: c.currencyCode, value: c.totalPrice?.amount });
});
['aplomb_quiz_started', 'aplomb_quiz_step_completed', 'aplomb_quiz_completed', 'aplomb_recommendation_displayed',
 'aplomb_recommendation_cta', 'aplomb_ajout_panier_contexte'].forEach((nom) => {
  analytics.subscribe(nom, (e) => gtag('event', nom, e.customData || {}));
});
```

Ce code n’a pas été exécuté sur la boutique : aucun identifiant GA4 n’existe encore. Avant l’activation, il faut le vérifier avec le débogueur de pixels de Shopify et le DebugView de GA4.
