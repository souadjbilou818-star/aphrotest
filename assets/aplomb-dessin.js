/**
 * <aplomb-dessin> : repli JavaScript de l'animation du chariot.
 * L'animation principale est en CSS (animation-timeline). Ce composant ne
 * s'active que si le navigateur ne la gère pas, et jamais si l'utilisateur
 * a demandé de réduire les animations. Il écrit --p (0 -> 1) sur l'élément.
 */
class AplombDessin extends HTMLElement {
  connectedCallback() {
    if (CSS.supports('animation-timeline: scroll()')) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    this.mode = this.dataset.timeline === 'root' ? 'root' : 'view';
    this.ticking = false;
    this.update = this.update.bind(this);
    this.onScroll = () => {
      if (this.ticking) return;
      this.ticking = true;
      requestAnimationFrame(this.update);
    };
    this.observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        window.addEventListener('scroll', this.onScroll, { passive: true });
        this.update();
      } else {
        window.removeEventListener('scroll', this.onScroll);
      }
    });
    this.observer.observe(this);
  }

  disconnectedCallback() {
    if (this.observer) this.observer.disconnect();
    window.removeEventListener('scroll', this.onScroll);
  }

  update() {
    this.ticking = false;
    const vh = window.innerHeight;
    let p;
    if (this.mode === 'root') {
      p = window.scrollY / (vh * 0.7);
    } else {
      const r = this.getBoundingClientRect();
      const cover = (vh - r.top) / (vh + r.height);
      p = (cover - 0.25) / 0.5;
    }
    this.style.setProperty('--p', Math.min(1, Math.max(0, p)).toFixed(4));
  }
}

if (!customElements.get('aplomb-dessin')) customElements.define('aplomb-dessin', AplombDessin);
