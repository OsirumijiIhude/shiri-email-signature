#!/usr/bin/env python3
"""Apply CM&A's sourced motion and plain-language copy to HTML, without a network.

Default: update canonical index.html and an existing dist/index.html in place.
A deployment mirror may use --file path/to/cma.html. Artwork/asset bytes are kept.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

COPY = {
    'Independent thinking. Zimbabwean heart. CM&A Advertising & Marketing brings four decades of strategy, creativity, branding and media expertise to ambitious brands. Based in Newlands, Harare.':
        'CM&A Advertising & Marketing. Branding, campaigns and media from Newlands, Harare. Zimbabwean owned, established in 1986.',
    'Great brands start with a great idea. Strategy, creativity and communication, made in Zimbabwe since 1986.':
        'Branding, campaigns and media. CM&A Advertising & Marketing, Harare, Zimbabwe. Established in 1986.',
    'Independent thinking. Since 1986.': 'Harare, Zimbabwe. Since 1986.',
    'Four decades of strategy, creativity and communication. Made in Zimbabwe. Built to make a difference.':
        'Branding, campaigns and media, from our office in Newlands, Harare.',
    'Explore our work ': 'View our work ',
    'Meet CM&amp;A ': 'About CM&amp;A ',
    'A nationwide moment of refreshment.': 'A nationwide promotional campaign.',
    'A new chapter for a Zimbabwean classic.': 'Packaging and campaign design.',
    'A fresh identity for Whitestone Gin.': 'Brand identity and positioning.',
    'Rewarding Gold Blend loyalty at scale.': 'A nationwide promotion.',
    'A contemporary world for Elegance.': 'Packaging across the range.',
    '<p>Explore the projects to see the thinking and the work behind each brand.</p>': '',
    'We are CM&amp;A. A fully Zimbabwean-owned advertising agency bringing strategic thinking and creative ambition together.':
        'We’re a Zimbabwean owned advertising agency in Newlands, Harare.',
    'Our story began in 1986. A strategic merger with Cameron McKay &amp; Finch in 1987 gave us the name CM&amp;A Advertising &amp; Marketing, and a platform to help shape some of Zimbabwe’s most iconic brands.':
        'The agency opened in 1986. A merger with Cameron McKay &amp; Finch the following year gave us the name CM&amp;A Advertising &amp; Marketing.',
    'Today, from our home in Newlands, Harare, we deliver end-to-end marketing communication solutions. Fully accredited by ZAAPA and ADMA, we have spent four decades turning brand ambition into measurable market results.':
        'We work across strategy, creative development, branding and media. CM&amp;A is accredited by ZAAPA and ADMA.',
    'Years of<br>great ideas.<small>1986 — 2026<br>And still thinking ahead.</small>':
        'Years in<br>advertising.<small>1986 to 2026</small>',
    'A defining merger. CM&amp;A Advertising &amp; Marketing is born.':
        'A merger with Cameron McKay &amp; Finch. The CM&amp;A name begins.',
    'Four decades of creativity. Fully Zimbabwean owned.': 'Zimbabwean owned. Based in Newlands, Harare.',
    'We exist to help brands grow by creating communication that adds value, strengthens brand identity, and produces measurable business results by applying our collective creative and strategic talents to deliver effective marketing and advertising services.':
        'To help brands grow through creative thinking and effective advertising.',
    'To be a recognized advertising and marketing agency in Zimbabwe, renowned for strategic excellence, creative innovation, and consistently delivering integrated communication solutions that drive measurable brand growth and business impact.':
        'To be recognised in Zimbabwe for our strategy, creative work and the results we deliver for clients.',
    'We have partnered with national and regional brands across diverse sectors. A selection of the names we’ve helped build over the years.':
        'Some of the brands we’ve worked with over the years.',
    'Our business environment keeps changing. One ingredient has stood the test of time: <strong>ideas.</strong> Ideas that help our clients grow, build lasting relationships, and make a difference to their bottom line.':
        'From the initial brief to production and media placement.',
    'The thinking that underpins everything we make, grounded in your brand, your category, and your market.':
        'A strategy based on your brand, your market and what you need to achieve.',
    'Big ideas, brought to life consistently across every channel your audience uses.':
        'Campaign concepts and creative work across print, broadcast and digital media.',
    'The right message, in the right place, at the right time, planned for maximum impact and efficiency.':
        'Choosing the channels, placements and timing for your campaign.',
    'Smart, well-negotiated placement that makes every dollar of media spend work harder.':
        'Negotiating and booking media placements within your budget.',
    'Communication that speaks to people, not just markets, building relationships that last beyond a single campaign.':
        'Direct communication that helps you build and maintain customer relationships.',
    'Logo development and design, corporate identity material, banners and collateral, signage and outdoor design, building brands with a consistent, unmistakable identity.':
        'Names, logos, corporate identity, packaging, signage and outdoor design.',
    'Targeted, activation-led communication designed to get your brand into people’s hands, and into their lives.':
        'Targeted promotions, activations and communication materials.',
    'Corporate storytelling that presents a year’s performance with clarity, credibility and polish.':
        'Design and production of clear, carefully presented annual reports.',
    'Need your brand<br>to stand out?': 'Let’s talk.',
    '<p>Need your brand to stand out and make a difference? Let’s talk.</p>': '',
    'Find our studio': 'Visit our office',
    'Zimbabwean owned. Proudly based in Harare.': 'Newlands, Harare, Zimbabwe.',
    'Your privacy matters.': 'Privacy',
    'Nightsky Cherry packaging': 'Nightsky range packaging',
    'alt="Nightsky Cherry"': 'alt="Nightsky range packaging"',
    'Let’s talk about it ': 'Contact CM&amp;A ',
}

CASES = {
    'hunters': dict(title='Hunter’s Big Refresh', category='Nationwide promotion / Hunter’s Cider',
        services='Concept development, campaign design and promotional execution',
        story='We developed and ran Hunter’s Big Refresh promotion across Zimbabwe. Prizes included trips to Zanzibar, PlayStation 5 consoles and smartphones.',
        gallery=[['hunters', 'Big Refresh campaign artwork'], ['hunters-event', 'Promotion artwork'], ['hunters-social', 'Social campaign artwork']]),
    'nightsky': dict(title='Nightsky Gin n’ Tonic', category='Brand creation / Nightsky',
        services='Naming, identity, packaging and positioning',
        story='We developed the Nightsky name, logo and packaging, along with the line “Give Me The Night.” The work established an identity for the ready to drink gin and tonic range.',
        gallery=[['nightsky-poster', 'Give Me The Night campaign artwork'], ['nightsky-lime', 'Nightsky packaging'], ['nightsky-cherry', 'Nightsky range packaging'], ['nightsky-ale', 'Nightsky can design']]),
    'gold-blend': dict(title='Gold Blend Whisky', category='Brand evolution / Gold Blend',
        services='Brand strategy, packaging and campaign development',
        story='We updated packaging across the Gold Blend range and developed a campaign around “Mix In The Right Circles, With The Right Blend.” The work focused on friendship, good company and responsible drinking.',
        gallery=[['gold-poster', 'Gold Blend campaign artwork'], ['gold-black', 'Gold Blend Black packaging'], ['gold-nine', 'Gold Blend No. 9'], ['gold-event', 'Brand launch artwork']]),
    'whitestone': dict(title='Whitestone Gin', category='Rebrand / Whitestone',
        services='Visual identity, positioning and rebranding',
        story='We redesigned Whitestone Gin’s visual identity and positioning, with the line “It’s All About Taste.”',
        gallery=[['whitestone', 'Whitestone Gin packaging'], ['whitestone-one', 'Whitestone Gin bottle'], ['whitestone-two', 'Whitestone Gin range']]),
    'land-of-gold': dict(title='Land of Gold', category='Nationwide promotion / Gold Blend',
        services='Promotion concept and campaign management',
        story='We developed and managed a nationwide Gold Blend promotion, with a residential stand as the main prize.',
        gallery=[['land-of-gold', 'Still from the Land of Gold promotion film'], ['gold-standard', 'Gold Blend Whisky'], ['gold-black', 'Gold Blend Black']]),
    'elegance': dict(title='Elegance', category='Packaging / Elegance',
        services='Brand development and packaging design',
        story='We refreshed packaging for the Elegance range of petroleum jellies, lotions, creams and shower gels. We also developed packaging for Dr Klin bathroom cleaners and Maxi-Smooth Camphor Creams.',
        gallery=[['elegance-aloe', 'Elegance Aloe Vera lotion'], ['elegance', 'Elegance cocoa body cream'], ['elegance-cocoa', 'Elegance cocoa lotion'], ['elegance-pink', 'Elegance packaging'], ['dr-klin', 'Dr Klin bathroom cleaner packaging']]),
}

CAROUSEL = '''  // CM&A carousel: revision guard keeps rapid clicks in order.
  let slide=0, slideRevision=0;
  async function changeSlide(delta){
    slide=(slide+delta+slides.length)%slides.length;
    const revision=++slideRevision, s=slides[slide];
    if(window.CMAMotion) await window.CMAMotion.beforeSwap();
    if(revision!==slideRevision)return;
    $('#hero-art').style.background=s.color;
    $('#slide-title').textContent=s.name;
    $('#slide-subtitle').textContent=s.subtitle;
    $('#slide-link').href='#project/'+s.key;
    $('#slide-link').setAttribute('aria-label','View '+s.name+' case study');
    $('#slide-counter').textContent=String(slide+1)+' / 3';
    $$('img',$('#hero-products')).forEach((img,i)=>{img.src=assets[s.images[i]];img.alt=s.alts[i];});
    window.CMAMotion?.afterSwap();
  }
  // End CM&A carousel.
'''

BOOT = '''<script id="cma-motion-boot">
(()=>{try{if(!matchMedia('(prefers-reduced-motion: reduce)').matches&&!sessionStorage.getItem('cma-intro-seen')&&!location.hash){document.documentElement.classList.add('cma-intro');window.__cmaIntroStart=performance.now();window.__cmaIntroTimer=setTimeout(()=>{document.documentElement.classList.remove('cma-intro');document.getElementById('cma-intro')?.remove();},2600);}}catch{/* A blocked storage API must never block the website. */}})();
</script>'''

INTRO = '''<!-- cma-intro:start -->
<div id="cma-intro" aria-label="CM&amp;A introduction"><div class="cma-intro-inner"><img class="cma-intro-logo" data-asset="logo" alt="CM&amp;A Advertising and Marketing" width="170" height="148"><div class="sk-fold" aria-hidden="true"><div class="sk-fold-cube"></div><div class="sk-fold-cube"></div><div class="sk-fold-cube"></div><div class="sk-fold-cube"></div></div></div><button id="cma-skip-intro" type="button">Skip intro</button></div>
<!-- cma-intro:end -->'''

def apply(html: str) -> str:
    if 'id="hero-title"' not in html or 'id="asset-library"' not in html:
        raise ValueError('Expected the existing CM&A source, not a replacement template.')
    for identifier, tag in [('cma-motion-style', 'style'), ('cma-motion-boot', 'script'), ('cma-motion', 'script'), ('cma-motion-licenses', 'script')]:
        html = re.sub(rf'<{tag}\b[^>]*\bid="{identifier}"[^>]*>.*?</{tag}>\s*', '', html, flags=re.S)
    html = re.sub(r'<!-- cma-intro:start -->.*?<!-- cma-intro:end -->\s*', '', html, flags=re.S)
    for old, new in COPY.items():
        html = html.replace(old, new)
    html, count = re.subn(r'  const cases=\{.*?\n  \};', '  const cases=' + json.dumps(CASES, ensure_ascii=False, indent=2) + ';', html, count=1, flags=re.S)
    if not count:
        # Subsequent runs see JSON generated by the preceding line.
        html, count = re.subn(r'  const cases=\{.*?\n\};', '  const cases=' + json.dumps(CASES, ensure_ascii=False, indent=2) + ';', html, count=1, flags=re.S)
    if count != 1:
        raise ValueError('Case-study source changed; review before modifying it.')
    if '// CM&A carousel:' in html:
        html = re.sub(r'  // CM&A carousel:.*?  // End CM&A carousel\.\n', lambda _: CAROUSEL, html, count=1, flags=re.S)
    else:
        html, count = re.subn(r'  let slide=0;\n  function changeSlide[^\n]+\n', lambda _: CAROUSEL, html, count=1)
        if count != 1:
            raise ValueError('Carousel source changed; review before modifying it.')
    html = re.sub(r'<span class="num">\d{2}</span>', '', html)
    # Old decorative CSS is inert, but no diagonal-arrow glyphs may survive.
    html = re.sub(r'<span class="(?:arrow|open-icon|big-arrow|asterisk|section-no|number|tag)"[^>]*>.*?</span>', '', html, flags=re.S)
    for glyph in ('↗', '↖', '↘', '↙', '✳'):
        html = html.replace(glyph, '')
    css = (HERE / 'motion.css').read_text(encoding='utf-8')
    js = (HERE / 'motion.js').read_text(encoding='utf-8')
    licenses = (HERE / 'THIRD_PARTY_LICENSES.txt').read_text(encoding='utf-8')
    html = html.replace('</head>', '<style id="cma-motion-style">\n' + css + '</style>\n' + BOOT + '\n</head>', 1)
    html = html.replace('<body>', '<body>\n' + INTRO, 1)
    html = html.replace('</body>', '<script id="cma-motion">\n' + js + '</script>\n<script type="text/plain" id="cma-motion-licenses">' + licenses + '</script>\n</body>', 1)
    return html


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--file', type=Path, help='Update one existing deployment mirror instead.')
    args = parser.parse_args()
    paths = [args.file] if args.file else [ROOT / 'index.html', ROOT / 'dist' / 'index.html']
    for path in paths:
        if not path.exists():
            if args.file or path.name == 'index.html' and path.parent == ROOT:
                raise FileNotFoundError(path)
            continue
        before = path.read_text(encoding='utf-8')
        after = apply(before)
        # The original image registry is preserved byte for byte.
        registry = r'<template id="asset-library">.*?</template>'
        if re.search(registry, before, re.S).group(0) != re.search(registry, after, re.S).group(0):
            raise AssertionError('The client artwork registry must not change.')
        if before != after:
            path.write_text(after, encoding='utf-8')
        print(f'CM&A motion/copy: {path} ({len(after.encode())} bytes)')

if __name__ == '__main__':
    main()
