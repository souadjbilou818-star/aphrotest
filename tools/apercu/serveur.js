/**
 * Serveur d’aperçu local du thème L’Aplomb, pour les tests (Phase C).
 * LiquidJS + objets Shopify simulés + API panier simulée (en mémoire).
 * Ce n’est pas le moteur de Shopify : il sert à tester le rendu, le quiz,
 * le panier AJAX et la navigation vers le paiement, pas à les certifier.
 *
 * Usage : MODE=vente PORT=8765 node tools/apercu/serveur.js
 *   MODE      waitlist | reservation | vente (défaut : vente)
 *   PRODUITS  presents (défaut) | absents  (simule des produits en brouillon et
 *             des collections non publiées, comme sur la boutique avant
 *             l’ouverture : produits vides en Liquid, collections sans published_at)
 *
 * Routes : /  /products/:handle  /collections/:handle  /pages/trouver-mon-equipement
 *          /cart  /checkout  POST /cart/add.js  /cart/change.js  /cart  /contact
 *          GET /cart.js  /assets/*  /design/*  /__reinitialiser (vide le panier)
 */
const fs = require('fs');
const http = require('http');
const path = require('path');
const { Liquid } = require('liquidjs');

const ROOT = path.resolve(__dirname, '..', '..');
const MODE = process.env.MODE || 'vente';
const ABSENTS = process.env.PRODUITS === 'absents';
const PORT = Number(process.env.PORT || 8765);

const lire = (p) => fs.readFileSync(path.join(ROOT, p), 'utf8');
const lireJson = (p) => JSON.parse(lire(p).replace(/^\s*\/\*[\s\S]*?\*\/\s*/, ''));
const locale = lireJson('locales/fr.default.json');

/* ---------- Catalogue simulé ---------- */
const imageIA = (nom, w, h, alt) => ({ src: `/design/images-ia/${nom}`, width: w, height: h, alt, aspect_ratio: w / h });
const TAILLES = {
  'plan-09-soiree.jpg': [1536, 1024], 'plan-07-coffret.jpg': [1536, 1024], 'plan-06-posture-provisoire.jpg': [1024, 1280],
  'atelier-pliable-0-ambiance.jpg': [1122, 1402], '0c2d1da44e298772ffb0f69115cd.jpg': [664, 653], 'e91889c646d686461ef85700d425.jpg': [664, 653],
  'f2e29f8b47bd8b2e338339bf9902.jpg': [669, 635], 'a17a7ed34c2b8a31c3c83caba9d0.jpg': [661, 629], '93040adb410abd48ee6f563c4581.jpg': [667, 658],
};
const imageMedia = (nom, w, h, alt) => ({ src: `/design/medias/${nom}`, width: w, height: h, alt, aspect_ratio: w / h });
let idSeq = 7000;
function variante(produit, title, price, opts = {}) {
  const v = {
    id: ++idSeq, title, price, available: opts.available !== false, options: [title], option1: title,
    url: `/products/${produit}?variant=${idSeq}`,
    inventory_management: opts.stock !== undefined ? 'shopify' : null,
    inventory_policy: 'deny', inventory_quantity: opts.stock,
    metafields: { aplomb: { contenu: opts.contenu } },
  };
  return v;
}
function produit({ id, handle, title, type, variantes, option = 'Édition', media = [], aplomb = {}, suffixe = null, description = '' }) {
  const prix = variantes.map((v) => v.price);
  const p = {
    id, handle, title, type, url: `/products/${handle}`, template_suffix: suffixe, description,
    variants: variantes, price: Math.min(...prix), price_min: Math.min(...prix), price_max: Math.max(...prix),
    price_varies: Math.min(...prix) !== Math.max(...prix), available: variantes.some((v) => v.available),
    has_only_default_variant: variantes.length === 1 && variantes[0].title === 'Default Title',
    options: [option], media,
    featured_media: media[0] || null,
    metafields: { aplomb, gpsr: {} },
  };
  p.selected_or_first_available_variant = variantes.find((v) => v.available) || variantes[0];
  p.options_with_values = [{
    name: option, position: 1, values: variantes.map((v) => v.title), selected_value: p.selected_or_first_available_variant.title,
  }];
  variantes.forEach((v) => { v.product = p; });
  return p;
}
const media = (img, i) => ({ id: 900 + i, media_type: 'image', alt: img.alt, preview_image: img });

const CATALOGUE = [
  produit({
    id: 101, handle: 'coulisse-01', title: 'COULISSE 01', type: 'Coulisse',
    variantes: [
      variante('coulisse-01', 'Essentielle', 14900, { contenu: 'La planche, deux cordons de résistance, deux poignées.' }),
      variante('coulisse-01', 'Studio', 18900, { stock: 3, contenu: 'L’Essentielle, plus des chaussettes antidérapantes et une housse de rangement.' }),
    ],
    aplomb: { accroche: 'Deux plateaux qui coulissent l’un sans l’autre : le travail en glissé du Pilates, chez vous.', dimensions_deplie: '105 × 40 × 3 cm (fiche fournisseur)' },
    description: '<p>Description de test (aperçu local).</p>',
    media: [
      ['0c2d1da44e298772ffb0f69115cd.jpg', 664, 653, 'COULISSE 01 rose : la planche, les deux plateaux coulissants, les poignées et le cordon de résistance'],
      ['e91889c646d686461ef85700d425.jpg', 664, 653, 'COULISSE 01 rose, vue de trois quarts'],
      ['a17a7ed34c2b8a31c3c83caba9d0.jpg', 661, 629, 'COULISSE 01 noir, vue de trois quarts'],
      ['93040adb410abd48ee6f563c4581.jpg', 667, 658, 'Contenu du colis COULISSE 01'],
    ].map(([n, w, h, a], i) => media(imageMedia(n, w, h, a), 30 + i)),
  }),
  produit({
    id: 102, handle: 'la-trousse', title: 'Le Coffret Essentiel, 13 pièces', type: 'Les Essentiels', suffixe: 'essentiels',
    variantes: [variante('la-trousse', 'Default Title', 6900)], option: 'Title',
    aplomb: { accroche: 'Des séances Pilates complètes sur le tapis, avec cinq accessoires rangés dans un sac.', materiaux: 'Ballon en PVC anti-éclatement ; anneau à cœur en fibre de verre', contenu_coffret: 'Anneau 38 cm, ballon 25 cm, 5 bandes, bande en huit, sangle, chaussettes, sac, embout' },
    description: '<p>Description de test (aperçu local).</p>',
    media: [
      ['coffret-1-coffret.jpg', 'Le coffret Les Essentiels, image générée'], ['coffret-2-seances.jpg', 'Six exercices avec le coffret, image générée'],
      ['coffret-3-ballon.jpg', 'Ballon de Pilates 25 cm, image générée'], ['coffret-4-anneau.jpg', 'Anneau de Pilates 38 cm, image générée'],
      ['coffret-5-sangle.jpg', 'Étirement avec la sangle, image générée'], ['coffret-6-bandes.jpg', 'Bande de résistance, image générée'],
    ].map(([n, a], i) => media(imageMedia(n, 1254, 1254, a), 10 + i)),
  }),
  produit({
    id: 107, handle: 'atelier-pliable', title: 'ATELIER Pliable', type: 'Reformers Atelier', suffixe: 'atelier',
    variantes: [variante('atelier-pliable', 'Default Title', 149000)], option: 'Title',
    aplomb: { accroche: 'Le geste du reformer, chez vous : un vrai chariot sur un cadre en acier, qui se plie après la séance.', dimensions_deplie: '197 × 57 × 72,5 cm (fiche fournisseur)', dimensions_plie: '108 × 55 × 29 cm (fiche fournisseur)', poids: '32,5 kg (fiche fournisseur)', materiaux: 'Cadre en acier, ABS, PP, mousse (fiche fournisseur)' },
    description: '<p>Description de test (aperçu local).</p>',
    media: [
      ['atelier-pliable-0-ambiance.jpg', 1122, 1402, 'Reformer ATELIER Pliable dans un salon lumineux, image générée'],
      ['atelier-pliable-1.jpg', 800, 800, 'Reformer pliable ATELIER, vue de trois quarts'], ['atelier-pliable-2-dimensions.jpg', 800, 640, 'Encombrement du reformer déplié'],
      ['atelier-pliable-3-tubes.jpg', 800, 570, 'Tubes de résistance en latex'], ['atelier-pliable-4-vue.jpg', 1024, 1024, 'Reformer pliable ATELIER avec barre de pieds'],
    ].map(([n, w, h, a], i) => media(imageMedia(n, w, h, a), 20 + i)),
  }),
  produit({
    id: 103, handle: 'atelier-chene', title: 'ATELIER Chêne', type: 'Reformers Atelier', suffixe: 'atelier',
    variantes: [variante('atelier-chene', 'Default Title', 149000)], option: 'Title',
    aplomb: { liste_attente: { value: true } },
  }),
  produit({
    id: 104, handle: 'chaussettes', title: 'Les chaussettes L’Aplomb', type: 'Accessoires',
    variantes: [variante('chaussettes', 'Default Title', 1800)], option: 'Title',
  }),
  produit({
    id: 105, handle: 'patins-feutre', title: 'Les patins feutre', type: 'Accessoires',
    variantes: [variante('patins-feutre', 'Default Title', 1500, { available: false })], option: 'Title',
  }),
  produit({
    id: 106, handle: 'reservation-prioritaire', title: 'Réservation prioritaire', type: 'Service',
    variantes: [variante('reservation-prioritaire', 'Default Title', 1900)], option: 'Title',
  }),
];
CATALOGUE.forEach((p) => {
  if (p.has_only_default_variant) p.options_with_values = [];
});
// Compléments proposés sous COULISSE 01 (metafield aplomb.complements)
CATALOGUE[0].metafields.aplomb.complements = { value: ['chaussettes', 'patins-feutre'].map((h) => CATALOGUE.find((p) => p.handle === h)) };
// Un produit en brouillon référencé par un réglage arrive sur Shopify comme un
// objet creux (handle et url vides, prix 0) : on reproduit ce cas.
const CREUX = { id: null, handle: '', url: '', title: '', price: 0, price_min: 0, variants: [], available: false, metafields: { aplomb: {}, gpsr: {} } };
const parHandle = (h) => (ABSENTS ? (h ? CREUX : null) : CATALOGUE.find((p) => p.handle === h) || null);
const toutesVariantes = () => CATALOGUE.flatMap((p) => p.variants);

const collection = (handle, title, produits, numero, description) => ({
  id: handle.length * 1000, handle, title, url: `/collections/${handle}`, description, published_at: '2026-11-01T09:00:00Z',
  products: produits, products_count: produits.length, metafields: { aplomb: { numero } },
});
const COLLECTIONS = {
  'les-essentiels': collection('les-essentiels', 'Les Essentiels', CATALOGUE.filter((p) => p.type === 'Les Essentiels'), '01',
    '<p>Des kits d’accessoires pour pratiquer sur le tapis, sans appareil à ranger.</p>'),
  coulisse: collection('coulisse', 'Coulisse', CATALOGUE.filter((p) => p.type === 'Coulisse'), '02',
    '<p>Une planche à deux plateaux coulissants.</p>'),
  'reformers-atelier': collection('reformers-atelier', 'Reformers Atelier', CATALOGUE.filter((p) => p.type === 'Reformers Atelier'), '03',
    '<p>De vrais reformers à chariot.</p>'),
  frontpage: collection('frontpage', 'Page d’accueil', ['coulisse-01', 'la-trousse', 'atelier-pliable'].map((h) => CATALOGUE.find((p) => p.handle === h)), '', ''),
};
CATALOGUE.forEach((p) => { p.collections = Object.values(COLLECTIONS).filter((c) => c.products.includes(p)); });
const PAGES = {
  'trouver-mon-equipement': { title: 'Trouver mon équipement', handle: 'trouver-mon-equipement', url: '/pages/trouver-mon-equipement' },
  'livraison-et-retours': { title: 'Livraison et retours', handle: 'livraison-et-retours', url: '/pages/livraison-et-retours' },
};

/* ---------- Panier simulé ---------- */
let lignes = []; // { variant, quantity }
function cartObjet() {
  const items = lignes.map((l, i) => ({
    key: `${l.variant.id}:${i}`, id: l.variant.id, quantity: l.quantity, variant: l.variant, product: l.variant.product,
    title: l.variant.product.title, url: l.variant.url, image: l.variant.product.featured_media ? l.variant.product.featured_media.preview_image : null,
    final_price: l.variant.price, final_line_price: l.variant.price * l.quantity, url_to_remove: `/cart/change?line=${i + 1}&quantity=0`,
    line_level_discount_allocations: [],
  }));
  return {
    items, item_count: items.reduce((a, b) => a + b.quantity, 0), total_price: items.reduce((a, b) => a + b.final_line_price, 0),
    cart_level_discount_applications: [],
  };
}
function ajouter(id, quantite) {
  const v = toutesVariantes().find((x) => x.id === Number(id));
  if (!v) return { status: 404, message: 'Introuvable', description: 'Cette variante n’existe pas.' };
  if (!v.available) return { status: 422, message: 'Épuisé', description: `${v.product.title} est épuisé.` };
  const l = lignes.find((x) => x.variant.id === v.id);
  const total = (l ? l.quantity : 0) + quantite;
  if (v.inventory_management && total > v.inventory_quantity) {
    return { status: 422, message: 'Stock', description: `Vous ne pouvez pas ajouter plus de ${v.inventory_quantity} × ${v.product.title} au panier.` };
  }
  if (l) l.quantity = total;
  else lignes.push({ variant: v, quantity: quantite });
  return null;
}
function changer(ligne, quantite) {
  const l = lignes[ligne - 1];
  if (!l) return { status: 400, message: 'Ligne', description: 'Ligne introuvable.' };
  if (quantite <= 0) {
    lignes.splice(ligne - 1, 1);
    return null;
  }
  const v = l.variant;
  if (v.inventory_management && quantite > v.inventory_quantity) {
    l.quantity = v.inventory_quantity;
    return { status: 422, message: 'Stock', description: `Il ne reste que ${v.inventory_quantity} × ${v.product.title}.` };
  }
  l.quantity = quantite;
  return null;
}

/* ---------- Réglages ---------- */
function defautsSchema(schema) {
  const out = {};
  for (const s of schema || []) if (s.id && 'default' in s) out[s.id] = s.default;
  return out;
}
const settingsSchema = lireJson('config/settings_schema.json');
const settings = {};
for (const g of settingsSchema) Object.assign(settings, defautsSchema(g.settings));
Object.assign(settings, {
  launch_mode: MODE,
  produit_principal: parHandle('coulisse-01'),
  produit_reservation: parHandle('reservation-prioritaire'),
  // Comme observé sur Shopify : une collection non publiée reste lisible en
  // Liquid (sans published_at), mais sa page renvoie une 404 aux visiteurs.
  collection_essentiels: ABSENTS ? { ...COLLECTIONS['les-essentiels'], published_at: null, products: [], products_count: 0 } : COLLECTIONS['les-essentiels'],
  collection_coulisse: ABSENTS ? { ...COLLECTIONS.coulisse, published_at: null, products: [], products_count: 0 } : COLLECTIONS.coulisse,
  collection_atelier: ABSENTS ? { ...COLLECTIONS['reformers-atelier'], published_at: null, products: [], products_count: 0 } : COLLECTIONS['reformers-atelier'],
  // Une page non publiée est vide en Liquid (observé sur l’aperçu Shopify).
  page_quiz: ABSENTS ? null : PAGES['trouver-mon-equipement'],
  page_livraison: ABSENTS ? null : PAGES['livraison-et-retours'],
  logo: image('shopify://shop_images/laplomb-logo.png'),
  favicon: image('shopify://shop_images/laplomb-monogramme.png'),
});

/* Résout les réglages typés (produit, collection, page, image…) d’un schéma. */
function resoudre(valeurs, schemaSettings) {
  const types = Object.fromEntries((schemaSettings || []).filter((s) => s.id).map((s) => [s.id, s.type]));
  const out = { ...valeurs };
  for (const [k, v] of Object.entries(out)) {
    const t = types[k];
    if (t === 'product') out[k] = typeof v === 'string' ? parHandle(v) : v || null;
    else if (t === 'product_list') out[k] = Array.isArray(v) ? v.map(parHandle).filter(Boolean) : [];
    else if (t === 'collection') out[k] = typeof v === 'string' ? (ABSENTS ? null : COLLECTIONS[v] || null) : v || null;
    else if (t === 'image_picker' || (typeof v === 'string' && v.startsWith('shopify://shop_images/'))) out[k] = image(v);
    else if (t === 'video') out[k] = v || null;
  }
  return out;
}
function image(ref) {
  if (typeof ref !== 'string' || !ref.startsWith('shopify://shop_images/')) return ref || null;
  const nom = ref.split('/').pop();
  if (fs.existsSync(path.join(ROOT, 'design', 'medias', nom))) return imageMedia(nom, ...(TAILLES[nom] || [1254, 1254]), '');
  if (!fs.existsSync(path.join(ROOT, 'design', 'images-ia', nom))) return null;
  const [w, h] = TAILLES[nom] || [1600, 1067];
  return imageIA(nom, w, h, '');
}

/* ---------- Moteur ---------- */
const engine = new Liquid({ root: [path.join(ROOT, 'snippets')], extname: '.liquid', jsTruthy: false });
function sauter(nomFin) {
  return {
    parse(token, reste) {
      for (;;) {
        const t = reste.shift();
        if (!t) throw new Error(`${nomFin} manquant`);
        if (t.name === nomFin) return;
      }
    },
    render() { return ''; },
  };
}
engine.registerTag('schema', sauter('endschema'));
engine.registerTag('doc', sauter('enddoc'));
engine.registerTag('stylesheet', sauter('endstylesheet'));

function blocTag(nom, rendu) {
  engine.registerTag(nom, {
    parse(token, reste) {
      this.args = token.args;
      this.tpls = [];
      const stream = this.liquid.parser.parseStream(reste);
      stream.on(`tag:end${nom}`, () => stream.stop()).on('template', (t) => this.tpls.push(t)).on('end', () => { throw new Error(`end${nom}`); });
      stream.start();
    },
    render: rendu,
  });
}

blocTag('form', function* rendre(ctx, emitter) {
  const args = this.args;
  const type = (args.match(/^\s*'([^']+)'/) || [])[1];
  let id = (args.match(/\bid:\s*'([^']+)'/) || [])[1];
  const idVar = (args.match(/\bid:\s*([a-z_]+)/) || [])[1];
  if (!id && idVar) id = yield ctx.get([idVar]);
  const cls = (args.match(/class:\s*'([^']+)'/) || [])[1];
  const attrs = [...args.matchAll(/([a-z]+-[a-z-]+|novalidate):\s*'([^']*)'/g)].map(([, k, v]) => ` ${k}="${v}"`).join('');
  const action = type === 'customer' ? '/contact' : '/cart/add';
  emitter.write(`<form method="post" action="${action}"${id ? ` id="${id}"` : ''}${cls ? ` class="${cls}"` : ''}${attrs} accept-charset="UTF-8"><input type="hidden" name="form_type" value="${type}">`);
  ctx.push({ form: { 'posted_successfully?': false, errors: null } });
  yield this.liquid.renderer.renderTemplates(this.tpls, ctx, emitter);
  ctx.pop();
  emitter.write('</form>');
});

blocTag('paginate', function* rendre(ctx, emitter) {
  ctx.push({ paginate: { pages: 1, current_page: 1 } });
  yield this.liquid.renderer.renderTemplates(this.tpls, ctx, emitter);
  ctx.pop();
});

engine.registerTag('sections', {
  parse(token) { this.groupe = token.args.replace(/['"\s]/g, ''); },
  * render(ctx, emitter) { emitter.write(yield rendreGroupe(this.groupe, ctx.getAll())); },
});
engine.registerTag('section', {
  parse(token) { this.nom = token.args.replace(/['"\s]/g, ''); },
  * render(ctx, emitter) { emitter.write(yield rendreSection(this.nom, { type: this.nom }, ctx.getAll())); },
});

/* ---------- Filtres ---------- */
const nommes = (args) => Object.fromEntries(args.filter((a) => Array.isArray(a)).map(([k, v]) => [k, v]));
engine.registerFilter('t', (cle, ...args) => {
  let v = cle.split('.').reduce((o, k) => (o ? o[k] : undefined), locale);
  const vars = nommes(args);
  if (v && typeof v === 'object' && 'other' in v) v = Number(vars.count) === 1 ? v.one : v.other;
  if (typeof v !== 'string') return `[${cle}]`;
  return v.replace(/\{\{\s*(\w+)\s*\}\}/g, (_, k) => (k in vars ? vars[k] : ''));
});
engine.registerFilter('asset_url', (nom) => `/assets/${nom}`);
engine.registerFilter('stylesheet_tag', (url) => `<link rel="stylesheet" href="${url}">`);
engine.registerFilter('preload_tag', (url, ...args) => {
  const a = nommes(args);
  return `<link rel="preload" href="${url}" as="${a.as || 'font'}" type="${a.type || ''}" crossorigin>`;
});
const argent = (c) => `${(Number(c || 0) / 100).toFixed(2).replace('.', ',')} €`;
engine.registerFilter('money', argent);
engine.registerFilter('money_without_trailing_zeros', argent);
engine.registerFilter('image_url', (img) => (img && img.src ? img.src : img && img.preview_image ? img.preview_image.src : ''));
engine.registerFilter('image_tag', (src, ...args) => {
  const a = nommes(args);
  const srcset = a.widths ? ` srcset="${String(a.widths).split(',').map((w) => `${src}?width=${w.trim()} ${w.trim()}w`).join(', ')}"` : '';
  return `<img src="${src}"${srcset}${a.class ? ` class="${a.class}"` : ''} alt="${String(a.alt || '').replace(/"/g, '&quot;')}" loading="${a.loading || 'lazy'}"${a.fetchpriority ? ` fetchpriority="${a.fetchpriority}"` : ''} sizes="${a.sizes || ''}" width="1600" height="1600">`;
});
engine.registerFilter('video_tag', () => '<video controls playsinline></video>');
engine.registerFilter('external_video_tag', () => '<iframe title="vidéo"></iframe>');
engine.registerFilter('media_tag', () => '');
engine.registerFilter('link_to', (txt, url) => `<a href="${url}">${txt}</a>`);
engine.registerFilter('structured_data', () => '{}');
engine.registerFilter('handleize', (s) => String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''));
engine.registerFilter('default_pagination', () => '');
engine.registerFilter('payment_terms', () => '');
// Comme Shopify : division entière quand le diviseur est un entier.
engine.registerFilter('divided_by', (a, b) => (Number.isInteger(Number(b)) ? Math.floor(Number(a) / Number(b)) : Number(a) / Number(b)));

/* ---------- Rendu ---------- */
function schemaDe(src) {
  const m = src.match(/\{%-?\s*schema\s*-?%\}([\s\S]*?)\{%-?\s*endschema\s*-?%\}/);
  return m ? JSON.parse(m[1]) : {};
}
function globaux() {
  return {
    settings,
    shop: { name: 'L’Aplomb', privacy_policy: { url: '/policies/privacy-policy' } },
    routes: { root_url: '/', cart_url: '/cart', all_products_collection_url: '/collections/all', search_url: '/search' },
    cart: cartObjet(), content_for_header: '', canonical_url: 'http://localhost/',
    images: Object.fromEntries(fs.readdirSync(path.join(ROOT, 'design', 'medias')).filter((n) => /\.(png|jpe?g)$/.test(n)).map((n) => [n, imageMedia(n, 1254, 1254, '')])),
  };
}

async function rendreSection(id, def, contexte) {
  const src = lire(`sections/${def.type}.liquid`);
  const schema = schemaDe(src);
  const reglages = resoudre({ ...defautsSchema(schema.settings), ...(def.settings || {}) }, schema.settings);
  const blocks = (def.block_order || Object.keys(def.blocks || {})).map((bid) => {
    const b = def.blocks[bid];
    const bs = (schema.blocks || []).find((x) => x.type === b.type) || {};
    const s = resoudre({ ...defautsSchema(bs.settings), ...(b.settings || {}) }, bs.settings);
    return { id: bid, type: b.type, settings: s, shopify_attributes: '' };
  });
  const section = { id, settings: reglages, blocks };
  const html = await engine.parseAndRender(src, { ...globaux(), ...contexte, section });
  const tag = schema.tag || 'div';
  return `<${tag} id="shopify-section-${id}" class="shopify-section${schema.class ? ` ${schema.class}` : ''}">${html}</${tag}>`;
}

async function rendreGroupe(groupe, contexte) {
  const def = lireJson(`sections/${groupe}.json`);
  const morceaux = [];
  for (const id of def.order) morceaux.push(await rendreSection(id, def.sections[id], contexte));
  return morceaux.join('\n');
}

async function page(gabarit, contexte) {
  const def = lireJson(`templates/${gabarit}.json`);
  const [nom, suffixe] = gabarit.split('.');
  const ctx = {
    ...contexte, template: { name: nom, suffix: suffixe || null },
    request: { locale: { iso_code: 'fr' }, design_mode: false, page_type: nom, origin: '' },
  };
  engine.options.globals = { ...globaux(), ...ctx };
  const corps = [];
  for (const id of def.order) corps.push(await rendreSection(`template--${nom}__${id}`, def.sections[id], ctx));
  return engine.parseAndRender(lire('layout/theme.liquid'), { ...globaux(), ...ctx, content_for_layout: corps.join('\n'), page_title: contexte.page_title });
}

async function sectionsDemandees(liste, chemin) {
  const out = {};
  engine.options.globals = { ...globaux(), template: { name: chemin.startsWith('/cart') ? 'cart' : 'index' } };
  for (const id of liste) {
    if (!id) continue;
    if (id === 'panier-tiroir') out[id] = await rendreSection(id, { type: 'panier-tiroir' }, {});
    else if (id.endsWith('__main') && chemin.startsWith('/cart')) out[id] = await rendreSection(id, { type: 'cart' }, {});
  }
  return out;
}

/* ---------- Serveur ---------- */
const TYPES = { '.css': 'text/css', '.js': 'text/javascript', '.woff2': 'font/woff2', '.svg': 'image/svg+xml', '.jpg': 'image/jpeg', '.png': 'image/png', '.html': 'text/html' };
function corpsJson(req) {
  return new Promise((ok) => {
    let d = '';
    req.on('data', (c) => { d += c; });
    req.on('end', () => {
      const type = req.headers['content-type'] || '';
      if (type.includes('json')) {
        try { ok(JSON.parse(d || '{}')); } catch (_) { ok({}); }
      } else ok(Object.fromEntries(new URLSearchParams(d)));
    });
  });
}
const envoyer = (res, statut, type, corps) => {
  res.writeHead(statut, { 'Content-Type': `${type}; charset=utf-8`, 'Cache-Control': 'no-store' });
  res.end(corps);
};

const serveur = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);
  const p = decodeURIComponent(url.pathname);
  try {
    if (req.method === 'POST' && p === '/cart/add.js') {
      const b = await corpsJson(req);
      const items = b.items || [{ id: b.id, quantity: Number(b.quantity || 1) }];
      for (const it of items) {
        const err = ajouter(it.id, Number(it.quantity || 1));
        if (err) return envoyer(res, err.status, 'application/json', JSON.stringify(err));
      }
      const sections = await sectionsDemandees(String(b.sections || '').split(','), b.sections_url || '/');
      return envoyer(res, 200, 'application/json', JSON.stringify({ items, sections }));
    }
    if (req.method === 'POST' && p === '/cart/change.js') {
      const b = await corpsJson(req);
      const err = changer(Number(b.line), Number(b.quantity));
      if (err) return envoyer(res, err.status, 'application/json', JSON.stringify(err));
      const sections = await sectionsDemandees(String(b.sections || '').split(','), b.sections_url || '/');
      return envoyer(res, 200, 'application/json', JSON.stringify({ ...cartObjet(), items: undefined, sections }));
    }
    if (req.method === 'POST' && p === '/cart/add') {
      const b = await corpsJson(req);
      ajouter(b.id, 1);
      res.writeHead(302, { Location: '/cart' });
      return res.end();
    }
    if (req.method === 'POST' && p === '/cart') {
      const b = await corpsJson(req);
      if ('checkout' in b) {
        res.writeHead(302, { Location: '/checkout' });
        return res.end();
      }
      res.writeHead(302, { Location: '/cart' });
      return res.end();
    }
    if (req.method === 'POST' && p === '/contact') {
      res.writeHead(302, { Location: `${req.headers.referer || '/'}` });
      return res.end();
    }
    if (req.method === 'GET' && url.searchParams.get('sections')) {
      const sections = await sectionsDemandees(url.searchParams.get('sections').split(','), p);
      return envoyer(res, 200, 'application/json', JSON.stringify(sections));
    }
    if (p === '/cart.js') return envoyer(res, 200, 'application/json', JSON.stringify(cartObjet()));
    if (p === '/__reinitialiser') {
      lignes = [];
      return envoyer(res, 200, 'text/plain', 'ok');
    }
    if (p === '/checkout') {
      const c = cartObjet();
      return envoyer(res, 200, 'text/html', `<!doctype html><html lang="fr"><title>Paiement (simulé)</title><body><h1>Paiement Shopify (simulé)</h1><p data-total="${c.total_price}">${c.item_count} article(s), ${argent(c.total_price)}</p></body></html>`);
    }
    if (p.startsWith('/assets/') || p.startsWith('/design/')) {
      const f = path.join(ROOT, p);
      if (!f.startsWith(ROOT) || !fs.existsSync(f)) return envoyer(res, 404, 'text/plain', 'introuvable');
      res.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream', 'Cache-Control': 'max-age=60' });
      return fs.createReadStream(f).pipe(res);
    }
    let html;
    if (p === '/') html = await page('index', { page_title: 'L’Aplomb' });
    else if (p.startsWith('/products/')) {
      const prod = parHandle(p.split('/')[2]);
      if (!prod) return envoyer(res, 404, 'text/html', '<h1>404</h1>');
      const vid = Number(url.searchParams.get('variant'));
      const v = prod.variants.find((x) => x.id === vid);
      const produitCtx = v ? { ...prod, selected_or_first_available_variant: v, options_with_values: prod.options_with_values.map((o) => ({ ...o, selected_value: v.title })) } : prod;
      html = await page(prod.template_suffix ? `product.${prod.template_suffix}` : 'product', { product: produitCtx, page_title: prod.title });
    } else if (p.startsWith('/collections/')) {
      const h = p.split('/')[2];
      const c = h === 'all' ? collection('all', 'Tous les produits', CATALOGUE.filter((x) => x.type !== 'Service'), '', '') : COLLECTIONS[h];
      if (!c || ABSENTS) return envoyer(res, 404, 'text/html', '<h1>404</h1>');
      html = await page('collection', { collection: c, page_title: c.title });
    } else if (p === '/pages/trouver-mon-equipement') {
      html = await page('page.pilates-quiz', { page: PAGES['trouver-mon-equipement'], page_title: 'Trouver mon équipement' });
    } else if (p === '/cart') {
      html = await page('cart', { page_title: 'Panier' });
    } else return envoyer(res, 404, 'text/html', '<h1>404</h1>');
    return envoyer(res, 200, 'text/html', html);
  } catch (e) {
    console.error(e);
    return envoyer(res, 500, 'text/plain', String(e.stack || e));
  }
});

serveur.listen(PORT, () => console.log(`aperçu : http://127.0.0.1:${PORT} (mode ${MODE}${ABSENTS ? ', produits absents' : ''})`));
