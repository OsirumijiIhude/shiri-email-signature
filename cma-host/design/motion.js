/*
 * CM&A application-specific DOM adapters for published effects:
 * Motion Primitives TextEffect / TextRoll, copyright (c) 2024 ibelick, MIT.
 * React Bits AnimatedContent, copyright (c) 2026 David Haz,
 * MIT + Commons Clause. This is an application integration, not a component product.
 * See MOTION_SOURCES.md for exact upstream blobs, licences and adaptations.
 */
(() => {
  'use strict';
  if (window.CMAMotion) return;
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const preference = matchMedia('(prefers-reduced-motion: reduce)');
  const active = new Set();
  const byElement = new WeakMap();
  const observers = new Set();
  const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
  const canAnimate = () => !preference.matches && typeof Element.prototype.animate === 'function';
  const out = 'cubic-bezier(.22,1,.36,1)';

  function play(element, frames, options = {}) {
    if (!element || !canAnimate()) return Promise.resolve();
    byElement.get(element)?.cancel();
    let animation;
    try {
      animation = element.animate(frames, { duration: 500, easing: out, fill: 'both', ...options });
    } catch { return Promise.resolve(); }
    active.add(animation);
    byElement.set(element, animation);
    return animation.finished.catch(() => {}).then(() => {
      active.delete(animation);
      if (byElement.get(element) === animation) byElement.delete(element);
      animation.cancel();
    });
  }

  // Motion Primitives TextEffect: fade-in-blur preset, per-word stagger .05s.
  // Only the renderer changes: the existing semantic HTML is retained.
  function textEffect(element) {
    if (!element || !canAnimate() || element.dataset.cmaText) return;
    element.dataset.cmaText = 'true';
    element.setAttribute('aria-label', element.innerText.replace(/\s+/g, ' ').trim());
    const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    const words = [];
    for (const node of nodes) {
      const fragment = document.createDocumentFragment();
      for (const segment of node.textContent.split(/(\s+)/)) {
        if (!segment.trim()) { fragment.append(document.createTextNode(segment)); continue; }
        const word = document.createElement('span');
        word.className = 'cma-word';
        word.setAttribute('aria-hidden', 'true');
        word.textContent = segment;
        words.push(word);
        fragment.append(word);
      }
      node.replaceWith(fragment);
    }
    words.forEach((word, index) => play(word, [
      { opacity: 0, transform: 'translateY(20px)', filter: 'blur(12px)' },
      { opacity: 1, transform: 'translateY(0)', filter: 'blur(0px)' }
    ], { duration: 550, delay: index * 50 }));
  }

  // React Bits AnimatedContent: configurable offset, scale, opacity, once in view.
  function animatedContent(element, { distance = 40, duration = 800, scale = 1, delay: wait = 0 } = {}) {
    return play(element, [
      { opacity: 0, transform: `translateY(${distance}px) scale(${scale})` },
      { opacity: 1, transform: 'translateY(0) scale(1)' }
    ], { duration, delay: wait });
  }

  function observeOnce(elements, callback, root = null) {
    if (!canAnimate() || !('IntersectionObserver' in window)) return;
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        observer.unobserve(entry.target);
        callback(entry.target);
      });
    }, { root, threshold: 0.1 });
    observers.add(observer);
    elements.forEach(element => observer.observe(element));
    return observer;
  }

  // Motion Primitives TextRoll: original 0 -> 90 / 90 -> 0 rotateX layers.
  // Configured with a shorter per-character delay for navigation labels.
  function addTextRoll(link) {
    if (!canAnimate()) return;
    const label = link.textContent.trim();
    if (!label || link.children.length) return;
    const roll = document.createElement('span');
    roll.className = 'cma-roll';
    roll.setAttribute('aria-hidden', 'true');
    const letters = [...label].map(character => {
      const unit = document.createElement('span');
      unit.className = 'cma-roll-unit';
      for (const className of ['cma-roll-front', 'cma-roll-back', 'cma-roll-width']) {
        const layer = document.createElement('span');
        layer.className = className;
        layer.textContent = character === ' ' ? '\u00a0' : character;
        unit.append(layer);
      }
      roll.append(unit);
      return unit;
    });
    const accessibleLabel = document.createElement('span');
    accessibleLabel.className = 'sr-only';
    accessibleLabel.textContent = label;
    link.replaceChildren(roll, accessibleLabel);
    const run = () => {
      if (!canAnimate()) return;
      letters.forEach((unit, index) => {
        unit.children[0].style.transform = 'rotateX(90deg)';
        unit.children[1].style.transform = 'rotateX(0deg)';
        play(unit.children[0], [{ transform: 'rotateX(0deg)' }, { transform: 'rotateX(90deg)' }],
          { duration: 320, delay: index * 18, easing: 'ease-in' });
        play(unit.children[1], [{ transform: 'rotateX(90deg)' }, { transform: 'rotateX(0deg)' }],
          { duration: 320, delay: index * 18 + 120, easing: 'ease-in' });
      });
    };
    link.addEventListener('pointerenter', event => { if (event.pointerType !== 'touch') run(); });
    link.addEventListener('focus', run);
  }

  let introDone = false;
  async function finishIntro(immediate = false) {
    if (introDone) return;
    introDone = true;
    clearTimeout(window.__cmaIntroTimer);
    const intro = $('#cma-intro');
    try {
      if (!immediate && intro && document.documentElement.classList.contains('cma-intro')) {
        await play(intro, [{ opacity: 1 }, { opacity: 0 }], { duration: 220 });
      }
    } finally {
      document.documentElement.classList.remove('cma-intro');
      intro?.remove();
    }
  }

  async function start() {
    const intro = $('#cma-intro');
    const skip = $('#cma-skip-intro');
    const interrupt = () => finishIntro(true);
    skip?.addEventListener('click', interrupt);
    const onKey = event => { if (event.key === 'Escape' || event.key === 'Tab') interrupt(); };
    document.addEventListener('keydown', onKey);
    window.addEventListener('wheel', interrupt, { passive: true, once: true });
    window.addEventListener('touchstart', interrupt, { passive: true, once: true });
    if (intro && document.documentElement.classList.contains('cma-intro') && canAnimate()) {
      try { sessionStorage.setItem('cma-intro-seen', '1'); } catch { /* Storage is optional. */ }
      const readiness = Promise.allSettled([
        document.fonts?.ready || Promise.resolve(),
        ...$$('#hero-products img, .cma-intro-logo').map(image => image.decode ? image.decode() : Promise.resolve())
      ]);
      // A short brand introduction, not a fabricated loading percentage.
      const elapsed = performance.now() - (window.__cmaIntroStart || 0);
      await Promise.all([delay(Math.max(0, 900 - elapsed)), Promise.race([readiness, delay(1500)])]);
      await finishIntro();
    } else await finishIntro(true);
    document.removeEventListener('keydown', onKey);
    if (!canAnimate()) return;
    textEffect($('#hero-title'));
    $$('#hero-products img').forEach((image, index) => animatedContent(image,
      { distance: 60, duration: 850, scale: 0.97, delay: index * 85 }));
    animatedContent($('.hero-description'), { distance: 20, duration: 600, delay: 120 });
    $$('.hero-actions a, .nav-cta').forEach(addTextRoll);
    // The rest of the page stays still until the visitor interacts.
    $$('.filter').forEach(button => button.addEventListener('click', () => {
      $$('.work-card:not([hidden])').forEach((card, index) => animatedContent(card,
        { distance: 24, duration: 500, delay: Math.min(index * 40, 160) }));
    }));
    for (const dialog of $$('dialog')) {
      let galleryObserver;
      const onOpen = () => {
        galleryObserver?.disconnect();
        if (!dialog.open || !canAnimate()) return;
        animatedContent($('.case-hero', dialog) || dialog, { distance: 20, duration: 400 });
        galleryObserver = observeOnce($$('.case-gallery figure', dialog), element => animatedContent(element), dialog);
      };
      new MutationObserver(onOpen).observe(dialog, { attributes: true, attributeFilter: ['open'] });
      if (dialog.open) onOpen();
    }
  }

  // Hooks are called by the existing carousel; its routing and labels stay native.
  window.CMAMotion = {
    beforeSwap: () => Promise.all($$('#hero-products img').map(image => play(image,
      [{ opacity: 1, transform: 'translateY(0)' }, { opacity: 0, transform: 'translateY(-20px)' }],
      { duration: 160, easing: 'ease-in' }))),
    afterSwap: () => $$('#hero-products img').forEach((image, index) => animatedContent(image,
      { distance: 40, duration: 650, delay: index * 65 })),
    finishIntro,
    version: '2026-09-21.1'
  };
  preference.addEventListener('change', () => {
    if (!preference.matches) return;
    active.forEach(animation => animation.cancel());
    observers.forEach(observer => observer.disconnect());
    finishIntro(true);
  });
  window.addEventListener('pagehide', () => {
    active.forEach(animation => animation.cancel());
    observers.forEach(observer => observer.disconnect());
    finishIntro(true);
  });
  start().catch(() => finishIntro(true));
})();
