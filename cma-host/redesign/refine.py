#!/usr/bin/env python3
"""Prepare the CMA studio, capabilities and footer source revision before building.

This is a deterministic source migration, not a runtime DOM replacement. It keeps
all original artwork, portfolio behavior and enquiry fields untouched. Run before
redesign/build.py. Running it a second time is a no-op.
"""
from __future__ import annotations
import argparse
import hashlib
import re
from pathlib import Path

OLD_VERSION = 'studio-rebuild-20260922'
VERSION = 'studio-sections-v2-20260922'

STUDIO = '''<section class="studio-section" id="studio" aria-labelledby="studio-title">
  <div class="wrap">
    <div class="studio-surface">
      <p class="label studio-eyebrow">The studio</p>
      <div class="studio-introduction">
        <h2 id="studio-title">Independent minds.<br><span>Zimbabwean roots.</span></h2>
        <div class="studio-narrative">
          <p>We’re CM&amp;A. Thinkers, designers and communicators bringing a local understanding to every brand we work on.</p>
          <details class="studio-notes">
            <summary>Our story <svg class="icon" aria-hidden="true"><use href="#icon-plus"/></svg></summary>
            <div><p>Our doors first opened in 1986. A merger with Cameron McKay &amp; Finch in 1987 established CM&amp;A Advertising &amp; Marketing. Today, our home is Newlands, Harare.</p>
            <p>We help brands grow through communication that strengthens their identity and adds value to their business. Strategic thinking, creative innovation and integrated communication guide our work.</p></div>
          </details>
        </div>
      </div>
      <dl class="studio-facts">
        <div><dt>Our beginning</dt><dd>Since 1986.</dd></div>
        <div><dt>Our independence</dt><dd>Zimbabwean owned.</dd></div>
        <div><dt>Our home</dt><dd>Newlands, Harare.</dd></div>
      </dl>
    </div>
    <div class="studio-brandline"><p>A few familiar names<br> we’ve worked with.</p><div class="brand-names" aria-label="Selected brands"><span>Hunter’s</span><span>Nightsky</span><span>Gold Blend</span><span>Whitestone</span><span>Elegance</span></div></div>
  </div>
</section>'''

SERVICES = '''<section class="capabilities section wrap" id="services" aria-labelledby="services-title">
  <div class="capabilities-heading"><div><p class="label">What we do</p><h2 id="services-title">A clear idea.<br><span>Every way to bring it to life.</span></h2></div><p>Strategy, creativity and communication.<br> Built around what your brand needs.</p></div>
  <div class="capability-tabs" role="tablist" aria-label="Explore our services" hidden>
    <button type="button" role="tab" id="tab-strategy" aria-controls="panel-strategy" aria-selected="true" tabindex="0">Strategy<span class="tab-count" aria-hidden="true">02</span></button>
    <button type="button" role="tab" id="tab-creative" aria-controls="panel-creative" aria-selected="false" tabindex="-1">Creative<span class="tab-count" aria-hidden="true">03</span></button>
    <button type="button" role="tab" id="tab-communication" aria-controls="panel-communication" aria-selected="false" tabindex="-1">Communication<span class="tab-count" aria-hidden="true">03</span></button>
  </div>
  <div class="capability-panels">
    <section class="capability-panel" id="panel-strategy" aria-labelledby="tab-strategy">
      <div class="capability-overview"><p class="capability-kicker">Strategy</p><h3>Find the<br> right direction.</h3><p>Understand the brand. Ask the right questions. Give the work a clear purpose.</p><a class="text-link" href="#contact">Talk about your brief</a></div>
      <div class="capability-deliverables">
        <article class="service capability-item"><h4>Strategy development</h4><p>Understanding your brand, your category and your market. The thinking that gives every creative decision a purpose.</p></article>
        <article class="service capability-item"><h4>Media strategy &amp; planning</h4><p>Choosing where, when and how your message reaches people, with attention to impact and efficiency.</p></article>
      </div>
    </section>
    <section class="capability-panel" id="panel-creative" aria-labelledby="tab-creative">
      <div class="capability-overview"><p class="capability-kicker">Creative</p><h3>Make it<br> recognisable.</h3><p>Turn the thinking into an identity, a campaign and a story people can connect with.</p><a class="text-link" href="#work">See the work</a></div>
      <div class="capability-deliverables">
        <article class="service capability-item"><h4>Branding &amp; packaging</h4><p>Names, logos, identities, packaging, collateral, signage and outdoor design. A recognisable brand, wherever it appears.</p></article>
        <article class="service capability-item"><h4>Creative campaigns</h4><p>Multimedia ideas developed and implemented consistently across the channels your audience uses.</p></article>
        <article class="service capability-item"><h4>Annual reports</h4><p>Corporate storytelling that presents a year’s performance clearly and credibly.</p></article>
      </div>
    </section>
    <section class="capability-panel" id="panel-communication" aria-labelledby="tab-communication">
      <div class="capability-overview"><p class="capability-kicker">Communication</p><h3>Put it<br> into the world.</h3><p>Get the idea in front of the right people, in the places that matter to them.</p><a class="text-link" href="#contact">Plan your next move</a></div>
      <div class="capability-deliverables">
        <article class="service capability-item"><h4>Media buying</h4><p>Negotiating and placing media to make the most of your budget.</p></article>
        <article class="service capability-item"><h4>Direct &amp; relationship marketing</h4><p>Communication that speaks to people, building relationships beyond a single campaign.</p></article>
        <article class="service capability-item"><h4>Below-the-line communication</h4><p>Targeted activations that get your brand into people’s hands and everyday lives.</p></article>
      </div>
    </section>
  </div>
</section>'''

FOOTER = '''<footer class="cma-footer" aria-label="Studio contact and information"><div class="wrap cma-footer-inner">
  <div class="cma-footer-identity"><a class="cma-footer-wordmark" href="#home" aria-label="CM&A home">CM&amp;A</a><p>© 2026 CM&amp;A</p></div>
  <a class="cma-footer-address" href="https://www.google.com/maps/search/?api=1&amp;query=32%20Aboyne%20Drive%20Newlands%20Harare%20Zimbabwe" target="_blank" rel="noopener noreferrer" aria-label="32 Aboyne Drive, Newlands, Harare. Open Google Maps"><svg class="icon" aria-hidden="true"><use href="#icon-map"/></svg><span>32 Aboyne Drive, Newlands<br>Harare, Zimbabwe</span></a>
  <div class="cma-footer-actions"><a href="mailto:tendayi@cma.co.zw" aria-label="Email CM&A" title="Email CM&A"><svg class="icon" aria-hidden="true"><use href="#icon-email"/></svg></a><a href="https://wa.me/263712407662" target="_blank" rel="noopener noreferrer" aria-label="WhatsApp CM&A" title="WhatsApp CM&A"><svg class="icon" aria-hidden="true"><use href="#icon-whatsapp"/></svg></a><button id="privacy-open" type="button">Privacy</button></div>
</div></footer>'''

CSS = '''/* CMA studio and capabilities: source replacement, revision 2. */
.studio-section{padding:36px 0 0;background:var(--paper)}
.studio-surface{padding:clamp(28px,4.5vw,64px);border-radius:22px;background:#e9ece3;color:#282f28}
.studio-eyebrow{display:flex;align-items:center;gap:10px;color:#59644f}
.studio-eyebrow::before{content:"";width:6px;height:6px;border-radius:50%;background:#687954}
.studio-introduction{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);gap:clamp(28px,5vw,72px);margin-top:30px;align-items:start}
.studio-introduction h2{font-size:clamp(36px,4.1vw,60px);line-height:1.1;font-weight:600;letter-spacing:-.055em}
.studio-introduction h2 span{color:#65705c}
.studio-narrative>p{font-size:17px;line-height:1.85;max-width:38ch;color:#4b5447}
.studio-notes{margin-top:20px;font-size:13px}
.studio-notes summary{display:flex;align-items:center;justify-content:space-between;gap:18px;min-height:48px;border-bottom:1px solid #bdc5b3;cursor:pointer;list-style:none}
.studio-notes summary::-webkit-details-marker{display:none}
.studio-notes .icon{width:17px;height:17px;transition:transform .2s}
.studio-notes[open] .icon{transform:rotate(45deg)}
.studio-notes p{font-size:14px;line-height:1.8;margin-top:18px;color:#4b5447}
.studio-facts{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:28px;margin:52px 0 0;padding-top:25px;border-top:1px solid #c4cbba}
.studio-facts dt{font-size:11px;color:#59644f;margin-bottom:7px}
.studio-facts dd{margin:0;font-size:clamp(16px,1.55vw,22px);letter-spacing:-.035em;font-weight:500}
.studio-brandline{display:grid;grid-template-columns:190px minmax(0,1fr);gap:30px;align-items:center;padding:34px 6px 0}
.studio-brandline>p{font-size:11px;line-height:1.8;color:var(--muted)}
.studio-brandline .brand-names{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));align-items:center;gap:20px}
.studio-brandline .brand-names span{font:600 clamp(14px,1.35vw,19px)/1.4 'Plus Jakarta Sans',Arial,sans-serif;letter-spacing:-.035em;color:#565b50;white-space:nowrap}
.capabilities{padding-block:clamp(78px,8vw,118px)}
.capabilities-heading{display:flex;justify-content:space-between;gap:40px;align-items:end;margin-bottom:42px}
.capabilities-heading .label{color:var(--muted);margin-bottom:22px}
.capabilities-heading h2{font-size:clamp(36px,3.8vw,55px);line-height:1.13;letter-spacing:-.055em;max-width:760px}
.capabilities-heading h2 span{color:#777b70}
.capabilities-heading>p{font-size:13px;line-height:1.8;max-width:29ch;color:var(--muted);padding-bottom:4px;flex-shrink:0}
.capability-tabs{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));border-bottom:1px solid var(--line)}
.capability-tabs button{position:relative;min-width:0;min-height:66px;display:flex;gap:14px;align-items:center;justify-content:space-between;background:transparent;text-align:left;padding:16px 20px;color:#76796e;font-size:16px;letter-spacing:-.025em;font-weight:500;transition:color .2s,background .2s}
.capability-tabs button:first-child{padding-left:0}
.capability-tabs button::after{content:"";position:absolute;bottom:-1px;left:0;right:0;height:2px;background:var(--ink);transform:scaleX(0);transform-origin:left;transition:transform .25s var(--ease)}
.capability-tabs button[aria-selected=true]{color:var(--ink)}
.capability-tabs button[aria-selected=true]::after{transform:scaleX(1)}
.capability-tabs button:hover{color:var(--ink);background:rgba(34,35,32,.025)}
.tab-count{font-size:10px;color:#777b70;letter-spacing:0}
.capability-panel{display:grid;grid-template-columns:minmax(0,.9fr) minmax(0,1.4fr);gap:clamp(36px,7vw,96px);padding:42px 0 0;min-height:345px;align-items:start}
.capability-panel+.capability-panel{border-top:1px solid var(--line);margin-top:30px}
.capabilities-ready .capability-panel{border:0;margin:0}
.capability-panel[hidden]{display:none!important}
.capability-kicker{font-size:11px;color:var(--muted);margin-bottom:18px}
.capabilities-ready .capability-kicker{display:none}
.capability-overview h3{font-size:clamp(31px,3vw,44px);line-height:1.12;letter-spacing:-.05em;margin:0}
.capability-overview>p:not(.capability-kicker){font-size:14px;line-height:1.85;max-width:31ch;color:var(--muted);margin-top:20px}
.capability-overview .text-link{margin-top:22px;font-size:12px;min-height:44px}
.capability-deliverables{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:30px 38px;align-content:start;padding-top:4px}
.capability-item{border:0;padding:0;min-width:0}
.capability-item h4{font-size:17px;line-height:1.45;font-weight:600;letter-spacing:-.025em;margin:0 0 12px}
.capability-item p{font-size:14px;line-height:1.85;color:var(--muted);max-width:35ch;padding:0;margin:0}
.contact{padding-block:clamp(64px,7vw,96px) 58px}
.contact .contact-layout{gap:clamp(40px,7vw,100px)}
.contact .contact-intro h2{font-size:clamp(36px,3.8vw,54px);line-height:1.12}
.contact .email-main{font-size:clamp(18px,1.7vw,24px)}
.contact .more-contact{margin-top:14px}
.cma-footer{background:#eeeae2;color:var(--ink);padding:0 0 12px}
.cma-footer-inner{border-top:1px solid #d1d0c5;padding:25px 0 13px;display:grid;grid-template-columns:1fr 1.15fr auto;align-items:center;gap:30px}
.cma-footer-wordmark{display:inline-flex;align-items:center;min-height:36px;font-size:26px;letter-spacing:-.075em;font-weight:700;line-height:1}
.cma-footer-identity p{font-size:10px;color:#686b60;line-height:1.6;margin-top:3px}
.cma-footer-address{display:inline-flex;gap:12px;align-items:center;justify-self:start;min-height:48px;font-size:11px;line-height:1.65;color:#555b50}
.cma-footer-address .icon{width:20px;height:20px;flex-shrink:0}
.cma-footer-address:hover{color:var(--ink)}
.cma-footer-actions{display:flex;align-items:center;gap:8px}
.cma-footer-actions>a{display:grid;place-items:center;width:44px;height:44px;border-radius:50%;transition:background .2s}
.cma-footer-actions>a:hover{background:#dedfd5}
.cma-footer-actions .icon{width:20px;height:20px}
.cma-footer-actions button{background:transparent;min-height:44px;padding:10px 8px;margin-left:8px;font-size:11px;color:#555b50}
.cma-footer-actions button:hover{text-decoration:underline;text-underline-offset:4px}
.whatsapp-float.at-footer{opacity:0;visibility:hidden;pointer-events:none;transform:translateY(8px)}
@media(min-width:1100px){.capability-panels{min-height:348px}}
@media(max-width:1050px){.studio-introduction{grid-template-columns:1fr 1fr;gap:32px}.studio-introduction h2{font-size:clamp(34px,4.1vw,46px)}.studio-narrative>p{font-size:15px}.studio-brandline{grid-template-columns:150px minmax(0,1fr);gap:20px}.studio-brandline .brand-names{gap:13px}.capabilities-heading{align-items:start;flex-direction:column;gap:22px}.capabilities-heading>p{max-width:42ch}.capabilities-heading>p br{display:none}.capability-panel{gap:38px;grid-template-columns:minmax(0,.8fr) minmax(0,1.2fr)}.capability-deliverables{gap:24px}}
@media(max-width:760px){.studio-section{padding-top:10px}.studio-surface{border-radius:16px;padding:28px}.studio-introduction{grid-template-columns:1fr;gap:26px;margin-top:25px}.studio-introduction h2{font-size:clamp(32px,5.8vw,44px)}.studio-narrative>p{font-size:15px;max-width:50ch}.studio-notes{margin-top:12px}.studio-facts{gap:18px;margin-top:30px;padding-top:22px}.studio-facts dd{font-size:15px;line-height:1.45}.studio-facts dt{font-size:10px}.studio-brandline{display:block;padding-top:24px}.studio-brandline>p{margin-bottom:18px}.studio-brandline>p br{display:none}.studio-brandline .brand-names{display:flex;flex-wrap:wrap;gap:14px 26px}.studio-brandline .brand-names span{font-size:15px}.capabilities{padding-top:72px;padding-bottom:64px}.capabilities-heading{margin-bottom:28px}.capabilities-heading h2{font-size:clamp(34px,6vw,44px)}.capability-tabs button{font-size:13px;min-height:58px;padding:12px 6px;justify-content:center;gap:8px}.capability-tabs button:first-child{padding-left:6px}.tab-count{display:none}.capability-panel{grid-template-columns:1fr;gap:28px;padding-top:30px;min-height:0}.capability-overview h3{font-size:32px}.capability-overview h3 br{display:none}.capability-overview>p:not(.capability-kicker){max-width:45ch;margin-top:15px}.capability-overview .text-link{margin-top:12px}.capability-deliverables{grid-template-columns:repeat(2,minmax(0,1fr));gap:26px}.capability-item h4{font-size:15px}.capability-item p{font-size:14px}.cma-footer-inner{grid-template-columns:1fr auto;gap:18px;padding-top:22px}.cma-footer-actions{justify-self:end;gap:4px}.cma-footer-actions button{margin-left:4px;padding-inline:6px}.cma-footer-address{grid-row:2;grid-column:1/-1;border-top:1px solid #d9d8cd;padding-top:16px;width:100%;min-height:0}.cma-footer{padding-bottom:16px}.contact .contact-intro h2{font-size:40px}}
@media(max-width:430px){.studio-surface{padding:25px 22px}.studio-introduction h2{font-size:32px}.studio-facts{grid-template-columns:1fr;gap:0;margin-top:26px;padding-top:8px}.studio-facts>div{display:flex;align-items:baseline;justify-content:space-between;gap:12px;padding:12px 0;border-bottom:1px solid #cbd1c2}.studio-facts>div:last-child{border:0;padding-bottom:0}.studio-facts dt{margin:0;font-size:11px}.studio-facts dd{font-size:14px;text-align:right}.capabilities-heading h2{font-size:34px}.capability-tabs button{font-size:12px;letter-spacing:-.045em}.capability-deliverables{grid-template-columns:1fr;gap:23px}.capability-item{padding-top:19px;border-top:1px solid var(--line)}.capability-item h4{font-size:17px;margin-bottom:9px}.capability-item p{max-width:43ch}.capability-overview h3{font-size:30px}.cma-footer-actions>a{width:40px}.cma-footer-inner{gap:12px}}
@media(prefers-reduced-motion:reduce){.capability-tabs button::after,.studio-notes .icon{transition:none}}
'''

JS = '''
/* CMA grouped capabilities: progressively enhanced, keyboard-accessible tabs. */
(() => {
  'use strict';
  const root = document.getElementById('services');
  if (!root) return;
  const tablist = root.querySelector('.capability-tabs');
  const tabs = Array.from(tablist.querySelectorAll('[role="tab"]'));
  const panels = tabs.map(tab => document.getElementById(tab.getAttribute('aria-controls')));
  if (panels.some(panel => !panel)) return;
  function activate(index, moveFocus = false) {
    tabs.forEach((tab, i) => {
      const selected = i === index;
      tab.setAttribute('aria-selected', String(selected));
      tab.tabIndex = selected ? 0 : -1;
      panels[i].hidden = !selected;
      panels[i].setAttribute('role', 'tabpanel');
      panels[i].tabIndex = 0;
    });
    if (moveFocus) tabs[index].focus();
  }
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => activate(index));
    tab.addEventListener('keydown', event => {
      let next;
      if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
      else if (event.key === 'ArrowLeft') next = (index + tabs.length - 1) % tabs.length;
      else if (event.key === 'Home') next = 0;
      else if (event.key === 'End') next = tabs.length - 1;
      else return;
      event.preventDefault(); activate(next, true);
    });
  });
  root.classList.add('capabilities-ready');
  tablist.hidden = false;
  activate(0);
  const floating = document.querySelector('.whatsapp-float');
  const footer = document.querySelector('.cma-footer');
  if (floating && footer && 'IntersectionObserver' in window) {
    new IntersectionObserver(entries => {
      const visible = entries[0].isIntersecting;
      floating.classList.toggle('at-footer', visible);
      floating.tabIndex = visible ? -1 : 0;
    }, {threshold: 0}).observe(footer);
  }
})();
'''

TESTS = '''          check(f'{width}: three capability tabs',page.locator('.capability-tabs [role=tab]').count()==3)
          for category, count in (('strategy',2),('creative',3),('communication',3)):
            page.locator('#tab-'+category).click()
            check(f'{width}: {category} panel visible',page.locator('#panel-'+category).is_visible())
            check(f'{width}: {category} selected',page.locator('#tab-'+category).get_attribute('aria-selected')=='true')
            check(f'{width}: one capability panel',page.locator('.capability-panel:visible').count()==1)
            check(f'{width}: {category} services',page.locator('#panel-'+category+' .service').count()==count)
            check(f'{width}: {category} overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
            if width in (390,1440):
              page.locator('#services').scroll_into_view_if_needed()
              page.screenshot(path=str(output/f'services-{category}-{width}.png'))
          page.locator('#tab-strategy').focus()
          page.keyboard.press('ArrowRight')
          check(f'{width}: tabs keyboard next',page.locator('#tab-creative').get_attribute('aria-selected')=='true')
          page.keyboard.press('End')
          check(f'{width}: tabs keyboard end',page.locator('#tab-communication').get_attribute('aria-selected')=='true')
          page.keyboard.press('Home')
          check(f'{width}: tabs keyboard home',page.locator('#tab-strategy').get_attribute('aria-selected')=='true')
          page.keyboard.press('ArrowLeft')
          check(f'{width}: tabs keyboard wrap',page.locator('#tab-communication').get_attribute('aria-selected')=='true')
          page.locator('.studio-notes summary').click()
          check(f'{width}: studio history opens',page.locator('.studio-notes').get_attribute('open') is not None)
          page.locator('.studio-notes summary').click()
          check(f'{width}: studio history closes',page.locator('.studio-notes').get_attribute('open') is None)
          check(f'{width}: footer has no duplicate tagline',page.locator('footer').inner_text().count('Independent')==0)
          check(f'{width}: footer has one privacy',page.locator('footer #privacy-open').count()==1)
          page.locator('footer').scroll_into_view_if_needed()
          page.wait_for_timeout(350)
          check(f'{width}: footer compact',page.locator('footer').bounding_box()['height']<230)
          check(f'{width}: no floating contact overlap',page.locator('.whatsapp-float').evaluate("e=>getComputedStyle(e).visibility==='hidden'"))
          check(f'{width}: footer actions fit',page.locator('.cma-footer-actions').evaluate('e=>e.scrollWidth<=e.clientWidth'))
          if width in (390,1440): page.screenshot(path=str(output/f'footer-{width}.png'))
'''


def once(pattern: str, replacement: str, text: str, label: str) -> str:
    result, n = re.subn(pattern, lambda _: replacement, text, count=1, flags=re.S)
    if n != 1:
        raise ValueError(f'Expected one {label}; source structure has changed.')
    return result


def transform(html: str, css: str, js: str) -> tuple[str, str, str]:
    html = once(r'<section class="section studio" id="studio".*?</section>', STUDIO, html, 'studio section')
    html = once(r'<section class="section wrap" id="services".*?</section>', SERVICES, html, 'services section')
    html = once(r'<footer class="footer">.*?</footer>', FOOTER, html, 'footer')
    html = once(r'<div class="contact-actions">.*?</div>', '', html, 'duplicate contact actions')
    html = html.replace(OLD_VERSION, VERSION)
    css = once(r'/\* The studio is one concise story\. \*/.*?(?=/\* A compact place to start a conversation\. \*/)', '', css, 'old studio and services styles')
    # New, namespaced CSS is placed after the original responsive rules.
    css += '\n' + CSS
    js += '\n' + JS
    return html, css, js


def prepare(directory: Path) -> None:
    names = ('site.html', 'site.css', 'site.js', 'build.py', 'test_browser.py')
    source = {name: (directory/name).read_text(encoding='utf-8') for name in names}
    if f'content="{VERSION}"' in source['site.html']:
        if VERSION not in source['build.py'] or VERSION not in source['test_browser.py']:
            raise ValueError('Partially prepared source; review before rebuilding.')
        print('CMA sections source already prepared: ' + VERSION)
        return
    if OLD_VERSION not in source['site.html']:
        raise ValueError('Unexpected CMA template version.')
    html, css, js = transform(source['site.html'], source['site.css'], source['site.js'])
    test = source['test_browser.py'].replace(OLD_VERSION, VERSION)
    test = once(r"          page\.locator\('\.service summary'\).*?check\(f'\{width\}: one open service'.*?\n", TESTS, test, 'old accordion regression')
    updated = {'site.html':html, 'site.css':css, 'site.js':js,
               'build.py':source['build.py'].replace(OLD_VERSION, VERSION), 'test_browser.py':test}
    compile(updated['build.py'], 'build.py', 'exec')
    compile(updated['test_browser.py'], 'test_browser.py', 'exec')
    if html.count('class="service capability-item"') != 8:
        raise AssertionError('All eight services must be preserved.')
    if html.count('id="privacy-open"') != 1:
        raise AssertionError('There must be one privacy control.')
    for name, text in updated.items():
        (directory/name).write_text(text,encoding='utf-8')
        print(name, hashlib.sha256(text.encode()).hexdigest())
    print('CMA_SECTIONS_VERSION ' + VERSION)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory',type=Path,default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    prepare(args.directory)
