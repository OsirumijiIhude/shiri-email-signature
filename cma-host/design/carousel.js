  // CM&A carousel: one controller owns timing, transitions and manual input.
  let slide = 0, slideRevision = 0;
  const carouselStage = $('.hero-art-stage');
  const rotationButton = $('#slide-toggle');
  const rotationLabel = $('#slide-toggle-label');
  const slideStatus = $('#slide-status');
  const rotationPreference = matchMedia('(prefers-reduced-motion: reduce)');
  const slideDuration = 6000;
  const decodedImages = new Map();
  let rotationTimer = 0, progressAnimation = null, changingSlide = false;
  let userPaused = false, focusPaused = false, pointerPaused = false;
  let pageSuspended = false;
  let carouselVisible = carouselStage.getBoundingClientRect().bottom > 0 &&
    carouselStage.getBoundingClientRect().top < innerHeight;

  function stopRotation() {
    clearTimeout(rotationTimer);
    rotationTimer = 0;
    progressAnimation?.cancel();
    progressAnimation = null;
  }
  function rotationAllowed() {
    return !userPaused && !focusPaused && !pointerPaused && !pageSuspended &&
      !document.hidden && carouselVisible && !rotationPreference.matches &&
      !document.querySelector('dialog[open]') &&
      !document.documentElement.classList.contains('cma-intro');
  }
  function syncRotation() {
    const stopped = userPaused || focusPaused;
    rotationButton.hidden = rotationPreference.matches;
    rotationButton.dataset.paused = String(stopped);
    rotationButton.setAttribute('aria-label', stopped ? 'Start automatic project rotation' : 'Pause automatic project rotation');
    rotationLabel.textContent = stopped ? 'Play' : 'Pause';
    if (!rotationAllowed() || changingSlide) { stopRotation(); return; }
    if (rotationTimer) return;
    const progress = $('.slide-progress > span');
    if (progress && typeof progress.animate === 'function') {
      progressAnimation = progress.animate(
        [{ transform: 'scaleX(0)' }, { transform: 'scaleX(1)' }],
        { duration: slideDuration, easing: 'linear', fill: 'forwards' }
      );
    }
    rotationTimer = setTimeout(() => {
      rotationTimer = 0;
      changeSlide(1, true);
    }, slideDuration);
  }
  function decodeAsset(key) {
    const source = assets[key];
    if (!source) return Promise.reject(new Error('Missing carousel artwork: ' + key));
    if (!decodedImages.has(source)) {
      const image = new Image();
      const ready = new Promise((resolve, reject) => {
        const timeout = setTimeout(() => reject(new Error('Artwork loading timed out')), 5000);
        const finish = ok => { clearTimeout(timeout); ok ? resolve() : reject(new Error('Artwork could not load')); };
        image.onload = () => {
          if (image.decode) image.decode().catch(() => {}).then(() => finish(true));
          else finish(true);
        };
        image.onerror = () => finish(false);
        image.src = source;
      }).catch(error => { decodedImages.delete(source); throw error; });
      decodedImages.set(source, ready);
    }
    return decodedImages.get(source);
  }
  async function changeSlide(delta, automatic = false) {
    if (automatic && !rotationAllowed()) { syncRotation(); return; }
    stopRotation();
    slide = (slide + delta + slides.length) % slides.length;
    const revision = ++slideRevision, next = slides[slide];
    changingSlide = true;
    try {
      await Promise.all(next.images.map(decodeAsset));
      if (revision !== slideRevision) return;
      if (window.CMAMotion) await window.CMAMotion.beforeSwap();
      if (revision !== slideRevision) return;
      $('#hero-art').style.background = next.color;
      $('#slide-title').textContent = next.name;
      $('#slide-subtitle').textContent = next.subtitle;
      $('#slide-link').href = '#project/' + next.key;
      $('#slide-link').setAttribute('aria-label', 'View ' + next.name + ' case study');
      $('#slide-counter').textContent = (slide + 1) + ' / ' + slides.length;
      $$('img', $('#hero-products')).forEach((image, index) => {
        image.src = assets[next.images[index]];
        image.alt = next.alts[index];
        image.dataset.asset = next.images[index];
      });
      if (!automatic) slideStatus.textContent = next.name + ', project ' + (slide + 1) + ' of ' + slides.length;
      window.CMAMotion?.afterSwap();
    } catch {
      // Leave the existing artwork and case link intact when a new image fails.
      if (revision === slideRevision && !automatic) slideStatus.textContent = 'That project could not load. Please try again.';
    } finally {
      if (revision === slideRevision) { changingSlide = false; syncRotation(); }
    }
  }
  let pointerAction = null;
  rotationButton.addEventListener('pointerdown', () => { pointerAction = userPaused || focusPaused; });
  rotationButton.addEventListener('pointercancel', () => { pointerAction = null; });
  rotationButton.addEventListener('click', event => {
    const resume = event.detail > 0 && pointerAction !== null ? pointerAction : userPaused || focusPaused;
    pointerAction = null;
    if (resume) {
      userPaused = false;
      focusPaused = false;
      pointerPaused = false;
    } else userPaused = true;
    syncRotation();
  });
  carouselStage.addEventListener('pointerenter', event => {
    if (event.pointerType === 'mouse') { pointerPaused = true; syncRotation(); }
  });
  carouselStage.addEventListener('pointerleave', () => { pointerPaused = false; syncRotation(); });
  carouselStage.addEventListener('focusin', () => {
    // Keyboard focus stops automatic changes until the visitor explicitly plays.
    focusPaused = true;
    syncRotation();
  });
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(entries => {
      carouselVisible = entries[0].isIntersecting && entries[0].intersectionRatio >= 0.1;
      syncRotation();
    }, { threshold: 0.1 }).observe(carouselStage);
  }
  new MutationObserver(syncRotation).observe(document.documentElement,
    { attributes: true, attributeFilter: ['class'] });
  $$('dialog').forEach(element => new MutationObserver(syncRotation).observe(element,
    { attributes: true, attributeFilter: ['open'] }));
  document.addEventListener('visibilitychange', syncRotation);
  rotationPreference.addEventListener('change', syncRotation);
  window.addEventListener('pagehide', () => { pageSuspended = true; stopRotation(); });
  window.addEventListener('pageshow', () => { pageSuspended = false; syncRotation(); });
  syncRotation();
  // End CM&A carousel.
