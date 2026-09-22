#!/usr/bin/env python3
"""CMA section rhythm and brief-led copy. Run before build.py.

Copy source: CMA WEBSITE COPY 2026.docx, supplied by the client. Retains the
original artwork and all interactive contracts. No external dependencies.
"""
from __future__ import annotations
import argparse
import hashlib
import re
import runpy
from html import escape
from pathlib import Path

OLD = 'studio-sections-v2-20260922'
VERSION = 'studio-rhythm-v3-20260922'

PROJECTS = (
    ('nightsky', 'nightsky', 'Nightsky Gin n’ Tonic', 'Brand naming, identity and packaging', ('nightsky-cherry', 'nightsky-lime', 'nightsky-ale')),
    ('hunters', 'hunters', 'Hunter’s Cider', 'The Big Refresh promotion', ('hunters',)),
    ('gold-blend', 'gold', 'Gold Blend Whisky', 'Packaging and brand evolution', ('gold-standard', 'gold-black', 'gold-nine')),
    ('whitestone', 'whitestone', 'Whitestone Gin', 'Visual identity and positioning', ('whitestone-one', 'whitestone', 'whitestone-two')),
    ('land-of-gold', 'land', 'Gold Blend “Land of Gold”', 'Nationwide consumer promotion', ('land-of-gold',)),
    ('elegance', 'elegance', 'Elegance', 'Brand evolution and packaging design', ('elegance', 'elegance-aloe', 'elegance-cocoa')),
)

def work_section() -> str:
    cards = []
    for key, style, name, scope, assets in PROJECTS:
        images = ''.join('<img src="{{asset:' + asset + '}}" alt="' + escape(name + ' ' + ('campaign artwork' if len(assets) == 1 else 'packaging ' + str(i + 1)), quote=True) + '" loading="lazy">' for i, asset in enumerate(assets))
        if len(assets) == 1:
            visual = images.replace('<img ', '<img class="work-cover" ', 1)
        else:
            visual = '<span class="product-set">' + images + '</span>'
        cards.append('<figure class="project"><button class="work-picture ' + style + '" data-project="' + key + '" aria-label="View ' + escape(name, quote=True) + ' project">' + visual + '<span class="project-cue" aria-hidden="true"><svg class="icon"><use href="#icon-plus"/></svg></span></button><figcaption><h3>' + escape(name) + '</h3><p>' + escape(scope) + '</p></figcaption></figure>')
    return '<section class="section work-section" id="work" aria-labelledby="work-title"><div class="wrap"><div class="work-heading"><div><p class="label">Branding &amp; campaigns</p><h2 id="work-title">What we’ve done.</h2></div><a class="text-link" href="#services">Our services</a></div><div class="portfolio">' + '\n'.join(cards) + '</div></div></section>'

STUDIO = '''<section class="section studio-section" id="studio" aria-labelledby="studio-title"><div class="wrap">
<div class="studio-introduction"><div><p class="label">Since 1986</p><h2 id="studio-title">Who we are.</h2></div><div class="studio-narrative"><p>We are CM&amp;A, a fully Zimbabwean owned advertising and marketing agency. For four decades, we have helped brands grow through communication that adds value.</p><details class="studio-notes"><summary>Our story <svg class="icon" aria-hidden="true"><use href="#icon-plus"/></svg></summary><div><p>Our agency first opened its doors in 1986. A merger with Cameron McKay &amp; Finch in 1987 established CM&amp;A Advertising &amp; Marketing. Today, we are based in Newlands, Harare.</p><h3>Our mission</h3><p>To help brands grow by creating communication that adds value, strengthens brand identity and produces measurable business results.</p><h3>Our vision</h3><p>To be recognised in Zimbabwe for strategic excellence, creative innovation and integrated communication that drives brand growth.</p></div></details></div></div>
<div class="studio-brandline"><p class="label">Our brands over the years</p><div class="brand-names" aria-label="Selected brands"><span>Hunter’s</span><span>Nightsky</span><span>Gold Blend</span><span>Whitestone</span><span>Elegance</span></div></div>
</div></section>'''

FOOTER = '''<footer class="cma-footer" aria-label="Footer"><div class="wrap cma-footer-inner"><a class="footer-credit" href="#home" aria-label="CM&A home">© 2026 CM&amp;A</a><nav class="cma-footer-actions" aria-label="Contact links"><a href="mailto:tendayi@cma.co.zw" aria-label="Email CM&A" title="Email"><svg class="icon" aria-hidden="true"><use href="#icon-email"/></svg></a><a href="https://wa.me/263712407662" target="_blank" rel="noopener noreferrer" aria-label="WhatsApp CM&A" title="WhatsApp"><svg class="icon" aria-hidden="true"><use href="#icon-whatsapp"/></svg></a><a href="https://www.google.com/maps/search/?api=1&amp;query=32%20Aboyne%20Drive%20Newlands%20Harare%20Zimbabwe" target="_blank" rel="noopener noreferrer" aria-label="Find CM&A on Google Maps" title="Google Maps"><svg class="icon" aria-hidden="true"><use href="#icon-map"/></svg></a><button id="privacy-open" type="button">Privacy</button></nav></div></footer>'''

SERVICES = (
    ('Strategy development', 'The thinking that underpins everything we make, grounded in your brand, your category and your market.'),
    ('Media strategy & planning', 'The right message, in the right place, at the right time. Planned for impact and efficiency.'),
    ('Branding & packaging', 'Logo design, corporate identity, packaging, collateral, signage and outdoor design.'),
    ('Multimedia concept development & implementation', 'Big ideas, brought to life consistently across every channel your audience uses.'),
    ('Annual reports', 'Corporate storytelling that presents a year’s performance with clarity and credibility.'),
    ('Media buying', 'Well negotiated placement that makes every dollar of media spend work harder.'),
    ('Direct & relationship marketing', 'Communication that speaks to people, not just markets. Building relationships beyond a single campaign.'),
    ('Below the line communication', 'Targeted communication that gets your brand into people’s hands and into their lives.'),
)

CSS = '''
/* Section rhythm v3. Full-width surfaces; consistent portfolio geometry. */
:root{--surface-work:#eeefe9;--surface-studio:#dce4d9;--surface-services:#fcfbf8;--surface-contact:#e8ddd1;--surface-footer:#262d27}
#home{background:var(--paper)}
#home .hero-after p{max-width:48ch}
#work{width:100%;max-width:none;margin:0;background:var(--surface-work);padding-block:clamp(64px,7vw,104px)}
#work .work-heading{display:flex;align-items:end;justify-content:space-between;gap:32px;margin-bottom:42px}
#work .work-heading .label{font-size:12px;color:#62685d;margin-bottom:18px}
#work .work-heading h2{font-size:clamp(34px,4vw,56px);line-height:1.14;font-weight:600;letter-spacing:-.055em}
#work .work-heading .text-link{font-size:13px;flex-shrink:0}
#work .portfolio{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:44px 32px}
#work .project,#work .project:nth-child(n){grid-column:auto;padding:0;margin:0;min-width:0}
#work .work-picture,#work .work-picture.hunters,#work .work-picture.gold,#work .work-picture.whitestone,#work .work-picture.land,#work .work-picture.elegance{aspect-ratio:3/2;border-radius:8px;width:100%;display:block;padding:0;position:relative;overflow:hidden;isolation:isolate}
#work .work-picture .product-set{position:absolute;inset:12% 15%;display:flex;align-items:center;justify-content:center;gap:6%;transition:transform .5s var(--ease)}
#work .work-picture .product-set img,#work .work-picture .product-set img:first-child,#work .work-picture .product-set img:last-child{height:100%;width:29%;max-width:32%;object-fit:contain;transform:none;margin:0;align-self:center;filter:drop-shadow(0 7px 5px rgba(25,25,20,.09))}
#work .work-picture.elegance .product-set{align-items:end;inset:15% 14%}
#work .work-picture.elegance .product-set img:first-child{height:48%;align-self:end}
#work .work-picture .work-cover{display:block;width:100%;height:100%;object-fit:contain;padding:12px;transition:transform .5s var(--ease)}
#work .work-picture.nightsky{background:#cfdbe3}#work .work-picture.hunters{background:#245b36}#work .work-picture.gold{background:#e4c792}#work .work-picture.whitestone{background:#cbd8d0}#work .work-picture.land{background:#dcca9f}#work .work-picture.elegance{background:#e6cfc3}
#work .work-picture:hover .product-set{transform:scale(1.025)}
#work .work-picture:hover .work-cover{transform:scale(1.015)}
#work .project-cue{position:absolute;right:15px;top:15px;display:grid;place-items:center;width:34px;height:34px;border-radius:50%;background:rgba(252,251,248,.9);color:#283026;opacity:0;transform:translateY(3px);transition:opacity .2s,transform .2s}
#work .work-picture:hover .project-cue,#work .work-picture:focus-visible .project-cue{opacity:1;transform:none}
#work .project-cue .icon{width:16px;height:16px}
#work .project figcaption{display:block;padding:18px 0 0;margin:0;border:0}
#work .project figcaption h3{font-size:clamp(19px,1.8vw,24px);line-height:1.3;letter-spacing:-.035em;font-weight:600}
#work .project figcaption p{font-size:13px;line-height:1.65;color:#606659;margin-top:6px}
#studio{background:var(--surface-studio);padding-block:clamp(64px,7vw,104px);margin:0;color:#29332b}
#studio .studio-introduction{display:grid;grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr);gap:clamp(36px,7vw,110px);margin:0;align-items:start}
#studio .studio-introduction .label{font-size:12px;color:#54614f;margin-bottom:20px}
#studio .studio-introduction h2{font-size:clamp(34px,4vw,56px);line-height:1.14;letter-spacing:-.055em}
#studio .studio-narrative>p{font-size:clamp(17px,1.55vw,21px);line-height:1.8;color:#3e4c3e;max-width:45ch}
#studio .studio-notes{margin-top:20px}
#studio .studio-notes summary{min-height:48px;border-bottom:1px solid #b8c5b4;font-size:13px}
#studio .studio-notes p{color:#43503f;font-size:15px;line-height:1.8}
#studio .studio-notes h3{font-size:15px;letter-spacing:0;line-height:1.4;margin-top:22px}
#studio .studio-notes h3+p{margin-top:9px}
#studio .studio-brandline{display:block;border-top:1px solid #b8c5b4;padding:28px 0 0;margin-top:48px}
#studio .studio-brandline>p{font-size:12px;color:#53614e;margin:0 0 22px}
#studio .brand-names{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:20px;align-items:center;justify-content:space-between}
#studio .brand-names span{font-family:inherit;font-size:clamp(16px,1.65vw,23px);font-weight:600;letter-spacing:-.035em;color:#43513e;white-space:nowrap}
#services{width:100%;max-width:none;background:var(--surface-services);margin:0;padding-block:clamp(64px,7vw,104px)}
#services .capabilities-heading{gap:52px;align-items:center;margin-bottom:38px}
#services .capabilities-heading h2{font-size:clamp(34px,4vw,56px);line-height:1.14;letter-spacing:-.055em}
#services .capabilities-heading h2 span{color:inherit}
#services .capabilities-heading .label{font-size:12px;color:#686b60;margin-bottom:20px}
#services .capabilities-heading>p{font-size:15px;line-height:1.8;max-width:34ch;color:#606659;padding:0;flex-shrink:1}
#services .capability-tabs button{font-size:16px;min-height:62px;padding:16px 0;justify-content:flex-start;font-weight:600;color:#697063}
#services .capability-tabs button[aria-selected=true]{color:#29332b}
#services .capability-tabs button::after{background:#53684d}
#services .capability-panels{min-height:0}
#services .capability-panel{display:block;padding-top:34px;min-height:210px}
#services .capability-deliverables{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:32px;align-items:start;padding:0}
#services #panel-strategy .capability-deliverables{grid-template-columns:repeat(2,minmax(0,1fr))}
#services .capability-item{border:0;padding:0}
#services .capability-item h4{font-size:18px;line-height:1.5;letter-spacing:-.02em;max-width:32ch;margin:0 0 13px;color:#2d352d}
#services .capability-item p{font-size:15px;line-height:1.8;max-width:44ch;color:#606659;margin:0;padding:0}
#contact{background:var(--surface-contact);padding-block:clamp(60px,7vw,96px);color:#2d3029}
#contact .contact-intro .label{font-size:12px;color:#625c51}
#contact .contact-intro h2{font-size:clamp(34px,4vw,54px);line-height:1.14;max-width:530px;margin-block:22px}
#contact .contact-intro>p:not(.label){font-size:16px;color:#625c51}
#contact .form-heading h3{font-size:21px;letter-spacing:-.035em}
#contact .field label{font-size:12px;color:#514f46}
#contact .field input,#contact .field select,#contact .field textarea{font-size:15px;border-color:#a9a394}
#contact .field input::placeholder,#contact .field textarea::placeholder{color:#706c60}
#contact .more-contact{font-size:13px;color:#625c51}
.cma-footer{background:var(--surface-footer);color:#f1f2e9;padding:0;border:0}
.cma-footer .cma-footer-inner{min-height:76px;display:flex;align-items:center;justify-content:space-between;gap:16px;padding-block:12px;border:0}
.cma-footer .footer-credit{display:flex;align-items:center;min-height:44px;white-space:nowrap;font-size:12px;line-height:1.5;color:#d8ded3}
.cma-footer .cma-footer-actions{display:flex;align-items:center;gap:5px;flex-shrink:0}
.cma-footer .cma-footer-actions>a{display:grid;place-items:center;width:44px;height:44px;border:0;border-radius:6px;color:#d8ded3}
.cma-footer .cma-footer-actions>a:hover{background:#3d483c;color:#fff}
.cma-footer .cma-footer-actions .icon{width:18px;height:18px;stroke-width:1.6}
.cma-footer .cma-footer-actions button{padding:0 8px;margin:0;min-height:44px;min-width:48px;font-size:11px;color:#d8ded3;background:transparent}
.whatsapp-float.at-footer{opacity:0;visibility:hidden;pointer-events:none}
@media(max-width:1050px){#studio .studio-introduction{gap:44px}#services .capabilities-heading{flex-direction:row;align-items:start;gap:35px}#services .capabilities-heading>p{max-width:31ch}#services .capability-deliverables{gap:24px}#services .capability-item h4{font-size:16px}}
@media(max-width:760px){#work .work-heading{margin-bottom:30px;align-items:start;gap:22px}#work .work-heading .text-link{display:none}#work .portfolio{grid-template-columns:1fr;gap:32px}#work .project figcaption{padding-top:15px}#work .project figcaption h3{font-size:21px}#work .project figcaption p{font-size:13px}#studio .studio-introduction{grid-template-columns:1fr;gap:27px}#studio .studio-introduction .label{margin-bottom:15px}#studio .studio-narrative>p{font-size:17px;max-width:48ch}#studio .studio-brandline{margin-top:32px;padding-top:25px}#studio .brand-names{display:flex;justify-content:flex-start;flex-wrap:wrap;gap:17px 27px}#studio .brand-names span{font-size:17px}#services .capabilities-heading{display:block;margin-bottom:27px}#services .capabilities-heading>p{margin-top:23px;font-size:15px;max-width:46ch}#services .capability-tabs button{font-size:13px;justify-content:center;letter-spacing:-.025em;min-height:56px}#services .capability-deliverables,#services #panel-strategy .capability-deliverables{grid-template-columns:1fr;gap:22px}#services .capability-panel{padding-top:27px;min-height:0}#services .capability-item+.capability-item{padding-top:21px;border-top:1px solid #deded5}#services .capability-item h4{font-size:17px;margin-bottom:10px}#services .capability-item p{font-size:15px;max-width:48ch}.cma-footer .cma-footer-inner{min-height:70px;gap:10px;padding-block:10px}.cma-footer .footer-credit{font-size:10px}.cma-footer .cma-footer-actions{gap:2px}.cma-footer .cma-footer-actions>a{width:40px;height:44px}.cma-footer .cma-footer-actions button{font-size:10px;padding:0 5px;min-width:40px}}
@media(prefers-reduced-motion:reduce){#work .product-set,#work .work-cover,#work .project-cue{transition:none!important}}
'''

EXTRA_TESTS = '''          backgrounds=page.evaluate("['home','work','studio','services','contact'].map(id=>getComputedStyle(document.getElementById(id)).backgroundColor)")
          check(f'{width}: section shades are distinct',len(set(backgrounds))==5,backgrounds)
          check(f'{width}: section surfaces span viewport',page.evaluate("['work','studio','services','contact'].every(id=>Math.abs(document.getElementById(id).getBoundingClientRect().width-innerWidth)<2)"))
          frames=page.locator('.portfolio .work-picture').evaluate_all("els=>els.map(e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height}})")
          check(f'{width}: consistent artwork proportions',all(abs(r['w']/r['h']-1.5)<0.025 for r in frames))
          check(f'{width}: aligned project rows',width<=760 or all(abs(frames[i]['y']-frames[i+1]['y'])<2 for i in (0,2,4)))
          check(f'{width}: no decorative project numbering',page.locator('.portfolio figcaption>span').count()==0)
          check(f'{width}: no portfolio filler',page.locator('.work-bottom').count()==0 and page.locator('#work-title').inner_text()=='What we’ve done.')
          check(f'{width}: brief-led headline','our clients grow' in page.locator('#services-title').inner_text())
          check(f'{width}: footer one compact row',page.locator('footer').bounding_box()['height']<=82)
          check(f'{width}: footer no repeated address',page.locator('footer address,.cma-footer-address,.cma-footer-wordmark').count()==0)
          check(f'{width}: footer concise text',len(page.locator('footer').inner_text().strip())<35)
          check(f'{width}: icon actions have accessible names',page.locator('footer a[title]').evaluate_all("els=>els.length===3&&els.every(e=>!!e.getAttribute('aria-label'))"))
'''

def replace_once(pattern: str, replacement: str, text: str, label: str) -> str:
    text, count = re.subn(pattern, lambda _: replacement, text, count=1, flags=re.S)
    if count != 1:
        raise ValueError('Expected one ' + label + '; source has changed.')
    return text


def prepare(directory: Path) -> None:
    paths = {name: directory / name for name in ('site.html','site.css','site.js','build.py','test_browser.py')}
    src = {name: path.read_text(encoding='utf-8') for name, path in paths.items()}
    if 'content="studio-rebuild-20260922"' in src['site.html']:
        runpy.run_path(str(directory / 'refine.py'))['prepare'](directory)
        src = {name: path.read_text(encoding='utf-8') for name, path in paths.items()}
    if 'content="' + VERSION + '"' in src['site.html']:
        if VERSION not in src['build.py'] or VERSION not in src['test_browser.py']:
            raise ValueError('Partially prepared v3 source.')
        print('CMA v3 already prepared: ' + VERSION)
        return
    if 'content="' + OLD + '"' not in src['site.html']:
        raise ValueError('Run refine.py before refine_v3.py.')
    html, css, js = src['site.html'], src['site.css'], src['site.js']
    html = replace_once(r'<section class="section wrap" id="work".*?</section>', work_section(), html, 'work section')
    html = replace_once(r'<section class="studio-section" id="studio".*?</section>', STUDIO, html, 'studio section')
    html = replace_once(r'<footer class="cma-footer".*?</footer>', FOOTER, html, 'footer')
    html = html.replace('<section class="capabilities section wrap" id="services" aria-labelledby="services-title">', '<section class="capabilities section" id="services" aria-labelledby="services-title"><div class="wrap">', 1)
    html = replace_once(r'</section>\s*(?=<section class="section contact")', '</div></section>\n', html, 'services inner container')
    html = replace_once(r'<div class="capabilities-heading">.*?</h2></div><p>.*?</p></div>', '<div class="capabilities-heading"><div><p class="label">What we do</p><h2 id="services-title">Ideas that help<br>our clients grow.</h2></div><p>In a changing business environment, one ingredient has stood the test of time for CM&amp;A: ideas.</p></div>', html, 'services introduction')
    html = re.sub(r'<div class="capability-overview">.*?</div>', '', html, flags=re.S)
    html = re.sub(r'<span class="tab-count"[^>]*>.*?</span>', '', html, flags=re.S)
    articles = list(re.finditer(r'<article class="service capability-item">.*?</article>', html, re.S))
    if len(articles) != len(SERVICES):
        raise ValueError('Expected eight services.')
    for match, (title, description) in reversed(list(zip(articles, SERVICES))):
        html = html[:match.start()] + '<article class="service capability-item"><h4>' + escape(title) + '</h4><p>' + escape(description) + '</p></article>' + html[match.end():]
    html = replace_once(r'<title>.*?</title>', '<title>CM&A Advertising &amp; Marketing | Harare, Zimbabwe</title>', html, 'page title')
    html = replace_once(r'<meta property="og:title"[^>]*>', '<meta property="og:title" content="CM&A Advertising &amp; Marketing">', html, 'sharing title')
    html = replace_once(r'<meta property="og:description"[^>]*>', '<meta property="og:description" content="A fully Zimbabwean owned advertising and marketing agency. Strategy, branding, campaigns and media since 1986.">', html, 'sharing description')
    html = replace_once(r'<h1 class="hero-title rise" id="hero-title">.*?</h1>', '<h1 class="hero-title rise" id="hero-title">Ideas.<span>That work.</span></h1>', html, 'hero title')
    html = html.replace('A name. An identity.<br>A night to remember.', 'Brand naming, identity<br>and packaging.')
    html = replace_once(r'<div class="hero-after wrap">.*?</div>', '<div class="hero-after wrap"><p>We help brands grow through communication that adds value.</p><a class="text-link" href="#work">View our work</a></div>', html, 'hero summary')
    html = html.replace('Your next idea starts here', 'Contact us').replace('Tell us what<br>you’re thinking.', 'Need your brand<br>to stand out?').replace('A new brand, a fresh direction, or a challenge to work through together.', 'Let’s talk.').replace('A little about your project', 'Your enquiry')
    categories = {'A brand, from the beginning.':'Brand creation','A promotion with a national stage.':'Big Refresh promotion','A familiar name. A new chapter.':'Brand evolution','It’s all about taste.':'Whitestone Gin rebrand','Rewarding loyalty, nationwide.':'Land of Gold promotion','Everyday care, reconsidered.':'Packaging design'}
    for old, new in categories.items():
        js = js.replace("category:'" + old + "'", "category:'" + new + "'")
    # Only carousel descriptions, not supplied campaign taglines or case studies.
    for old, new in [('A name. An identity. A night to remember.','Brand naming, identity and packaging.'),('A name. An identity.\\nA night to remember.','Brand naming, identity and packaging.')]:
        js = js.replace(old,new)
    for old, new in [('A familiar name. A new chapter.','Packaging and brand evolution.'),('A fresh identity. It’s all about taste.','Visual identity and brand positioning.')]:
        js = js.replace("description:'" + old + "'", "description:'" + new + "'")
    css += '\n' + CSS
    html = html.replace(OLD, VERSION)
    test = src['test_browser.py'].replace(OLD, VERSION)
    needle = "          check(f'{width}: no floating contact overlap'"
    if needle not in test:
        raise ValueError('Expected v2 browser regression tests.')
    test = test.replace(needle, EXTRA_TESTS + needle, 1)
    output = {'site.html':html,'site.css':css,'site.js':js,'build.py':src['build.py'].replace(OLD,VERSION),'test_browser.py':test}
    compile(output['build.py'], 'build.py', 'exec'); compile(test, 'test_browser.py', 'exec')
    for item in ('id="company"','id="service"','id="enquiry-form"','id="privacy-open"'):
        if html.count(item) != 1:
            raise ValueError('Lost unique control ' + item)
    for name, text in output.items():
        paths[name].write_text(text,encoding='utf-8')
        print(name,hashlib.sha256(text.encode()).hexdigest())
    print('CMA_RHYTHM_VERSION ' + VERSION)

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory',type=Path,default=Path(__file__).resolve().parent)
    prepare(parser.parse_args().directory)
