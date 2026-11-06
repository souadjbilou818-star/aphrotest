/**
 * <aplomb-quiz> : quiz de choix d’équipement.
 *
 * - Une question à la fois ; « Continuer » valide (message d’erreur si aucune
 *   réponse), « Retour » revient en arrière sans perdre les réponses.
 * - Au toucher ou au clic, choisir une réponse passe à la suite. Au clavier
 *   (flèches), rien ne bouge tant que l’on n’a pas validé.
 * - Réponses gardées dans sessionStorage pour la visite (aucune donnée
 *   personnelle). En page dédiée, chaque étape crée une entrée d’historique :
 *   le bouton Retour du navigateur revient à la question précédente.
 * - Recommandation : somme pondérée des orientations de chaque réponse ;
 *   une réponse peut écarter une famille (ex. petit espace → pas de reformer).
 * - Événements : quiz_started, quiz_step_completed, quiz_completed,
 *   recommendation_displayed, recommendation_cta (assets/aplomb-interactions.js).
 */
(() => {
  const FAMILLES = ['essentiels', 'coulisse', 'atelier'];
  const AUTO_DELAI = 220;
  const suivre = (nom, donnees) => window.aplomb && window.aplomb.suivre && window.aplomb.suivre(nom, donnees);
  const reduit = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  class AplombQuiz extends HTMLElement {
    connectedCallback() {
      this.id_ = this.dataset.quizId || 'quiz';
      this.cle = `aplomb-quiz:${this.id_}`;
      this.mode = this.dataset.mode;
      this.form = this.querySelector('[data-quiz-form]');
      this.etapes = [...this.querySelectorAll('[data-quiz-etape]')];
      this.total = this.etapes.length;
      this.barre = this.querySelector('[data-quiz-barre]');
      this.segments = [...this.querySelectorAll('[data-quiz-segment]')];
      this.compte = this.querySelector('[data-quiz-compte]');
      this.resultats = this.querySelector('[data-quiz-resultats]');
      if (!this.form || !this.total) return;

      this.etat = this.lire();
      this.dernierPointeur = 0;
      this.form.hidden = false;
      this.barre.hidden = false;

      this.form.addEventListener('pointerdown', (e) => {
        this.cibleTouchee = e.target.closest('.quiz__option');
        this.dernierPointeur = Date.now();
      });
      this.form.addEventListener('change', (e) => this.surChoix(e));
      this.form.addEventListener('submit', (e) => { e.preventDefault(); this.valider(); });
      this.querySelector('[data-quiz-retour]').addEventListener('click', () => this.retour());
      const recommencer = this.querySelector('[data-quiz-recommencer]');
      if (recommencer) recommencer.addEventListener('click', () => this.recommencer());
      this.querySelectorAll('[data-quiz-sortie]').forEach((a) =>
        a.addEventListener('click', () => suivre('quiz_exit', { quiz_id: this.id_, etape: this.etat.etape }))
      );
      this.querySelectorAll('[data-quiz-cta]').forEach((a) =>
        a.addEventListener('click', () => suivre('recommendation_cta', { quiz_id: this.id_, famille: this.etat.famille, action: a.dataset.quizCta }))
      );
      this.resultats.addEventListener('submit', (e) => {
        const famille = e.target.closest('[data-quiz-resultat]');
        if (famille) suivre('recommendation_cta', { quiz_id: this.id_, famille: famille.dataset.quizResultat, action: e.target.matches('[data-panier]') ? 'panier' : 'liste_attente' });
      });

      if (this.mode === 'page') {
        window.addEventListener('popstate', (e) => {
          const n = e.state && e.state.aplombQuiz;
          if (typeof n === 'number' || n === 'resultat') this.aller(n, { historique: false });
        });
      }

      this.restaurer();
    }

    /* ---------- État ---------- */
    lire() {
      try {
        const e = JSON.parse(sessionStorage.getItem(this.cle));
        if (e && e.v === 1 && e.reponses) return e;
      } catch (_) { /* stockage indisponible : on repart de zéro */ }
      return { v: 1, reponses: {}, etape: 1, famille: null, commence: false };
    }

    ecrire() {
      try { sessionStorage.setItem(this.cle, JSON.stringify(this.etat)); } catch (_) { /* navigation privée */ }
    }

    restaurer() {
      this.etapes.forEach((fs) => {
        const v = this.etat.reponses[fs.dataset.cle];
        if (!v) return;
        const input = fs.querySelector(`input[value="${CSS.escape(String(v))}"]`);
        if (input) input.checked = true;
      });
      if (this.etat.famille && this.etapes.every((fs) => this.reponse(fs))) {
        this.afficherResultat({ annoncer: false, suivi: false });
      } else {
        const n = Math.min(Math.max(1, this.etat.etape || 1), this.total);
        this.aller(n, { focus: false, historique: false });
        if (this.mode === 'page') history.replaceState({ ...(history.state || {}), aplombQuiz: n }, '');
      }
    }

    reponse(fs) {
      return fs.querySelector('input:checked');
    }

    /* ---------- Navigation ---------- */
    surChoix(e) {
      const input = e.target;
      if (!input.matches('input[type="radio"]')) return;
      const fs = input.closest('[data-quiz-etape]');
      this.erreur(fs, false);
      this.etat.reponses[fs.dataset.cle] = input.value;
      if (!this.etat.commence) {
        this.etat.commence = true;
        suivre('quiz_started', { quiz_id: this.id_, mode: this.mode });
      }
      this.ecrire();
      // Passage automatique seulement après un toucher ou un clic sur cette réponse.
      const touchee = this.cibleTouchee && this.cibleTouchee.contains(input) && Date.now() - this.dernierPointeur < 800;
      this.cibleTouchee = null;
      if (touchee) {
        clearTimeout(this.minuteur);
        this.minuteur = setTimeout(() => this.valider(), reduit() ? 0 : AUTO_DELAI);
      }
    }

    valider() {
      const n = this.etat.etape;
      const fs = this.etapes[n - 1];
      const choix = this.reponse(fs);
      if (!choix) {
        this.erreur(fs, true);
        const premier = fs.querySelector('input');
        if (premier) premier.focus();
        return;
      }
      suivre('quiz_step_completed', {
        quiz_id: this.id_,
        etape: n,
        question: fs.dataset.cle,
        reponse: choix.dataset.libelle,
      });
      if (n < this.total) {
        this.aller(n + 1);
      } else {
        this.afficherResultat({ annoncer: true, suivi: true });
      }
    }

    retour() {
      if (!this.resultats.hidden) {
        if (this.mode === 'page' && history.state && history.state.aplombQuiz === 'resultat') {
          history.back();
          return;
        }
        this.aller(this.total);
        return;
      }
      if (this.etat.etape <= 1) return;
      if (this.mode === 'page' && history.state && history.state.aplombQuiz === this.etat.etape) {
        history.back();
        return;
      }
      this.aller(this.etat.etape - 1);
    }

    aller(n, { focus = true, historique = true } = {}) {
      if (n === 'resultat') {
        this.afficherResultat({ annoncer: true, suivi: false, historique: false });
        return;
      }
      const precedent = this.etat.etape;
      this.etat.etape = n;
      this.etat.famille = null;
      this.ecrire();
      this.resultats.hidden = true;
      this.form.hidden = false;
      this.etapes.forEach((fs, i) => {
        const actif = i === n - 1;
        fs.hidden = !actif;
        if (actif && !reduit() && precedent !== n) {
          fs.classList.remove('is-entree');
          void fs.offsetWidth;
          fs.classList.add('is-entree');
        }
      });
      this.progression(n);
      if (historique && this.mode === 'page') history.pushState({ ...(history.state || {}), aplombQuiz: n }, '');
      if (focus) this.focaliser(this.etapes[n - 1].querySelector('.quiz__question'));
    }

    progression(n) {
      const fini = n === 'resultat';
      this.segments.forEach((s, i) => s.classList.toggle('is-fait', fini || i < n));
      this.segments.forEach((s, i) => s.classList.toggle('is-actuel', !fini && i === n - 1));
      const retour = this.querySelector('[data-quiz-retour]');
      retour.hidden = !fini && n <= 1;
      const modele = this.dataset.libelleQuestion || 'Question {n} sur {total}';
      this.compte.textContent = fini ? '' : modele.replace('{n}', n).replace('{total}', this.total);
    }

    erreur(fs, visible) {
      const msg = fs.querySelector('[data-quiz-erreur]');
      if (msg) msg.hidden = !visible;
      fs.querySelectorAll('input').forEach((i) => i.toggleAttribute('aria-invalid', visible));
    }

    focaliser(el) {
      if (!el) return;
      el.focus({ preventScroll: true });
      const haut = this.getBoundingClientRect().top;
      if (haut < 0 || haut > window.innerHeight * 0.4) {
        const marge = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--header-h')) || 64;
        window.scrollTo({ top: window.scrollY + haut - marge, behavior: reduit() ? 'auto' : 'smooth' });
      }
    }

    recommencer() {
      this.etapes.forEach((fs) => fs.querySelectorAll('input').forEach((i) => { i.checked = false; }));
      this.etat = { v: 1, reponses: {}, etape: 1, famille: null, commence: false };
      this.ecrire();
      suivre('quiz_restarted', { quiz_id: this.id_ });
      this.aller(1);
    }

    /* ---------- Recommandation ---------- */
    calculer() {
      const scores = Object.fromEntries(FAMILLES.map((f) => [f, 0]));
      const exclues = new Map();
      const choix = [];
      let decisive = null;
      let poidsMax = 0;
      this.etapes.forEach((fs) => {
        const input = this.reponse(fs);
        if (!input) return;
        const poids = Number(fs.dataset.poids) || 1;
        const orient = (input.dataset.oriente || '').split(/\s+/).filter((f) => FAMILLES.includes(f));
        orient.forEach((f) => { scores[f] += (2 * poids) / orient.length; });
        const ex = input.dataset.exclut;
        if (FAMILLES.includes(ex)) exclues.set(ex, input);
        if (poids > poidsMax && orient.length) { poidsMax = poids; decisive = orient; }
        choix.push({ fs, input, orient });
      });
      const classement = [...FAMILLES].sort((a, b) => {
        if (scores[b] !== scores[a]) return scores[b] - scores[a];
        const da = decisive && decisive.includes(a) ? 1 : 0;
        const db = decisive && decisive.includes(b) ? 1 : 0;
        if (db !== da) return db - da;
        return (b === 'coulisse') - (a === 'coulisse');
      });
      const premier = classement[0];
      const famille = classement.find((f) => !exclues.has(f)) || premier;
      const ecartee = famille !== premier ? { famille: premier, raison: exclues.get(premier) } : null;
      return { famille, scores, choix, ecartee };
    }

    afficherResultat({ annoncer = true, suivi = true, historique = true } = {}) {
      const r = this.calculer();
      this.etat.famille = r.famille;
      this.etat.etape = this.total;
      this.ecrire();

      this.form.hidden = true;
      this.resultats.hidden = false;
      const panneaux = [...this.resultats.querySelectorAll('[data-quiz-resultat]')];
      let actif = null;
      panneaux.forEach((p) => {
        p.hidden = p.dataset.quizResultat !== r.famille;
        if (!p.hidden) actif = p;
      });
      this.progression('resultat');

      // Arguments : les réponses qui mènent à cette famille.
      const liste = actif.querySelector('[data-quiz-arguments]');
      liste.replaceChildren();
      r.choix
        .filter((c) => c.orient.includes(r.famille) && c.input.dataset.argument)
        .forEach((c) => {
          const li = document.createElement('li');
          li.textContent = c.input.dataset.argument;
          liste.append(li);
        });
      liste.hidden = !liste.children.length;

      const ecarte = actif.querySelector('[data-quiz-ecarte]');
      if (r.ecartee && r.ecartee.raison && r.ecartee.raison.dataset.argument) {
        ecarte.textContent = r.ecartee.raison.dataset.argument;
        ecarte.hidden = false;
      } else {
        ecarte.hidden = true;
      }

      // Récapitulatif des réponses.
      const recap = this.querySelector('[data-quiz-recap]');
      recap.replaceChildren();
      r.choix.forEach((c) => {
        const div = document.createElement('div');
        const dt = document.createElement('dt');
        const dd = document.createElement('dd');
        dt.textContent = c.fs.dataset.question;
        dd.textContent = c.input.dataset.libelle;
        div.append(dt, dd);
        recap.append(div);
      });

      if (historique && this.mode === 'page' && !(history.state && history.state.aplombQuiz === 'resultat')) {
        history.pushState({ ...(history.state || {}), aplombQuiz: 'resultat' }, '');
      }
      if (annoncer) this.focaliser(actif);
      if (suivi) {
        const reponses = Object.fromEntries(r.choix.map((c) => [c.fs.dataset.cle, c.input.dataset.libelle]));
        suivre('quiz_completed', { quiz_id: this.id_, reponses });
        suivre('recommendation_displayed', {
          quiz_id: this.id_,
          famille: r.famille,
          produit_id: actif.dataset.produitId || null,
          produit_titre: actif.dataset.produitTitre || null,
          famille_ecartee: r.ecartee ? r.ecartee.famille : null,
        });
      }
    }
  }

  if (!customElements.get('aplomb-quiz')) customElements.define('aplomb-quiz', AplombQuiz);
})();
