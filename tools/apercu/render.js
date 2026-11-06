/**
 * Rendu local du thème L'Aplomb, pour contrôle visuel seulement.
 * LiquidJS + objets Shopify simulés (produit, réglages, traductions).
 * Ce n'est pas le moteur de Shopify : les captures définitives se font sur
 * l'aperçu du thème non publié.
 *
 * Usage : node tools/apercu/render.js [mode] [police]
 *   mode   : waitlist (défaut) | reservation | vente
 *   police : cormorant (défaut) | bodoni
 * Sortie : design/apercu/index.html et design/apercu/produit.html
 */
const fs = require('fs');
const path = require('path');
const { Liquid } = require('liquidjs');

const ROOT = path.resolve(__dirname, '..', '..');
const OUT = path.join(ROOT, 'design', 'apercu');
const [mode = 'waitlist', police = 'cormorant'] = process.argv.slice(2);

const lire = (p) => fs.readFileSync(path.join(ROOT, p), 'utf8');
const lireJson = (p) => JSON.parse(lire(p).replace(/^\s*\/\*[\s\S]*?\*\/\s*/, ''));
const locale = lireJson('locales/fr.default.json');

/* ---------- Objets simulés ---------- */
const IMAGES_IA = path.join(ROOT, 'design', 'images-ia');
function image(ref) {
  if (typeof ref !== 'string' || !ref.startsWith('shopify://shop_images/')) return ref;
  const nom = ref.split('/').pop();
  const fichier = path.join(IMAGES_IA, nom);
  if (!fs.existsSync(fichier)) return null;
  const tailles = { 'plan-09-soiree.jpg': [1536, 1024], 'plan-07-coffret.jpg': [1536, 1024], 'plan-06-posture-provisoire.jpg': [1024, 1280] };
  const [w, h] = tailles[nom] || [1600, 1067];
  return { src: `/design/images-ia/${nom}`, width: w, height: h, alt: '', aspect_ratio: w / h };
}

const variante = (id, title, price) => ({ id, title, price, available: true, url: `/products/mini-reformer?variant=${id}` });
const variantes = [variante(4401, 'Essentiel', 17900), variante(4402, 'Studio', 22900)];
const produit = {
  id: 44, title: 'Le mini-reformer L’Aplomb', handle: 'mini-reformer', url: '/products/mini-reformer',
  variants: variantes, selected_or_first_available_variant: variantes[0], has_only_default_variant: false,
  price: 17900, available: true, metafields: { aplomb: {}, gpsr: {} },
};
const reservation = {
  id: 45, title: 'Réservation prioritaire', url: '/products/reservation-prioritaire', price: 1900, available: true,
  selected_or_first_available_variant: variante(4501, 'Default Title', 1900),
};

function defautsSchema(schema) {
  const out = {};
  for (const s of schema || []) if (s.id && 'default' in s) out[s.id] = s.default;
  return out;
}
const settingsSchema = lireJson('config/settings_schema.json');
const settings = {};
for (const groupe of settingsSchema) Object.assign(settings, defautsSchema(groupe.settings));
Object.assign(settings, { launch_mode: mode, police_titres: police, produit_principal: produit, produit_reservation: reservation });

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

engine.registerTag('style', {
  parse(token, reste) {
    this.tpls = [];
    const stream = this.liquid.parser.parseStream(reste);
    stream.on('tag:endstyle', () => stream.stop()).on('template', (t) => this.tpls.push(t)).on('end', () => { throw new Error('endstyle'); });
    stream.start();
  },
  * render(ctx, emitter) { emitter.write('<style>'); yield this.liquid.renderer.renderTemplates(this.tpls, ctx, emitter); emitter.write('</style>'); },
});

engine.registerTag('form', {
  parse(token, reste) {
    this.args = token.args;
    this.tpls = [];
    const stream = this.liquid.parser.parseStream(reste);
    stream.on('tag:endform', () => stream.stop()).on('template', (t) => this.tpls.push(t)).on('end', () => { throw new Error('endform'); });
    stream.start();
  },
  * render(ctx, emitter) {
    const type = (this.args.match(/^\s*'([^']+)'/) || [])[1];
    const id = (this.args.match(/id:\s*'([^']+)'/) || [])[1];
    let idVar = (this.args.match(/id:\s*([a-z_]+)/) || [])[1];
    const cls = (this.args.match(/class:\s*'([^']+)'/) || [])[1];
    let idFinal = id;
    if (!idFinal && idVar) idFinal = yield ctx.get([idVar]);
    const action = type === 'customer' ? '/contact#' + (idFinal || '') : '/cart/add';
    emitter.write(`<form method="post" action="${action}"${idFinal ? ` id="${idFinal}"` : ''}${cls ? ` class="${cls}"` : ''} accept-charset="UTF-8"><input type="hidden" name="form_type" value="${type}">`);
    ctx.push({ form: { 'posted_successfully?': false, errors: null } });
    yield this.liquid.renderer.renderTemplates(this.tpls, ctx, emitter);
    ctx.pop();
    emitter.write('</form>');
  },
});

engine.registerTag('sections', {
  parse(token) { this.groupe = token.args.replace(/['"\s]/g, ''); },
  * render(ctx, emitter) { emitter.write(yield rendreGroupe(this.groupe, ctx.getAll ? ctx.getAll() : {})); },
});

/* ---------- Filtres ---------- */
const nommes = (args) => Object.fromEntries(args.filter((a) => Array.isArray(a)).map(([k, v]) => [k, v]));
const argent = (cents, decimales) => {
  const n = Number(cents || 0) / 100;
  const txt = decimales || n % 1 ? n.toFixed(2).replace('.', ',') : String(n);
  return `${txt} €`;
};
engine.registerFilter('t', (cle, ...args) => {
  let v = cle.split('.').reduce((o, k) => (o ? o[k] : undefined), locale);
  if (typeof v !== 'string') return `[${cle}]`;
  const vars = nommes(args);
  return v.replace(/\{\{\s*(\w+)\s*\}\}/g, (_, k) => (k in vars ? vars[k] : ''));
});
engine.registerFilter('asset_url', (nom) => `/assets/${nom}`);
engine.registerFilter('stylesheet_tag', (url) => `<link rel="stylesheet" href="${url}">`);
engine.registerFilter('preload_tag', (url, ...args) => {
  const a = nommes(args);
  return `<link rel="preload" href="${url}" as="${a.as || 'font'}" type="${a.type || ''}" crossorigin>`;
});
engine.registerFilter('money', (c) => argent(c, true));
engine.registerFilter('money_without_trailing_zeros', (c) => argent(c, false));
engine.registerFilter('money_without_currency', (c) => (Number(c || 0) / 100).toFixed(2));
engine.registerFilter('image_url', (img) => (img && img.src ? img.src : ''));
engine.registerFilter('image_tag', function (src, ...args) {
  const a = nommes(args);
  return `<img src="${src}" alt="${a.alt || ''}" loading="${a.loading || 'lazy'}"${a.fetchpriority ? ` fetchpriority="${a.fetchpriority}"` : ''} sizes="${a.sizes || ''}" width="1600" height="1067">`;
});
engine.registerFilter('video_tag', () => '<video controls playsinline></video>');
engine.registerFilter('link_to', (txt, url) => `<a href="${url}">${txt}</a>`);
engine.registerFilter('structured_data', () => '{}');
engine.registerFilter('inline_asset_content', () => '');
engine.registerFilter('payment_type_svg_tag', () => '');
engine.registerFilter('default_pagination', () => '');

/* ---------- Sections ---------- */
function schemaDe(src) {
  const m = src.match(/\{%-?\s*schema\s*-?%\}([\s\S]*?)\{%-?\s*endschema\s*-?%\}/);
  return m ? JSON.parse(m[1]) : {};
}
const globaux = {
  settings, shop: { name: 'L’Aplomb', privacy_policy: { url: '/policies/privacy-policy' } },
  routes: { root_url: '/', cart_url: '/cart', all_products_collection_url: '/collections/all', search_url: '/search' },
  cart: { item_count: 0 }, content_for_header: '', canonical_url: 'https://exemple.test/',
};

async function rendreSection(id, def, contexte) {
  const src = lire(`sections/${def.type}.liquid`);
  const schema = schemaDe(src);
  const reglages = { ...defautsSchema(schema.settings), ...(def.settings || {}) };
  for (const [k, v] of Object.entries(reglages)) reglages[k] = image(v);
  const blocks = (def.block_order || Object.keys(def.blocks || {})).map((bid) => {
    const b = def.blocks[bid];
    const bs = (schema.blocks || []).find((x) => x.type === b.type) || {};
    const s = { ...defautsSchema(bs.settings), ...(b.settings || {}) };
    for (const [k, v] of Object.entries(s)) s[k] = image(v);
    return { id: bid, type: b.type, settings: s, shopify_attributes: '' };
  });
  const section = { id, settings: reglages, blocks };
  const html = await engine.parseAndRender(src, { ...globaux, ...contexte, section });
  const tag = schema.tag || 'div';
  return `<${tag} id="shopify-section-${id}" class="shopify-section">${html}</${tag}>`;
}

async function rendreGroupe(groupe, contexte) {
  const def = lireJson(`sections/${groupe}.json`);
  const morceaux = [];
  for (const id of def.order) morceaux.push(await rendreSection(id, def.sections[id], contexte));
  return morceaux.join('\n');
}

async function page(gabarit, fichier, contexte) {
  const def = lireJson(`templates/${gabarit}.json`);
  const ctx = { ...contexte, template: { name: gabarit }, request: { locale: { iso_code: 'fr' }, design_mode: false, page_type: gabarit, origin: '' } };
  // Comme sur Shopify : les objets globaux restent visibles dans les snippets ({% render %}).
  engine.options.globals = { ...globaux, ...ctx };
  const corps = [];
  for (const id of def.order) corps.push(await rendreSection(id, def.sections[id], ctx));
  const layout = lire('layout/theme.liquid').replace('{% sections \'header-group\' %}', await rendreGroupe('header-group', ctx))
    .replace('{% sections \'footer-group\' %}', await rendreGroupe('footer-group', ctx));
  const html = await engine.parseAndRender(layout, { ...globaux, ...ctx, content_for_layout: corps.join('\n'), page_title: contexte.page_title });
  fs.mkdirSync(OUT, { recursive: true });
  fs.writeFileSync(path.join(OUT, fichier), html);
  console.log(`design/apercu/${fichier}`, html.length);
}

(async () => {
  await page('index', 'index.html', { page_title: 'L’Aplomb' });
  await page('product', 'produit.html', { product: produit, page_title: produit.title });
})().catch((e) => { console.error(e); process.exit(1); });
