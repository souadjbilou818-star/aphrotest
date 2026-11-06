/**
 * Tests de parcours (Phase C) sur le serveur d’aperçu local.
 *   MODE=vente PORT=8765 node tools/apercu/serveur.js &
 *   MODE=waitlist PRODUITS=absents PORT=8766 node tools/apercu/serveur.js &
 *   node tools/tests/parcours.js
 * Écrit docs/qa/resultats.json et les captures dans design/captures/storefront/.
 */
const fs = require('fs');
const path = require('path');
const { chromium, devices } = require('playwright');

const ROOT = path.resolve(__dirname, '..', '..');
const VENTE = 'http://127.0.0.1:8765';
const ATTENTE = 'http://127.0.0.1:8766';
const CAPTURES = path.join(ROOT, 'design', 'captures', 'storefront');
fs.mkdirSync(CAPTURES, { recursive: true });
fs.mkdirSync(path.join(ROOT, 'docs', 'qa'), { recursive: true });

const resultats = [];
async function test(nom, fn) {
  if (process.env.TEST && !nom.includes(process.env.TEST)) return;
  const t0 = Date.now();
  try {
    await fn();
    resultats.push({ test: nom, statut: 'ok', ms: Date.now() - t0 });
    console.log(`ok   ${nom}`);
  } catch (e) {
    resultats.push({ test: nom, statut: 'échec', erreur: String(e.message || e).split('\n')[0], ms: Date.now() - t0 });
    console.log(`ÉCHEC ${nom}\n     ${String(e.message || e).split('\n').slice(0, 6).join('\n     ')}`);
  }
}
function ok(cond, msg) {
  if (!cond) throw new Error(msg);
}
async function page(navigateur, opts = {}) {
  const ctx = await navigateur.newContext({ viewport: { width: 390, height: 844 }, ...opts });
  const p = await ctx.newPage();
  p.erreurs = [];
  p.on('console', (m) => { if (m.type() === 'error') p.erreurs.push(m.text()); });
  p.on('pageerror', (e) => p.erreurs.push(String(e)));
  return p;
}
const evenements = (p) => p.evaluate(() => (window.dataLayer || []).map((e) => e.event));
const reinitialiser = (p, base = VENTE) => p.request.get(`${base}/__reinitialiser`);

(async () => {
  const nav = await chromium.launch();

  /* ---------- Quiz ---------- */
  await test('Quiz : validation, toucher, clavier, retour, résultat COULISSE, mesure', async () => {
    const p = await page(nav);
    await p.goto(`${VENTE}/#quiz`);
    const q = p.locator('aplomb-quiz');
    await q.locator('[data-quiz-suivant]:visible').click();
    ok(await q.locator('[data-quiz-erreur]:visible').count() === 1, 'pas de message d’erreur sans réponse');
    ok(await p.evaluate(() => document.activeElement && document.activeElement.type === 'radio'), 'le focus ne va pas sur la première réponse');
    await q.locator('.quiz__option:visible', { hasText: 'Renforcement' }).click();
    await p.waitForSelector('[data-quiz-etape="2"]:not([hidden])');
    ok((await q.locator('[data-quiz-compte]').textContent()).includes('2 sur 4'), 'compteur incorrect');
    // Clavier : flèches = pas d’avance automatique
    await q.locator('[data-quiz-etape="2"] input').first().focus();
    await p.keyboard.press('ArrowDown');
    await p.waitForTimeout(400);
    ok(await q.locator('[data-quiz-etape="2"]:not([hidden])').count() === 1, 'avance automatique au clavier');
    await q.locator('[data-quiz-etape="2"] [data-quiz-suivant]').focus();
    await p.keyboard.press('Enter');
    await p.waitForSelector('[data-quiz-etape="3"]:not([hidden])');
    await q.locator('[data-quiz-retour]').click();
    await p.waitForSelector('[data-quiz-etape="2"]:not([hidden])');
    ok(await q.locator('[data-quiz-etape="2"] input:checked').count() === 1, 'réponse perdue au retour');
    await q.locator('[data-quiz-etape="2"] [data-quiz-suivant]').click();
    await q.locator('.quiz__option:visible', { hasText: 'compact' }).click();
    await p.waitForSelector('[data-quiz-etape="4"]:not([hidden])');
    await q.locator('.quiz__option:visible', { hasText: 'polyvalente' }).click();
    await p.waitForSelector('[data-quiz-resultat="coulisse"]:not([hidden])');
    ok(await q.locator('[data-quiz-arguments] li').count() >= 2, 'arguments absents');
    ok(await q.locator('[data-quiz-recap] div').count() === 4, 'récapitulatif incomplet');
    const ev = await evenements(p);
    for (const e of ['aplomb_quiz_started', 'aplomb_quiz_step_completed', 'aplomb_quiz_completed', 'aplomb_recommendation_displayed']) ok(ev.includes(e), `événement manquant : ${e}`);
    const etapes = await p.evaluate(() => [...new Set(window.dataLayer.filter((e) => e.event === 'aplomb_quiz_step_completed').map((e) => e.etape))].sort());
    ok(JSON.stringify(etapes) === '[1,2,3,4]', `étapes mesurées : ${etapes}`);
    ok(ev.filter((e) => e === 'aplomb_quiz_completed').length === 1, 'quiz_completed doit être unique');
    await p.screenshot({ path: path.join(CAPTURES, 'quiz-resultat-390.png'), fullPage: false });
    // Rechargement : le résultat est conservé pour la session
    await p.reload();
    await p.waitForSelector('[data-quiz-resultat="coulisse"]:not([hidden])');
    await q.locator('[data-quiz-recommencer]').click();
    await p.waitForSelector('[data-quiz-etape="1"]:not([hidden])');
    ok(await q.locator('input:checked').count() === 0, 'réponses non effacées');
    ok(p.erreurs.length === 0, `erreurs console : ${p.erreurs.join(' | ')}`);
    await p.context().close();
  });

  await test('Quiz : « petit espace » écarte les Reformers Atelier et le dit', async () => {
    const p = await page(nav);
    await p.goto(`${VENTE}/#quiz`);
    const q = p.locator('aplomb-quiz');
    for (const t of ['Renforcement', 'régulièrement', 'studio', 'petit espace']) {
      await q.locator('.quiz__option:visible', { hasText: t }).click();
      await p.waitForTimeout(350);
    }
    await p.waitForSelector('[data-quiz-resultat="coulisse"]:not([hidden])');
    ok(await q.locator('[data-quiz-resultat="coulisse"] [data-quiz-ecarte]:visible').count() === 1, 'la famille écartée n’est pas expliquée');
    await p.context().close();
  });

  await test('Quiz : kit simple → Les Essentiels', async () => {
    const p = await page(nav);
    await p.goto(`${VENTE}/#quiz`);
    const q = p.locator('aplomb-quiz');
    for (const t of ['Mobilité', 'débute', 'kit simple', 'petit espace']) {
      await q.locator('.quiz__option:visible', { hasText: t }).click();
      await p.waitForTimeout(350);
    }
    await p.waitForSelector('[data-quiz-resultat="essentiels"]:not([hidden])');
    await p.context().close();
  });

  await test('Quiz en page dédiée : le bouton Retour du navigateur revient d’une question', async () => {
    const p = await page(nav);
    await p.goto(`${VENTE}/pages/trouver-mon-equipement`);
    const q = p.locator('aplomb-quiz');
    await q.locator('.quiz__option:visible', { hasText: 'Renforcement' }).click();
    await p.waitForSelector('[data-quiz-etape="2"]:not([hidden])');
    await q.locator('.quiz__option:visible', { hasText: 'déjà' }).click();
    await p.waitForSelector('[data-quiz-etape="3"]:not([hidden])');
    await p.goBack();
    await p.waitForSelector('[data-quiz-etape="2"]:not([hidden])');
    ok(p.url().includes('/pages/trouver-mon-equipement'), 'le retour a quitté la page');
    ok(await p.locator('h1').count() === 1, 'la page quiz doit avoir un seul h1');
    await p.context().close();
  });

  await test('Quiz → ajout au panier depuis la recommandation, tiroir ouvert', async () => {
    const p = await page(nav);
    await reinitialiser(p);
    await p.goto(`${VENTE}/#quiz`);
    const q = p.locator('aplomb-quiz');
    for (const t of ['routine', 'déjà', 'compact', 'polyvalente']) {
      await q.locator('.quiz__option:visible', { hasText: t }).click();
      await p.waitForTimeout(350);
    }
    await q.locator('[data-quiz-resultat="coulisse"] button[name="add"]').click();
    await p.waitForSelector('dialog[data-tiroir][open]');
    ok((await p.locator('[data-panier-compte]').first().textContent()).trim() === '1', 'compteur du panier ≠ 1');
    ok(await p.locator('dialog[data-tiroir] .panier-ligne').count() === 1, 'ligne absente du tiroir');
    ok((await evenements(p)).includes('aplomb_recommendation_cta'), 'clic de recommandation non mesuré');
    await p.context().close();
  });

  /* ---------- Fiche produit ---------- */
  await test('Produit : variante Studio, prix, URL, compléments, panier', async () => {
    const p = await page(nav);
    await reinitialiser(p);
    await p.goto(`${VENTE}/products/coulisse-01`);
    await p.locator('.option', { hasText: 'Studio' }).click();
    ok((await p.locator('.produit__prix [data-prix]').textContent()).includes('189'), 'prix non mis à jour');
    ok(p.url().includes('variant='), 'URL non mise à jour');
    ok((await p.locator('[data-cta-principal] [data-cta-vente]').textContent()).includes('189'), 'libellé du bouton non mis à jour');
    ok(await p.locator('[data-complement]').count() === 1, 'le complément épuisé ne doit pas être proposé');
    await p.locator('.complement').click();
    await p.locator('[data-cta-principal] [data-cta-vente]').click();
    await p.waitForSelector('dialog[data-tiroir][open]');
    ok(await p.locator('dialog[data-tiroir] .panier-ligne').count() === 2, 'produit + complément attendus');
    ok((await p.locator('[data-panier-total]').textContent()).includes('207'), `total attendu 207 € : ${await p.locator('[data-panier-total]').textContent()}`);
    await p.screenshot({ path: path.join(CAPTURES, 'panier-tiroir-390.png') });
    await p.context().close();
  });

  await test('Panier : quantités, limite de stock (erreur lisible), retrait, paiement natif', async () => {
    const p = await page(nav);
    await reinitialiser(p);
    await p.goto(`${VENTE}/products/coulisse-01`);
    await p.locator('.option', { hasText: 'Studio' }).click();
    await p.locator('[data-cta-principal] [data-cta-vente]').click();
    await p.waitForSelector('dialog[data-tiroir][open]');
    const ligne = p.locator('dialog[data-tiroir] .panier-ligne').first();
    await ligne.locator('[data-qte="1"]').click();
    await p.waitForFunction(() => document.querySelector('dialog[data-tiroir] [data-qte-champ]').value === '2');
    const champ = p.locator('dialog[data-tiroir] [data-qte-champ]').first();
    await champ.fill('5');
    await champ.press('Enter');
    await p.waitForSelector('dialog[data-tiroir] [data-panier-erreur]:not([hidden])');
    ok((await p.locator('dialog[data-tiroir] [data-panier-erreur]').textContent()).length > 5, 'message d’erreur vide');
    await p.locator('dialog[data-tiroir] [data-retirer]').first().click();
    await p.waitForSelector('dialog[data-tiroir] .tiroir__vide');
    ok((await p.locator('[data-panier-compte]').first().textContent()).trim() === '0', 'compteur ≠ 0 après retrait');
    // Paiement : nouvel ajout puis formulaire natif /cart (name=checkout)
    await p.keyboard.press('Escape');
    await p.locator('[data-cta-principal] [data-cta-vente]').click();
    await p.waitForSelector('dialog[data-tiroir][open] [data-panier-paiement]');
    await Promise.all([p.waitForURL('**/checkout'), p.locator('[data-panier-paiement]').click()]);
    ok((await p.locator('h1').textContent()).includes('Paiement'), 'pas arrivé au paiement');
    await p.context().close();
  });

  await test('Page panier : quantité sans rechargement, paiement', async () => {
    const p = await page(nav);
    await reinitialiser(p);
    await p.request.post(`${VENTE}/cart/add.js`, { data: { items: [{ id: 7001, quantity: 1 }] } });
    await p.goto(`${VENTE}/cart`);
    await p.locator('[data-panier-page] [data-qte="1"]').click();
    await p.waitForFunction(() => document.querySelector('[data-panier-page] [data-qte-champ]').value === '2');
    ok(await p.locator('[data-sans-js]:visible').count() === 0, 'bouton « Mettre à jour » visible avec JS');
    await Promise.all([p.waitForURL('**/checkout'), p.locator('[data-panier-page] button[name="checkout"]').click()]);
    await p.context().close();
  });

  await test('Barre collante mobile : apparaît après le bloc d’achat et ajoute au panier', async () => {
    const p = await page(nav);
    await reinitialiser(p);
    await p.goto(`${VENTE}/products/coulisse-01`);
    ok(!(await p.locator('aplomb-collant').evaluate((e) => e.classList.contains('is-visible'))), 'visible trop tôt');
    await p.evaluate(() => window.scrollTo(0, document.querySelector('[data-cta-principal]').getBoundingClientRect().bottom + window.scrollY + 600));
    await p.waitForSelector('aplomb-collant.is-visible');
    await p.locator('aplomb-collant [data-collant-bouton]').click();
    await p.waitForSelector('dialog[data-tiroir][open]');
    await p.context().close();
  });

  await test('Galerie : flèches, compteur, visionneuse (zoom, Échap, retour du focus)', async () => {
    const p = await page(nav);
    await p.goto(`${VENTE}/products/la-trousse`);
    await p.locator('[data-suivant]').click();
    await p.waitForFunction(() => document.querySelector('[data-compteur]').textContent.startsWith('2'));
    await p.locator('[data-zoom="0"]').click();
    await p.waitForSelector('dialog[data-visionneuse][open]');
    await p.locator('[data-v-zoom]').click();
    ok((await p.locator('[data-v-zoom]').getAttribute('aria-pressed')) === 'true', 'zoom inactif');
    await p.keyboard.press('ArrowRight');
    ok((await p.locator('[data-v-compteur]').textContent()).startsWith('2'), 'flèche clavier inactive');
    await p.keyboard.press('Escape');
    await p.waitForFunction(() => !document.querySelector('dialog[data-visionneuse]').open);
    ok(await p.evaluate(() => document.activeElement.matches('[data-zoom]')), 'focus non rendu');
    ok(await p.locator('.galerie-produit .credit').count() === 3, 'mention « Image générée » manquante');
    await p.context().close();
  });

  await test('Produit en liste d’attente en mode Vente (Atelier) : aucun bouton d’achat', async () => {
    const p = await page(nav);
    await p.goto(`${VENTE}/products/atelier-chene`);
    ok(await p.locator('[data-cta-principal] form[action="/contact"]').count() === 1, 'formulaire de liste d’attente absent');
    ok(await p.locator('[data-cta-principal] [data-cta-vente]').count() === 0, 'bouton d’achat présent');
    ok((await p.locator('[data-cta-principal] input[name="contact[tags]"]').getAttribute('value')).includes('atelier-chene'), 'tag produit absent');
    await p.context().close();
  });

  await test('Collection : prix réels, épuisé signalé, navigation des familles', async () => {
    const p = await page(nav);
    await p.goto(`${VENTE}/collections/all`);
    ok(await p.locator('.carte-produit__etat', { hasText: 'Épuisé' }).count() === 1, 'état épuisé absent');
    await p.goto(`${VENTE}/collections/coulisse`);
    ok(await p.locator('.lien-famille--onglets a[aria-current="page"]').count() === 1, 'famille courante non signalée');
    await p.context().close();
  });

  /* ---------- Mode liste d’attente, produits en brouillon ---------- */
  await test('Liste d’attente, produits absents : replis honnêtes, aucun bouton d’achat', async () => {
    const p = await page(nav);
    await p.goto(`${ATTENTE}/`);
    ok(await p.locator('[data-cta-vente]').count() === 0, 'bouton d’achat présent');
    ok((await p.locator('.hero__ctas a').first().getAttribute('href')) === '#coulisse', 'repli du bouton produit');
    ok(await p.locator('#liste-vedette').count() === 1, 'liste d’attente du produit vedette absente');
    ok(await p.locator('#liste-cloture').count() === 1, 'liste d’attente de clôture absente');
    ok(await p.locator('dialog[data-tiroir]').count() === 0, 'tiroir rendu en liste d’attente');
    ok(await p.locator('.famille__prix--attente').count() === 3, 'familles sans prix attendues');
    ok(await p.locator('.lien-famille').count() === 0, 'lien vers une collection non publiée (404)');
    ok(await p.locator('.famille__lien').count() === 0, 'carte de famille liée à une collection non publiée');
    ok(await p.locator('details.menu-mobile').count() === 0, 'menu mobile vide affiché');
    const q = p.locator('aplomb-quiz');
    for (const t of ['routine', 'déjà', 'compact', 'polyvalente']) {
      await q.locator('.quiz__option:visible', { hasText: t }).click();
      await p.waitForTimeout(350);
    }
    await p.waitForSelector('[data-quiz-resultat="coulisse"]:not([hidden])');
    ok(await p.locator('[data-quiz-resultat="coulisse"] form[action="/contact"]').count() === 1, 'liste d’attente absente du résultat');
    ok((await p.locator('[data-quiz-resultat="coulisse"] input[name="contact[tags]"]').getAttribute('value')).includes('quiz,coulisse'), 'tags du quiz');
    ok(p.erreurs.length === 0, `erreurs console : ${p.erreurs.join(' | ')}`);
    ok(!(await p.content()).includes('Expédié depuis la France'), '« Expédié depuis la France » hors mode vente');
    await p.context().close();
  });

  /* ---------- Réactivité, erreurs console, captures ---------- */
  const PAGES = [
    ['accueil', '/'], ['produit', '/products/coulisse-01'], ['trousse', '/products/la-trousse'],
    ['quiz', '/pages/trouver-mon-equipement'], ['collection', '/collections/coulisse'], ['panier', '/cart'],
  ];
  const LARGEURS = [320, 375, 390, 768, 1024, 1440];
  for (const w of LARGEURS) {
    await test(`Largeur ${w} px : aucun débordement horizontal, aucune erreur console`, async () => {
      const p = await page(nav, { viewport: { width: w, height: w < 700 ? 844 : 900 } });
      const fautes = [];
      for (const [nom, url] of PAGES) {
        await p.goto(`${VENTE}${url}`, { waitUntil: 'networkidle' });
        const sw = await p.evaluate(() => document.documentElement.scrollWidth);
        if (sw > w) fautes.push(`${nom} : ${sw}px`);
        if ([390, 1440].includes(w)) {
          await p.addStyleTag({ content: '.collant{display:none!important}' });
          await p.evaluate(() => document.querySelectorAll('img[loading=lazy]').forEach((i) => { i.loading = 'eager'; }));
          await p.waitForTimeout(300);
          await p.screenshot({ path: path.join(CAPTURES, `${nom}-${w}.png`), fullPage: true });
        }
      }
      ok(fautes.length === 0, `débordement : ${fautes.join(', ')}`);
      ok(p.erreurs.length === 0, `erreurs console : ${p.erreurs.join(' | ')}`);
      await p.context().close();
    });
  }

  await nav.close();
  const bilan = { date: new Date().toISOString(), total: resultats.length, ok: resultats.filter((r) => r.statut === 'ok').length, resultats };
  fs.writeFileSync(path.join(ROOT, 'docs', 'qa', 'resultats.json'), `${JSON.stringify(bilan, null, 2)}\n`);
  console.log(`\n${bilan.ok}/${bilan.total} tests réussis`);
  process.exit(bilan.ok === bilan.total ? 0 : 1);
})();
