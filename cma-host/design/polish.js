/* Section tracking uses document order and one shared activation line. */
(() => {
  'use strict';
  if (window.__cmaEditorialReady) return;
  window.__cmaEditorialReady = true;
  const nav = document.querySelector('.nav');
  const links = [...document.querySelectorAll('.nav-links a, #mobile-nav a[href^="#"]')];
  const ids = new Set(links.map(link => link.hash.slice(1)));
  const sections = [...document.querySelectorAll('main > section[id]')].filter(section => ids.has(section.id));
  let pending = false, activeId = '';
  function updateNavigation() {
    pending = false;
    const headerHeight = nav?.getBoundingClientRect().height || 82;
    document.documentElement.style.setProperty('--cma-header', headerHeight + 'px');
    const activationLine = headerHeight + 24;
    let current = '';
    for (const section of sections) {
      if (section.getBoundingClientRect().top <= activationLine + 1) current = section.id;
      else break;
    }
    if (scrollY > 0 && innerHeight + scrollY >= document.documentElement.scrollHeight - 2) {
      current = sections.at(-1)?.id || current;
    }
    if (current === activeId) return;
    activeId = current;
    for (const link of links) {
      const selected = link.hash === '#' + current;
      link.classList.toggle('active', selected);
      if (selected) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    }
  }
  function scheduleNavigation() {
    if (!pending) { pending = true; requestAnimationFrame(updateNavigation); }
  }
  window.addEventListener('scroll', scheduleNavigation, { passive: true });
  window.addEventListener('resize', scheduleNavigation);
  window.addEventListener('pageshow', scheduleNavigation);
  window.addEventListener('hashchange', scheduleNavigation);
  document.addEventListener('toggle', scheduleNavigation, true);
  document.addEventListener('load', scheduleNavigation, true);
  if ('ResizeObserver' in window) {
    const resize = new ResizeObserver(scheduleNavigation);
    [nav, document.querySelector('main'), ...sections].filter(Boolean).forEach(node => resize.observe(node));
  }
  document.fonts?.ready.then(scheduleNavigation);
  scheduleNavigation();

  // A few short entrance accents, never hidden content or scroll hijacking.
  const preference = matchMedia('(prefers-reduced-motion: reduce)');
  const animations = new Set();
  function animateOnce(element) {
    if (preference.matches || typeof element.animate !== 'function') return;
    const drawing = element.classList.contains('cma-linework');
    const targets = drawing ? [...element.querySelectorAll('path')] : [element];
    targets.forEach((target, index) => {
      const frames = drawing
        ? [{ strokeDasharray: '1', strokeDashoffset: '1' }, { strokeDasharray: '1', strokeDashoffset: '0' }]
        : [{ opacity: 0.35, transform: 'translateY(12px)' }, { opacity: 1, transform: 'translateY(0)' }];
      const animation = target.animate(frames, {
        duration: drawing ? 850 : 480,
        delay: drawing ? index * 65 : 0,
        easing: 'cubic-bezier(.22,1,.36,1)',
        fill: 'none'
      });
      animations.add(animation);
      animation.finished.catch(() => {}).finally(() => { animations.delete(animation); animation.cancel(); });
    });
  }
  let observer;
  if ('IntersectionObserver' in window && !preference.matches) {
    observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        observer.unobserve(entry.target);
        animateOnce(entry.target);
      });
    }, { threshold: 0.2 });
    document.querySelectorAll('#about-title, #brands-title, #services-title, #contact-title, .cma-linework').forEach(node => observer.observe(node));
  }
  function cancelMotion() { animations.forEach(animation => animation.cancel()); }
  preference.addEventListener('change', () => { if (preference.matches) { observer?.disconnect(); cancelMotion(); } });
  window.addEventListener('pagehide', cancelMotion);
})();
