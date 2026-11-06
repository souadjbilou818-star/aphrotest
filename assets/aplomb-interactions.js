/**
 * L’Aplomb — interactions communes (vanilla, aucune dépendance).
 *
 * window.aplomb.suivre(nom, donnees) : événements de mesure (voir docs/analytics.md)
 * <aplomb-variantes> : choix des options, met à jour prix, disponibilité, formulaires, URL
 * <aplomb-galerie>   : galerie produit (flèches, compteur) et visionneuse (zoom, clavier, glisser)
 * <aplomb-collant>   : barre d’achat collante (mobile), après le bloc d’achat
 */
(() => {
  const doux = () => (window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth');

  /* ---------- Mesure ----------
     Les événements personnalisés passent par Shopify.analytics.publish : le
     pixel personnalisé (Réglages > Événements clients) les reçoit et applique le
     consentement de la Customer Privacy API. Le dataLayer de la page est
     alimenté en plus, sans aucun envoi tiers depuis le thème.
     Les événements standard (page_viewed, product_viewed, product_added_to_cart,
     checkout_started, checkout_completed) sont émis par Shopify : le thème ne
     les duplique pas. */
  const aplomb = (window.aplomb = window.aplomb || {});
  aplomb.suivre = (nom, donnees = {}) => {
    const evenement = `aplomb_${nom}`;
    try {
      window.dataLayer = window.dataLayer || [];
      window.dataLayer.push({ event: evenement, ...donnees });
      if (window.Shopify && Shopify.analytics && typeof Shopify.analytics.publish === 'function') {
        Shopify.analytics.publish(evenement, donnees);
      }
      document.dispatchEvent(new CustomEvent('aplomb:suivi', { detail: { nom: evenement, donnees } }));
    } catch (_) {
      /* la mesure ne doit jamais casser la page */
    }
  };

  document.addEventListener('click', (e) => {
    const el = e.target.closest('[data-suivi]');
    if (el) aplomb.suivre('cta_click', { cta: el.dataset.suivi, href: el.getAttribute('href') || null });
  });

  /* ---------- Variantes ---------- */
  class AplombVariantes extends HTMLElement {
    connectedCallback() {
      const json = this.querySelector('[data-variantes]');
      this.variantes = json ? JSON.parse(json.textContent) : [];
      this.racine = this.closest('[data-produit-id]') || document;
      this.addEventListener('change', () => this.maj());
    }

    choisies() {
      return [...this.querySelectorAll('fieldset')].map((fs) => {
        const c = fs.querySelector('input:checked');
        return c ? c.value : null;
      });
    }

    maj() {
      const sel = this.choisies();
      const v = this.variantes.find((x) => x.options.every((o, i) => o === sel[i]));
      const page = document;
      const form = page.getElementById(`achat-produit-${this.racine.dataset ? this.racine.dataset.produitId : ''}`);
      const portee = form || page;
      portee.querySelectorAll('[data-variant-input]').forEach((input) => {
        if (v) input.value = v.id;
      });
      page.querySelectorAll('[data-prix]').forEach((el) => {
        if (v) el.textContent = v.prix;
      });
      portee.querySelectorAll('[data-cta-vente]').forEach((b) => {
        b.disabled = !v || !v.disponible;
        const modele = b.dataset.libelle || '';
        b.textContent = v && v.disponible ? modele.replace('{prix}', v.prix) : b.dataset.epuise || 'Épuisé pour le moment';
      });
      page.querySelectorAll('[data-collant-bouton]').forEach((b) => {
        b.disabled = !v || !v.disponible;
      });
      const dispo = page.querySelector('[data-dispo].dispo--vente');
      if (dispo && v) {
        dispo.textContent = v.disponible ? dispo.dataset.stock || 'Disponible' : dispo.dataset.epuise || 'Épuisé pour le moment';
      }
      if (v) {
        const url = new URL(window.location.href);
        url.searchParams.set('variant', v.id);
        window.history.replaceState(window.history.state, '', url);
      }
    }
  }

  /* ---------- Galerie et visionneuse ---------- */
  class AplombGalerie extends HTMLElement {
    connectedCallback() {
      this.liste = this.querySelector('[data-galerie-liste]');
      if (!this.liste) return;
      this.items = [...this.liste.children];
      this.compteur = this.querySelector('[data-compteur]');
      this.index = 0;

      const prec = this.querySelector('[data-precedent]');
      const suiv = this.querySelector('[data-suivant]');
      if (prec) prec.addEventListener('click', () => this.defiler(this.index - 1));
      if (suiv) suiv.addEventListener('click', () => this.defiler(this.index + 1));

      if ('IntersectionObserver' in window && this.items.length > 1) {
        this.obs = new IntersectionObserver(
          (entrees) => {
            entrees.forEach((en) => {
              if (en.isIntersecting && en.intersectionRatio > 0.6) {
                this.index = Number(en.target.dataset.mediaIndex);
                this.majCompteur();
              }
            });
          },
          { root: this.liste, threshold: [0.6] }
        );
        this.items.forEach((it) => this.obs.observe(it));
      }

      this.dialog = this.querySelector('[data-visionneuse]');
      this.images = this.items
        .map((it) => it.querySelector('img'))
        .filter(Boolean);
      this.liste.addEventListener('click', (e) => {
        const b = e.target.closest('[data-zoom]');
        if (b) this.ouvrir(Number(b.dataset.zoom), b);
      });
      if (this.dialog) this.initVisionneuse();
    }

    disconnectedCallback() {
      if (this.obs) this.obs.disconnect();
    }

    majCompteur() {
      if (this.compteur) this.compteur.textContent = `${this.index + 1} / ${this.items.length}`;
    }

    defiler(i) {
      const n = (i + this.items.length) % this.items.length;
      const cible = this.items[n];
      this.liste.scrollTo({ left: cible.offsetLeft - this.liste.offsetLeft, behavior: doux() });
      this.index = n;
      this.majCompteur();
    }

    grandeSource(img) {
      const srcset = (img.getAttribute('srcset') || '').split(',').map((s) => s.trim().split(/\s+/));
      const plusGrand = srcset.sort((a, b) => parseInt(b[1], 10) - parseInt(a[1], 10))[0];
      return plusGrand && plusGrand[0] ? plusGrand[0] : img.currentSrc || img.src;
    }

    initVisionneuse() {
      const d = this.dialog;
      this.vImage = d.querySelector('[data-v-image]');
      this.vScene = d.querySelector('[data-v-scene]');
      this.vCompteur = d.querySelector('[data-v-compteur]');
      this.vZoom = d.querySelector('[data-v-zoom]');
      d.querySelector('[data-v-fermer]').addEventListener('click', () => d.close());
      d.querySelector('[data-v-precedent]').addEventListener('click', () => this.montrer(this.vIndex - 1));
      d.querySelector('[data-v-suivant]').addEventListener('click', () => this.montrer(this.vIndex + 1));
      this.vZoom.addEventListener('click', () => this.zoomer());
      this.vImage.addEventListener('click', (e) => this.zoomer(e));
      d.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') this.montrer(this.vIndex - 1);
        if (e.key === 'ArrowRight') this.montrer(this.vIndex + 1);
      });
      d.addEventListener('click', (e) => {
        if (e.target === d) d.close();
      });
      d.addEventListener('close', () => {
        document.documentElement.classList.remove('visionneuse-ouverte');
        if (this.declencheur) this.declencheur.focus();
      });
      let x0 = null;
      this.vScene.addEventListener('touchstart', (e) => {
        if (e.touches.length === 1 && !this.zoome) x0 = e.touches[0].clientX;
      }, { passive: true });
      this.vScene.addEventListener('touchend', (e) => {
        if (x0 === null) return;
        const dx = e.changedTouches[0].clientX - x0;
        x0 = null;
        if (Math.abs(dx) > 50) this.montrer(this.vIndex + (dx < 0 ? 1 : -1));
      });
    }

    ouvrir(i, declencheur) {
      if (!this.dialog || typeof this.dialog.showModal !== 'function') return;
      this.declencheur = declencheur;
      this.montrer(i);
      document.documentElement.classList.add('visionneuse-ouverte');
      this.dialog.showModal();
    }

    montrer(i) {
      const n = (i + this.images.length) % this.images.length;
      const img = this.images[n];
      this.vIndex = n;
      this.zoome = false;
      this.vScene.classList.remove('is-zoom');
      this.vZoom.setAttribute('aria-pressed', 'false');
      this.vImage.src = this.grandeSource(img);
      this.vImage.alt = img.alt;
      this.vCompteur.textContent = `${n + 1} / ${this.images.length}`;
    }

    zoomer(e) {
      this.zoome = !this.zoome;
      this.vScene.classList.toggle('is-zoom', this.zoome);
      this.vZoom.setAttribute('aria-pressed', String(this.zoome));
      if (this.zoome && e && e.clientX) {
        const r = this.vImage.getBoundingClientRect();
        this.vImage.style.transformOrigin = `${((e.clientX - r.left) / r.width) * 100}% ${((e.clientY - r.top) / r.height) * 100}%`;
      } else {
        this.vImage.style.transformOrigin = '50% 50%';
      }
    }
  }

  /* ---------- Barre collante ---------- */
  class AplombCollant extends HTMLElement {
    connectedCallback() {
      const cible = document.querySelector(this.dataset.cible || '[data-cta-principal]');
      if (!cible || !('IntersectionObserver' in window)) return;
      // Marge basse immense : la cible « sort » seulement quand elle passe
      // au-dessus de l’écran, même après un défilement très rapide.
      this.observer = new IntersectionObserver(
        ([entry]) => {
          const passe = !entry.isIntersecting && entry.boundingClientRect.top < 0;
          this.classList.toggle('is-visible', passe);
          this.toggleAttribute('inert', !passe);
          this.setAttribute('aria-hidden', String(!passe));
        },
        { rootMargin: '0px 0px 100000px 0px' }
      );
      this.observer.observe(cible);
    }

    disconnectedCallback() {
      if (this.observer) this.observer.disconnect();
    }
  }

  if (!customElements.get('aplomb-variantes')) customElements.define('aplomb-variantes', AplombVariantes);
  if (!customElements.get('aplomb-galerie')) customElements.define('aplomb-galerie', AplombGalerie);
  if (!customElements.get('aplomb-collant')) customElements.define('aplomb-collant', AplombCollant);

  /* Lien vers un champ e-mail (#liste-…-email) : on y place le curseur. */
  document.addEventListener('click', (event) => {
    const lien = event.target.closest('a[href*="-email"]');
    if (!lien) return;
    const id = lien.getAttribute('href').split('#')[1];
    const champ = id && document.getElementById(id);
    if (champ) {
      event.preventDefault();
      champ.scrollIntoView({ behavior: doux(), block: 'center' });
      champ.focus({ preventScroll: true });
    }
  });

  /* Menu mobile : se ferme avec Échap et au clic sur un lien. */
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;
    const menu = document.querySelector('[data-menu-mobile][open]');
    if (menu) {
      menu.open = false;
      menu.querySelector('summary').focus();
    }
  });

  /* Vidéos en lecture automatique : à l’arrêt si l’utilisateur limite les animations. */
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    document.querySelectorAll('video[autoplay]').forEach((v) => {
      v.pause();
      v.removeAttribute('autoplay');
      v.setAttribute('controls', '');
    });
  }
})();
