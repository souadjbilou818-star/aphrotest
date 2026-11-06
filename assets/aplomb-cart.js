/**
 * L’Aplomb — panier AJAX (API Ajax de Shopify, aucune dépendance).
 *
 * - Formulaires [data-panier="ajax"] : POST /cart/add.js (avec les compléments
 *   cochés), puis rafraîchissement du tiroir par l’API Section Rendering.
 * - Tiroir <dialog data-tiroir> et page panier [data-panier-page] :
 *   quantités (− / + / champ), retrait, erreurs lisibles (stock, limite).
 * - Le paiement reste le formulaire natif /cart (name="checkout") : aucun
 *   faux tunnel de paiement.
 * Sans JavaScript, tous les formulaires fonctionnent en navigation classique.
 */
(() => {
  const racine = (window.Shopify && Shopify.routes && Shopify.routes.root) || '/';
  const url = (chemin) => `${racine}${chemin.replace(/^\//, '')}`;
  const suivre = (nom, d) => window.aplomb && window.aplomb.suivre && window.aplomb.suivre(nom, d);
  const tiroir = document.querySelector('[data-tiroir]');
  const ouvrirTiroir = !!tiroir && document.body.dataset.panierTiroir === 'true';
  const messages = {
    erreur: document.body.dataset.panierErreur || 'La mise à jour n’a pas abouti. Réessayez.',
    ajout: document.body.dataset.ajoutErreur || 'L’ajout n’a pas abouti. Réessayez dans un instant.',
  };

  const sectionsDemandees = () => {
    const ids = [];
    if (tiroir) ids.push('panier-tiroir');
    const page = document.querySelector('[data-panier-page]');
    if (page && page.dataset.sectionId) ids.push(page.dataset.sectionId);
    return ids;
  };

  async function envoyer(chemin, corps) {
    const reponse = await fetch(url(chemin), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ ...corps, sections: sectionsDemandees().join(','), sections_url: window.location.pathname }),
    });
    let donnees = null;
    try {
      donnees = await reponse.json();
    } catch (_) {
      donnees = null;
    }
    if (!reponse.ok) {
      const err = new Error((donnees && (donnees.description || donnees.message)) || messages.erreur);
      err.statut = reponse.status;
      throw err;
    }
    return donnees || {};
  }

  function remplacer(sections) {
    if (!sections) return;
    const parseur = new DOMParser();
    Object.entries(sections).forEach(([id, html]) => {
      if (!html) return;
      const doc = parseur.parseFromString(html, 'text/html');
      const neuf = doc.querySelector('[data-panier-contenu]');
      const cible =
        id === 'panier-tiroir'
          ? tiroir && tiroir.querySelector('[data-panier-contenu]')
          : document.querySelector(`[data-panier-page][data-section-id="${CSS.escape(id)}"] [data-panier-contenu]`);
      if (neuf && cible) {
        cible.replaceWith(neuf);
        neuf.querySelectorAll('[data-sans-js]').forEach((el) => { el.hidden = true; });
      }
      if (neuf) majCompte(Number(neuf.dataset.compte));
    });
  }

  function majCompte(n) {
    if (Number.isNaN(n)) return;
    document.querySelectorAll('[data-panier-compte]').forEach((el) => {
      el.textContent = n;
    });
  }

  function erreurDans(conteneur, texte) {
    const el = conteneur && conteneur.querySelector('[data-panier-erreur], [data-achat-erreur]');
    if (!el) return;
    el.textContent = texte || '';
    el.hidden = !texte;
  }

  /* ---------- Ajout au panier ---------- */
  document.addEventListener('submit', async (e) => {
    const form = e.target;
    if (!(form instanceof HTMLFormElement) || form.dataset.panier !== 'ajax') return;
    if (!window.fetch) return;
    e.preventDefault();

    const bouton = e.submitter && e.submitter.form === form ? e.submitter : form.querySelector('[type="submit"]');
    const principal = form.querySelector('[type="submit"]');
    const idInput = form.querySelector('input[name="id"]');
    if (!idInput || !idInput.value) return;
    const qte = Number((form.querySelector('input[name="quantity"]') || {}).value || 1);
    const items = [{ id: Number(idInput.value), quantity: qte }];
    const complements = [...form.querySelectorAll('[data-complement]:checked')].map((c) => ({ id: Number(c.value), quantity: 1 }));
    items.push(...complements);

    erreurDans(form, '');
    [bouton, principal].forEach((b) => b && b.setAttribute('aria-busy', 'true'));
    [bouton, principal].forEach((b) => { if (b) b.disabled = true; });
    try {
      const reponse = await envoyer('cart/add.js', { items });
      remplacer(reponse.sections);
      suivre('ajout_panier_contexte', {
        contexte: form.id,
        variant_id: items[0].id,
        quantite: qte,
        complements: complements.map((c) => c.id),
      });
      form.querySelectorAll('[data-complement]:checked').forEach((c) => { c.checked = false; });
      if (ouvrirTiroir) {
        ouvrir(bouton);
      } else {
        window.location.href = url('cart');
      }
    } catch (err) {
      erreurDans(form, err.statut === 422 ? err.message : messages.ajout);
    } finally {
      [bouton, principal].forEach((b) => {
        if (!b) return;
        b.removeAttribute('aria-busy');
        b.disabled = false;
      });
    }
  });

  /* ---------- Tiroir ---------- */
  let declencheur = null;
  function ouvrir(depuis) {
    if (!tiroir || typeof tiroir.showModal !== 'function') {
      window.location.href = url('cart');
      return;
    }
    declencheur = depuis || document.activeElement;
    if (!tiroir.open) tiroir.showModal();
    document.documentElement.classList.add('tiroir-ouvert');
    const titre = tiroir.querySelector('.tiroir__titre');
    if (titre) {
      titre.setAttribute('tabindex', '-1');
      titre.focus();
    }
    suivre('panier_ouvert', {});
  }

  if (tiroir) {
    tiroir.addEventListener('close', () => {
      document.documentElement.classList.remove('tiroir-ouvert');
      if (declencheur && document.contains(declencheur)) declencheur.focus();
    });
    tiroir.addEventListener('click', (e) => {
      if (e.target === tiroir || e.target.closest('[data-tiroir-fermer]')) {
        if (e.target.closest('a[data-tiroir-fermer]') && !e.target.closest('a').getAttribute('href').startsWith('#')) return;
        tiroir.close();
      }
    });
    document.addEventListener('click', (e) => {
      const lien = e.target.closest('[data-panier-ouvrir]');
      if (!lien) return;
      e.preventDefault();
      ouvrir(lien);
    });
  }

  /* ---------- Quantités ---------- */
  const enCours = new WeakMap();
  async function changer(ligneEl, quantite) {
    const conteneur = ligneEl.closest('[data-panier-contenu]');
    const ligne = Number(ligneEl.dataset.ligne);
    if (enCours.get(conteneur)) return;
    enCours.set(conteneur, true);
    conteneur.setAttribute('aria-busy', 'true');
    erreurDans(conteneur, '');
    try {
      const reponse = await envoyer('cart/change.js', { line: ligne, quantity: Math.max(0, quantite) });
      remplacer(reponse.sections);
      if (!reponse.sections) window.location.reload();
    } catch (err) {
      erreurDans(conteneur, err.statut === 422 ? err.message : messages.erreur);
      conteneur.removeAttribute('aria-busy');
    } finally {
      enCours.delete(conteneur);
    }
  }

  document.addEventListener('click', (e) => {
    const b = e.target.closest('[data-qte]');
    const retirer = e.target.closest('[data-retirer]');
    const ligne = (b || retirer) && (b || retirer).closest('[data-ligne]');
    if (!ligne || !ligne.closest('[data-panier-contenu]')) return;
    e.preventDefault();
    if (retirer) {
      changer(ligne, 0);
      return;
    }
    const champ = ligne.querySelector('[data-qte-champ]');
    const actuel = Number(champ.value) || 0;
    changer(ligne, actuel + Number(b.dataset.qte));
  });

  document.addEventListener('change', (e) => {
    const champ = e.target.closest('[data-qte-champ]');
    if (!champ) return;
    const ligne = champ.closest('[data-ligne]');
    if (ligne && ligne.closest('[data-panier-contenu]')) changer(ligne, Number(champ.value) || 0);
  });

  /* Entrée dans un champ quantité : on met à jour, sans partir au paiement. */
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Enter') return;
    const champ = e.target.closest && e.target.closest('[data-qte-champ]');
    if (!champ) return;
    e.preventDefault();
    champ.dispatchEvent(new Event('change', { bubbles: true }));
  });

  /* La page panier sans bouton « Mettre à jour » quand le script tourne. */
  document.querySelectorAll('[data-sans-js]').forEach((el) => { el.hidden = true; });
})();
