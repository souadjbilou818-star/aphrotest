/**
 * L'Aplomb — composants vanilla (aucune dépendance).
 * <aplomb-editions> : sélecteur Essentiel / Studio
 * <aplomb-collant>  : appel à l'action collant (mobile), après le premier écran
 * <aplomb-quiz>     : quiz « Quelle édition pour vous ? »
 */

const doux = () => (window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth');

/* Met à jour tous les formulaires de la page quand l'édition change. */
function appliquerEdition(detail) {
  document.querySelectorAll('[data-variant-input]').forEach((input) => {
    input.value = detail.id;
  });
  document.querySelectorAll('[data-cta-vente]').forEach((bouton) => {
    const modele = document.querySelector('aplomb-editions')?.dataset.libelleVente || '';
    bouton.disabled = !detail.disponible;
    if (modele) bouton.textContent = modele.replace('{prix}', detail.prix);
  });
  document.querySelectorAll('[data-collant-nom]').forEach((el) => {
    const base = el.textContent.split(' · ')[0];
    el.textContent = `${base} · ${detail.nom}`;
  });
  document.querySelectorAll('[data-collant-prix]').forEach((el) => {
    const suffixe = el.textContent.trim().split(' ').pop();
    el.textContent = `${detail.prix} ${suffixe}`;
  });
}

class AplombEditions extends HTMLElement {
  connectedCallback() {
    this.addEventListener('change', (event) => {
      const input = event.target;
      if (!(input instanceof HTMLInputElement) || input.type !== 'radio') return;
      const detail = {
        id: input.value,
        prix: input.dataset.prix,
        nom: input.dataset.nom,
        disponible: input.dataset.disponible === 'true',
      };
      appliquerEdition(detail);
      const url = new URL(window.location.href);
      url.searchParams.set('variant', detail.id);
      window.history.replaceState({}, '', url);
    });
  }

  choisir(id) {
    const input = this.querySelector(`input[value="${CSS.escape(String(id))}"]`);
    if (!input) return false;
    input.checked = true;
    input.dispatchEvent(new Event('change', { bubbles: true }));
    return true;
  }
}

class AplombCollant extends HTMLElement {
  connectedCallback() {
    const cible = document.querySelector(this.dataset.cible || '[data-cta-principal]');
    if (!cible || !('IntersectionObserver' in window)) return;
    this.observer = new IntersectionObserver(([entry]) => {
      const passe = !entry.isIntersecting && entry.boundingClientRect.top < 0;
      this.classList.toggle('is-visible', passe);
      this.toggleAttribute('inert', !passe);
      this.setAttribute('aria-hidden', String(!passe));
    });
    this.observer.observe(cible);
  }

  disconnectedCallback() {
    if (this.observer) this.observer.disconnect();
  }
}

class AplombQuiz extends HTMLElement {
  connectedCallback() {
    this.form = this.querySelector('[data-quiz-form]');
    this.etapes = [...this.querySelectorAll('[data-etape]')];
    this.nav = this.querySelector('[data-quiz-nav]');
    this.suivant = this.querySelector('[data-suivant]');
    this.precedent = this.querySelector('[data-precedent]');
    this.resultat = this.querySelector('[data-resultat]');
    if (!this.form || this.etapes.length === 0) return;

    this.index = 0;
    this.libelleSuivant = this.suivant.textContent;
    this.nav.hidden = false;
    this.montrer(0);

    this.form.addEventListener('change', () => {
      this.suivant.disabled = !this.reponse(this.index);
    });
    this.suivant.addEventListener('click', () => {
      if (!this.reponse(this.index)) return;
      if (this.index < this.etapes.length - 1) this.montrer(this.index + 1, true);
      else this.conclure();
    });
    this.precedent.addEventListener('click', () => this.montrer(Math.max(0, this.index - 1), true));
    this.querySelector('[data-recommencer]')?.addEventListener('click', () => {
      this.form.reset();
      this.resultat.hidden = true;
      this.form.hidden = false;
      this.montrer(0, true);
    });
  }

  reponse(i) {
    const choisi = this.etapes[i].querySelector('input:checked');
    return choisi ? choisi.value : null;
  }

  montrer(i, focus) {
    this.index = i;
    this.etapes.forEach((etape, n) => {
      etape.hidden = n !== i;
    });
    this.precedent.hidden = i === 0;
    this.suivant.disabled = !this.reponse(i);
    this.suivant.textContent = i === this.etapes.length - 1 ? this.dataset.voir || this.libelleSuivant : this.libelleSuivant;
    if (focus) this.etapes[i].querySelector('input')?.focus();
  }

  conclure() {
    const r = Object.fromEntries(new FormData(this.form).entries());
    const raisons = [];
    if (r.sol === 'parquet') raisons.push('les patins en feutre protègent votre parquet');
    if (r.rangement === 'oui') raisons.push('la housse à sangle rend le rangement quotidien plus simple');
    if (r.frequence === '3plus') raisons.push('le programme de 8 semaines suit votre rythme');
    if (r.pratique === 'studio') raisons.push('la bande forte prolonge le travail de vos cours');
    const studio = raisons.length > 0;
    const edition = studio ? 'Studio' : 'Essentiel';

    this.querySelector('[data-edition]').textContent = edition;
    this.querySelector('[data-raison]').textContent = studio
      ? `Parce que ${raisons.join(', ')}.`
      : 'Le mini-reformer, quatre élastiques, les poignées et le programme de 28 jours suffisent pour bien commencer.';

    const lien = this.querySelector('[data-lien]');
    const id = studio ? this.dataset.idStudio : this.dataset.idEssentiel;
    lien.href = studio ? this.dataset.urlStudio : this.dataset.urlEssentiel;
    lien.textContent = `Voir l’édition ${edition}`;

    const editions = document.querySelector('aplomb-editions');
    lien.onclick = editions && id
      ? (event) => {
          if (editions.choisir(id)) {
            event.preventDefault();
            document.getElementById('achat')?.scrollIntoView({ behavior: doux(), block: 'start' });
          }
        }
      : null;

    const tags = this.querySelector('[data-quiz-tags]');
    if (tags) tags.value = `waitlist,aplomb,quiz,edition-${edition.toLowerCase()},objectif-${r.objectif || 'na'}`;

    this.form.hidden = true;
    this.resultat.hidden = false;
    this.resultat.focus();
  }
}

if (!customElements.get('aplomb-editions')) customElements.define('aplomb-editions', AplombEditions);
if (!customElements.get('aplomb-collant')) customElements.define('aplomb-collant', AplombCollant);
if (!customElements.get('aplomb-quiz')) customElements.define('aplomb-quiz', AplombQuiz);

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
