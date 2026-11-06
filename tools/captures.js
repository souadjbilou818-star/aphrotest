// Captures Playwright : node tools/captures.js <url> <dossier> [dsf] [prefixe]
// Variables : SLICES="390:7000,1440:5400" (hauteur des tranches), FORMAT=jpg
// - écran d'accueil à 390 et 1440 px
// - page entière découpée en tranches (lisibles)
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const [url, out, dsfArg, prefix = 'page'] = process.argv.slice(2);
  const dsf = Number(dsfArg || 1);
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const fmt = process.env.FORMAT === 'jpg' ? 'jpg' : 'png';
  const shot = (o) => (fmt === 'jpg' ? { ...o, type: 'jpeg', quality: 82 } : o);
  const custom = Object.fromEntries((process.env.SLICES || '').split(',').filter(Boolean).map((x) => x.split(':').map(Number)));
  const sizes = [
    { name: '390', width: 390, height: 844, slice: custom[390] || 1700 },
    { name: '1440', width: 1440, height: 900, slice: custom[1440] || 1500 },
  ];
  for (const s of sizes) {
    const ctx = await browser.newContext({ viewport: { width: s.width, height: s.height }, deviceScaleFactor: dsf });
    const page = await ctx.newPage();
    const errors = [];
    page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
    page.on('pageerror', (e) => errors.push(String(e)));
    await page.goto(url, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    // les fondus d'entrée dépendent du défilement : on capture l'état final
    await page.addStyleTag({ content: '.cadre__zone--image img,.acte__filet .filet{animation:none!important}' });
    await page.screenshot({ path: path.join(out, `${prefix}-${s.name}-ecran.png`) });
    // défilement complet : déclenche les images en chargement différé, puis retour en haut
    await page.evaluate(async () => {
      for (let y = 0; y < document.documentElement.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise((r) => setTimeout(r, 60)); }
      await Promise.all([...document.images].map((i) => (i.complete ? null : new Promise((r) => { i.onload = i.onerror = r; }))));
      window.scrollTo(0, 0);
    });
    await page.waitForTimeout(300);
    const h = await page.evaluate(() => document.documentElement.scrollHeight);
    const sw = await page.evaluate(() => document.documentElement.scrollWidth);
    let i = 0;
    for (let y = 0; y < h; y += s.slice) {
      i += 1;
      await page.screenshot(shot({ path: path.join(out, `${prefix}-${s.name}-page-${i}.${fmt}`), fullPage: true,
        clip: { x: 0, y, width: s.width, height: Math.min(s.slice, h - y) } }));
    }
    const fonts = await page.evaluate(() => [...document.fonts].filter((f) => f.status === 'loaded').map((f) => f.family + ' ' + f.style));
    console.log(JSON.stringify({ size: s.name, height: h, scrollWidth: sw, slices: i, errors, fonts: [...new Set(fonts)] }));
    await ctx.close();
  }
  await browser.close();
})();
