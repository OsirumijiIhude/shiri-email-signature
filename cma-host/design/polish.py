#!/usr/bin/env python3
"""Polish the existing CM&A document, preserving every client artwork byte.

python3 cma/design/polish.py           # finish + polish source and portable build
python3 cma/design/polish.py --file X  # finish + polish one existing host mirror
No network, external packages, new artwork or asset conversion is required.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import re
import runpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
NAV = (
    '<a href="#work">What We’ve Done</a><a href="#about">Who We Are</a>'
    '<a href="#brands">Our Brands</a><a href="#services">What We Do</a>'
    '<a href="#contact">Contact Us</a>'
)
CONTROLS = '''<button class="slide-toggle" id="slide-toggle" type="button" aria-label="Pause automatic project rotation" data-paused="false"><svg class="pause-icon" viewBox="0 0 10 12" aria-hidden="true" focusable="false"><path d="M1 1h2v10H1zM7 1h2v10H7z"/></svg><svg class="play-icon" viewBox="0 0 10 12" aria-hidden="true" focusable="false"><path d="M2 1l7 5-7 5z"/></svg><span id="slide-toggle-label">Pause</span></button>'''
LINEWORK = '''<!-- cma-linework:start --><svg class="cma-linework" viewBox="0 0 144 96" aria-hidden="true" focusable="false"><path pathLength="1" d="M8 27H98V87H8Z"/><path pathLength="1" d="M27 18H117V78H27Z"/><path pathLength="1" d="M46 9H136V69H46Z"/></svg><!-- cma-linework:end -->'''

SOCIAL_FOOTER = r'''<footer class="footer cma-footer"><div class="wrap"><div class="footer-main"><a class="footer-brand" href="#home" aria-label="CM&A, back to top">CM<span>&amp;</span>A</a><p class="footer-kicker">Independent thinking.<br>Zimbabwean heart.</p><div class="footer-contact-links"><a class="footer-action" href="mailto:tendayi@cma.co.zw" aria-label="Email CM&A"><span class="footer-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M3 5h18v14H3z"/><path d="m4 7 8 6 8-6"/></svg></span><span>Email</span></a><a class="footer-action" href="https://wa.me/263712407662?text=Hi%20CM%26A%2C%20I%27d%20like%20to%20discuss%20a%20project." target="_blank" rel="noopener noreferrer" aria-label="Chat with CM&A on WhatsApp"><span class="footer-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M20.5 11.6a8.5 8.5 0 0 1-12.6 7.5L3 20.5l1.4-4.7A8.5 8.5 0 1 1 20.5 11.6Z"/><path d="M8.2 7.9c.2-.4.4-.4.7-.4h.5c.2 0 .4.1.5.4l.8 1.8c.1.3.1.5-.1.7l-.6.8c-.2.2-.1.4 0 .6.7 1.3 1.8 2.3 3.1 3 .2.1.4.1.6-.1l.9-1.1c.2-.2.4-.3.7-.2l1.9.9c.3.1.4.3.4.6 0 .4-.2 1.2-.8 1.7-.6.6-1.4.8-2.4.6-1.1-.2-2.6-.7-4.4-2.3-1.5-1.3-2.5-3-2.8-4-.3-1-.1-1.9.3-2.5Z"/></svg></span><span>WhatsApp</span></a><a class="footer-action" href="https://www.google.com/maps/search/?api=1&amp;query=32%20Aboyne%20Drive%20Newlands%20Harare%20Zimbabwe" target="_blank" rel="noopener noreferrer" aria-label="Open CM&A in Google Maps"><span class="footer-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M12 21s6-5.2 6-11a6 6 0 1 0-12 0c0 5.8 6 11 6 11Z"/><circle cx="12" cy="10" r="2.3"/></svg></span><span>Google Maps</span></a></div></div><div class="footer-bottom"><p>© 2026 CM&amp;A Advertising &amp; Marketing</p><p>32 Aboyne Drive, Newlands, Harare</p><div><button id="privacy-open">Privacy</button><a href="#home">Back to top</a></div></div></div></footer>'''

WHATSAPP_FLOAT = r'''<a class="whatsapp-float" href="https://wa.me/263712407662?text=Hi%20CM%26A%2C%20I%27d%20like%20to%20discuss%20a%20project." target="_blank" rel="noopener noreferrer" aria-label="Chat with CM&A on WhatsApp"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.5 11.6a8.5 8.5 0 0 1-12.6 7.5L3 20.5l1.4-4.7A8.5 8.5 0 1 1 20.5 11.6Z"/><path d="M8.2 7.9c.2-.4.4-.4.7-.4h.5c.2 0 .4.1.5.4l.8 1.8c.1.3.1.5-.1.7l-.6.8c-.2.2-.1.4 0 .6.7 1.3 1.8 2.3 3.1 3 .2.1.4.1.6-.1l.9-1.1c.2-.2.4-.3.7-.2l1.9.9c.3.1.4.3.4.6 0 .4-.2 1.2-.8 1.7-.6.6-1.4.8-2.4.6-1.1-.2-2.6-.7-4.4-2.3-1.5-1.3-2.5-3-2.8-4-.3-1-.1-1.9.3-2.5Z"/></svg></a>'''

REGISTRY = re.compile(r'<template id="asset-library">.*?</template>', re.S)
OLD_SCROLL = re.compile(r'  let scheduled=false;function onScroll\(\).*?onScroll\(\);route\(\);', re.S)


def replace_once(pattern: str, replacement: str, html: str, label: str) -> str:
    result, count = re.subn(pattern, lambda _: replacement, html, count=1, flags=re.S)
    if count != 1:
        raise ValueError(f'Expected one {label}; refusing to patch a different document.')
    return result


def apply(html: str) -> str:
    registry = REGISTRY.search(html)
    if not registry or 'id="hero-title"' not in html:
        raise ValueError('Expected the existing CM&A site with its artwork registry.')
    for tag, identifier in [('style', 'cma-editorial-style'), ('script', 'cma-editorial')]:
        html = re.sub(rf'<{tag} id="{identifier}">.*?</{tag}>\s*', '', html, flags=re.S)
    html = re.sub(r'<!-- cma-linework:start -->.*?<!-- cma-linework:end -->', '', html, flags=re.S)
    html = replace_once(r'<div class="nav-links">.*?</div>', '<div class="nav-links">' + NAV + '</div>', html, 'desktop navigation')
    mobile = re.search(r'<div id="mobile-nav" class="mobile-nav">(.*?)</div>', html, re.S)
    if not mobile:
        raise ValueError('Mobile navigation was not found.')
    email = re.search(r'<a class="mobile-email".*?</a>', mobile.group(1), re.S)
    if not email:
        raise ValueError('Preserve the existing mobile email contact.')
    html = html[:mobile.start()] + '<div id="mobile-nav" class="mobile-nav">' + NAV + email.group(0) + '</div>' + html[mobile.end():]
    # The finishing layer gives the carousel a stable replacement boundary.
    carousel = (HERE / 'carousel.js').read_text(encoding='utf-8').rstrip() + '\n'
    html = replace_once(r'  // CM&A carousel:.*?  // End CM&A carousel\.\n', carousel, html, 'carousel controller')
    if OLD_SCROLL.search(html):
        html = OLD_SCROLL.sub('  // Section tracking is owned by cma-editorial.\n  route();', html, count=1)
    elif '// Section tracking is owned by cma-editorial.' not in html:
        raise ValueError('The old navigation handler changed; review before replacing it.')
    if 'id="slide-toggle"' not in html:
        html = replace_once(r'<div class="slide-nav">', '<div class="slide-nav">' + CONTROLS, html, 'carousel controls')
    html = html.replace('id="slide-counter" aria-live="polite"', 'id="slide-counter" aria-live="off"')
    if 'id="slide-status"' not in html:
        html = replace_once(r'<div class="slide-controls">', '<span class="slide-progress" aria-hidden="true"><span></span></span><span class="sr-only" id="slide-status" aria-live="polite" aria-atomic="true"></span><div class="slide-controls">', html, 'carousel progress')
    html = html.replace('<div class="hero-art-stage" aria-roledescription=', '<div class="hero-art-stage" role="group" aria-roledescription=')
    # Shorter headings preserve the service scope while avoiding cramped blocks.
    html = html.replace('<h3>Multi-Media Concept Development &amp; Implementation</h3>', '<h3>Campaign Development</h3>')
    html = html.replace('<h3>Direct / Relationship Marketing</h3>', '<h3>Direct &amp; Relationship Marketing</h3>')
    # Repair the original malformed option markup without changing service choices.
    options = ['Strategy Development', 'Creative Campaigns', 'Media Strategy &amp; Planning',
               'Media Buying', 'Relationship Marketing', 'Branding &amp; Packaging',
               'Below-The-Line Communication', 'Annual Reports']
    select = '<select id="service" name="service"><option value="A conversation">Select a service</option>'
    select += ''.join('<option>' + item + '</option>' for item in options) + '</select>'
    html = replace_once(r'<select id="service" name="service">.*?</select>', select, html, 'service selector')
    marker = '</div><div class="service-list">'
    if html.count(marker) != 1:
        raise ValueError('Expected the original service lead/list boundary.')
    html = html.replace(marker, LINEWORK + marker, 1)

    # Keep the client list honest: product lines are not presented as standalone brands.
    for non_brand in ('Dr Klin', 'Maxi-Smooth'):
        html = re.sub(
            rf'<a class="client-mark"[^>]*>\\s*<span(?: class="classic")?>{re.escape(non_brand)}</span>\\s*</a>',
            '', html, count=1, flags=re.S
        )
    html = replace_once(r'<footer class="footer">.*?</footer>', SOCIAL_FOOTER, html, 'compact footer')
    if 'class="whatsapp-float"' not in html:
        html = html.replace('</body>', WHATSAPP_FLOAT + '\\n</body>', 1)

    css = (HERE / 'polish.css').read_text(encoding='utf-8')
    javascript = (HERE / 'polish.js').read_text(encoding='utf-8')
    html = html.replace('</head>', '<style id="cma-editorial-style">\n' + css + '</style>\n</head>', 1)
    html = html.replace('</body>', '<script id="cma-editorial">\n' + javascript + '</script>\n</body>', 1)
    if REGISTRY.search(html).group(0) != registry.group(0):
        raise AssertionError('The client artwork registry must remain byte-for-byte identical.')
    return html


def prepare(path: Path) -> None:
    before = path.read_text(encoding='utf-8')
    finishing = runpy.run_path(str(HERE / 'finish.py'))['apply']
    after = apply(finishing(before))
    if REGISTRY.search(before).group(0) != REGISTRY.search(after).group(0):
        raise AssertionError('Preparation must not change client artwork.')
    path.write_text(after, encoding='utf-8')
    print(f'Prepared {path}: {len(after.encode("utf-8")):,} bytes; client artwork preserved')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--file', type=Path)
    args = parser.parse_args()
    paths = [args.file] if args.file else [ROOT / 'index.html', ROOT / 'dist' / 'index.html']
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(f'Missing existing CM&A document: {path}')
    for path in paths:
        prepare(path)


if __name__ == '__main__':
    main()
