#!/usr/bin/env python3
"""CMA v6: balanced agency section, full mobile logo rows and search/share metadata.
Build after the approved v5 source, or use --existing-release to refine a built v5.
No new business claims, external trackers, forms backend or font is introduced.
"""
from __future__ import annotations
import argparse, base64, hashlib, json, os, re, shutil, subprocess, sys, zipfile
from datetime import date
from html import escape, unescape
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
VERSION = 'studio-polish-seo-v6-20260922'
OLD = 'campaign-motion-v5-20260922'
DEFAULT_URL = 'https://cma-fixed-production.up.railway.app'
TITLE = 'CM&A | Advertising & marketing agency in Harare'
DESCRIPTION = 'A full service wholly owned Zimbabwean advertising agency based in Newlands, Harare, Zimbabwe. Strategy, branding, campaigns and media.'
ARCHIVE = 'CMA-website-v6.zip'
CSS = '''
/* v6: tighter navigation, visible studio information and unclipped logo tracks. */
:root{--cma-header-height:108px}
html{scroll-padding-top:calc(var(--cma-header-height) + 16px)}
.header .nav{height:var(--cma-header-height);min-height:var(--cma-header-height);padding-block:0}
.header .brand img{width:112px;height:96px;flex-shrink:0}
#studio .studio-intro-v6{grid-template-columns:minmax(0,.82fr) minmax(0,1.18fr);gap:clamp(32px,6vw,92px);align-items:start}
#studio .studio-intro-v6 .label{margin-bottom:17px}
#studio .studio-intro-v6 h2{margin:0;font-weight:400}
#studio .studio-intro-v6 .studio-narrative>p{font-size:clamp(24px,2.25vw,32px);line-height:1.5;max-width:39ch;margin:0;color:#193e58}
#studio .studio-details-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0;margin-top:44px;border-top:1px solid #83a9c4;padding-top:30px}
#studio .studio-detail{min-width:0;padding:0 clamp(22px,3vw,42px);border-left:1px solid #8eb1cc}
#studio .studio-detail:first-child{padding-left:0;border-left:0}
#studio .studio-detail:last-child{padding-right:0}
#studio .studio-detail h3{font-family:inherit;font-size:24px;line-height:1.3;font-weight:700;letter-spacing:-.01em;margin:0 0 16px;color:#173b56}
#studio .studio-detail p{font-size:18px;line-height:1.75;margin:0;max-width:36ch;color:#315571}
#studio .profile-brands{margin-top:52px;overflow:visible}
.brand-marquee{--logo-width:154px;--logo-height:108px;--logo-gap:16px;display:flex!important;flex-direction:column;gap:var(--logo-gap);height:auto!important;max-height:none!important;min-height:0;overflow:hidden;padding:4px 0;mask-image:linear-gradient(to right,transparent,#000 20px,#000 calc(100% - 20px),transparent);-webkit-mask-image:linear-gradient(to right,transparent,#000 20px,#000 calc(100% - 20px),transparent)}
.brand-marquee .brand-row{flex:0 0 var(--logo-height);height:var(--logo-height);min-height:var(--logo-height);max-height:none;margin:0;padding:0;border:0;overflow:hidden;box-sizing:border-box}
.brand-marquee .brand-track{height:var(--logo-height);min-height:var(--logo-height);align-items:stretch}
.brand-marquee .brand-strip{height:var(--logo-height);min-height:var(--logo-height);align-items:stretch;margin:0;padding-block:0;box-sizing:border-box}
.brand-marquee .brand-strip li{height:var(--logo-height)!important;min-height:var(--logo-height)!important;max-height:var(--logo-height)!important;aspect-ratio:auto;margin:0;box-sizing:border-box}
.brand-marquee .brand-strip img{height:100%;min-height:0;max-height:100%;object-fit:contain;margin:0;padding:9px;box-sizing:border-box}
.form-bottom{justify-content:flex-start}
@media(max-width:1050px){#studio .studio-detail{padding-inline:23px}#studio .studio-detail p{font-size:17px}#studio .studio-detail h3{font-size:22px}}
@media(max-width:760px){:root{--cma-header-height:88px}.header .brand img{width:92px;height:79px}#studio .studio-intro-v6{grid-template-columns:1fr;gap:22px}#studio .studio-intro-v6 .studio-narrative>p{font-size:25px;max-width:42ch}#studio .studio-details-grid{grid-template-columns:1fr;margin-top:30px;padding-top:0}#studio .studio-detail,#studio .studio-detail:first-child,#studio .studio-detail:last-child{display:grid;grid-template-columns:minmax(100px,.62fr) minmax(0,1.38fr);gap:24px;padding:24px 0;border-left:0;border-bottom:1px solid #8eb1cc}#studio .studio-detail:last-child{border-bottom:0;padding-bottom:0}#studio .studio-detail h3{font-size:22px;margin:0}#studio .studio-detail p{font-size:17px;line-height:1.7;max-width:45ch}#studio .profile-brands{margin-top:36px}.brand-marquee{--logo-width:134px;--logo-height:100px;--logo-gap:12px;mask-image:linear-gradient(to right,transparent,#000 8px,#000 calc(100% - 8px),transparent);-webkit-mask-image:linear-gradient(to right,transparent,#000 8px,#000 calc(100% - 8px),transparent)}.brand-marquee .brand-strip img{padding:7px}}
@media(max-width:430px){#studio .studio-detail,#studio .studio-detail:first-child,#studio .studio-detail:last-child{grid-template-columns:1fr;gap:11px;padding-block:23px}#studio .studio-detail p{font-size:17px}#studio .studio-intro-v6 .studio-narrative>p{font-size:24px}.brand-marquee{--logo-width:126px;--logo-height:94px;--logo-gap:10px}}
'''

def once(pattern, replacement, text, label):
    result,n=re.subn(pattern,lambda _:replacement,text,count=1,flags=re.S)
    if n != 1: raise ValueError('Expected one '+label)
    return result


def studio(html):
    pattern=r'<div class="studio-introduction">.*?</details></div></div>'
    match=re.search(pattern,html,re.S)
    if not match: raise ValueError('Expected the existing studio disclosure')
    block=match[0]
    intro=re.search(r'<div class="studio-narrative"><p>(.*?)</p>',block,re.S)[1]
    details=re.search(r'<details class="studio-notes">.*?</summary><div>(.*?)</div></details>',block,re.S)[1]
    history=re.search(r'^\s*<p>(.*?)</p>',details,re.S)[1]
    mission=re.search(r'<h3>Our mission</h3><p>(.*?)</p>',details,re.S)[1]
    vision=re.search(r'<h3>Our vision</h3><p>(.*?)</p>',details,re.S)[1]
    replacement='<div class="studio-introduction studio-intro-v6"><div class="studio-heading"><p class="label">Since 1986</p><h2 id="studio-title">Who we are.</h2></div><div class="studio-narrative"><p>'+intro+'</p></div></div><div class="studio-details-grid">'
    for heading,copy in [('Our history',history),('Our mission',mission),('Our vision',vision)]:
        replacement+='<article class="studio-detail"><h3>'+heading+'</h3><p>'+copy+'</p></article>'
    replacement+='</div>'
    for copy in (intro,history,mission,vision):
        if copy not in replacement: raise AssertionError('Studio copy lost')
    return html[:match.start()]+replacement+html[match.end():]


def metadata(html, origin, logo, verification=''):
    # Replace, rather than duplicate, all previous search/share metadata.
    html=re.sub(r'<title>.*?</title>','',html,flags=re.S)
    html=re.sub(r'<meta\b[^>]*(?:name|property)=["\'](?:description|robots|googlebot|google-site-verification|theme-color|og:[^"\']+|twitter:[^"\']+)["\'][^>]*>','',html,flags=re.I)
    html=re.sub(r'<link\b[^>]*rel=["\'](?:canonical|icon|shortcut icon|apple-touch-icon)["\'][^>]*>','',html,flags=re.I)
    html=re.sub(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>.*?</script>','',html,flags=re.S)
    root=origin+'/'
    image=origin+'/media/cma-social-v6.jpg'
    tags=['<title>'+escape(TITLE)+'</title>', '<link rel="canonical" href="'+root+'">']
    names={'description':DESCRIPTION,'robots':'index, follow, max-image-preview:large','theme-color':'#bdd9ef','twitter:card':'summary_large_image','twitter:title':TITLE,'twitter:description':DESCRIPTION,'twitter:image':image,'twitter:image:alt':'CM&A Advertising & Marketing, Newlands, Harare, Zimbabwe'}
    if verification: names['google-site-verification']=verification
    props={'og:type':'website','og:locale':'en_ZW','og:site_name':'CM&A Advertising & Marketing','og:title':TITLE,'og:description':DESCRIPTION,'og:url':root,'og:image':image,'og:image:secure_url':image,'og:image:type':'image/jpeg','og:image:width':'1200','og:image:height':'630','og:image:alt':'CM&A Advertising & Marketing, Newlands, Harare, Zimbabwe'}
    for k,v in names.items(): tags.append('<meta name="'+k+'" content="'+escape(v,quote=True)+'">')
    for k,v in props.items(): tags.append('<meta property="'+k+'" content="'+escape(v,quote=True)+'">')
    tags+=['<link rel="icon" href="/favicon.ico" sizes="any">','<link rel="icon" type="image/png" href="/media/cma-icon-192-v6.png" sizes="192x192">','<link rel="apple-touch-icon" href="/media/cma-icon-180-v6.png">']
    graph={'@context':'https://schema.org','@graph':[{'@type':'Organization','@id':root+'#organization','name':'CM&A Advertising & Marketing','alternateName':'CM&A','url':root,'description':DESCRIPTION,'logo':{'@type':'ImageObject','url':origin+'/media/cma-icon-512-v6.png','width':512,'height':512},'image':image,'email':'tendayi@cma.co.zw','telephone':'+263242746867','address':{'@type':'PostalAddress','streetAddress':'32 Aboyne Drive, Newlands','addressLocality':'Harare','addressCountry':'ZW'}},{'@type':'WebSite','@id':root+'#website','url':root,'name':'CM&A Advertising & Marketing','inLanguage':'en-ZW','publisher':{'@id':root+'#organization'}}]}
    tags.append('<script type="application/ld+json">'+json.dumps(graph,ensure_ascii=False).replace('<','\\u003c')+'</script>')
    return html.replace('</head>','\n'.join(tags)+'\n</head>',1)


def social_assets(directory, html, logo, chromium):
    from PIL import Image
    from playwright.sync_api import sync_playwright
    original=Image.open(directory/logo.lstrip('/')).convert('RGBA')
    for size in (180,192,512):
        canvas=Image.new('RGBA',(size,size),'#15384f');mark=original.copy();mark.thumbnail((round(size*.80),round(size*.80)),Image.Resampling.LANCZOS)
        canvas.alpha_composite(mark,((size-mark.width)//2,(size-mark.height)//2));canvas.convert('RGB').save(directory/f'media/cma-icon-{size}-v6.png')
    icon=Image.open(directory/'media/cma-icon-512-v6.png')
    icon.save(directory/'favicon.ico',format='ICO',sizes=[(16,16),(32,32),(48,48),(64,64)])
    fonts='\n'.join(re.findall(r'@font-face\s*\{[^}]*\}',html,re.S))
    logo_uri='data:image/png;base64,'+base64.b64encode((directory/logo.lstrip('/')).read_bytes()).decode()
    # A screenshot of exact branded HTML, not generated or substituted artwork.
    card='<!doctype html><html><head><meta charset="utf-8"><style>'+fonts+'''*{box-sizing:border-box}body{margin:0;width:1200px;height:630px;background:#bdd9ef;color:#15384f;font-family:"CMA Optima",Optima,Arial,sans-serif;position:relative;overflow:hidden}.copy{position:absolute;left:72px;top:65px;width:615px}.top{font-size:24px;margin:0 0 65px}h1{font-size:80px;line-height:1.1;font-weight:400;letter-spacing:-2px;margin:0}p{font-size:26px;line-height:1.5;margin-top:30px}.brand{position:absolute;right:0;top:0;width:430px;height:630px;background:#15384f;display:flex;align-items:center;justify-content:center}.brand img{width:305px;height:auto}.line{position:absolute;bottom:55px;left:72px;width:570px;height:1px;background:#8eafc9}</style></head><body><div class="copy"><p class="top">CM&amp;A Advertising &amp; Marketing</p><h1>Advertising<br>&amp; marketing.</h1><p>Newlands, Harare, Zimbabwe</p></div><div class="line"></div><div class="brand"><img src="'''+logo_uri+'" alt="CM&A"></div></body></html>'
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=chromium,headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
        page=browser.new_page(viewport={'width':1200,'height':630},device_scale_factor=1)
        page.set_content(card,wait_until='load');page.evaluate('document.fonts.ready')
        page.screenshot(path=str(directory/'media/cma-social-v6.jpg'),type='jpeg',quality=91)
        browser.close()


def refine(directory, origin, verification='', chromium='/usr/bin/chromium'):
    html=(directory/'index.html').read_text(encoding='utf-8')
    if OLD not in html: raise ValueError('Expected the approved v5 release')
    html=studio(html)
    html=once(r'(<div class="form-bottom"><button[^>]*type="submit"[^>]*>.*?</button>)<p>.*?</p>',re.search(r'<div class="form-bottom"><button[^>]*type="submit"[^>]*>.*?</button>',html,re.S)[0],html,'enquiry helper note')
    html=once(r'const interval=6000;', 'const interval=4500;',html,'hero dwell interval')
    html=html.replace("const interval=4500;", "const interval=4500;scene.dataset.intervalMs=String(interval);",1)
    html=html.replace('</head>','<style id="cma-v6-style">\n'+CSS+'</style>\n</head>',1).replace(OLD,VERSION)
    manifest=json.loads((directory/'build-manifest.json').read_text())
    logo=manifest['logo_derivative']['file']
    html=metadata(html,origin,logo,verification)
    social_assets(directory,html,logo,chromium)
    (directory/'index.html').write_text(html,encoding='utf-8')
    (directory/'robots.txt').write_text('User-agent: *\nAllow: /\nDisallow: /__qa/\nDisallow: /downloads/\n\nSitemap: '+origin+'/sitemap.xml\n')
    (directory/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>'+origin+'/</loc><lastmod>2026-09-22</lastmod></url></urlset>\n')
    (directory/'404.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Page not found | CM&amp;A</title><style>body{background:#bdd9ef;color:#15384f;font:20px/1.6 Optima,Arial,sans-serif;margin:12vh 8vw}a{color:inherit}</style><h1>Page not found.</h1><p><a href="/">Return to CM&amp;A</a></p></html>')
    manifest.update(version=VERSION,html_sha256=hashlib.sha256(html.encode()).hexdigest())
    manifest['motion']['version']=VERSION;manifest['motion']['hero_interval_ms']=4500
    manifest['refinement']={'studio_all_copy_visible':True,'studio_panels':3,'hero_transition_durations_unchanged':True,'header_height_desktop':108,'header_height_mobile':88,'header_logo_size_unchanged':True,'logo_rows':2,'mobile_logo_rows_explicit_height':True,'edge_fade_desktop_px':20,'edge_fade_mobile_px':8,'enquiry_helper_note_removed':True}
    manifest['seo']={'site_url':origin,'title':TITLE,'canonical':origin+'/','sitemap':origin+'/sitemap.xml','social_image':origin+'/media/cma-social-v6.jpg','social_image_dimensions':[1200,630],'schema_types':['Organization','WebSite'],'google_verification_provided':bool(verification),'search_console_submitted':False}
    (directory/'build-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('CMA_V6_BUILD '+json.dumps({'version':VERSION,'hero_interval_ms':4500,'seo':manifest['seo']}),flush=True)

ARCHIVE_BUILD='''#!/usr/bin/env python3
"""Build the supplied editable site. Optima font files are supplied separately."""
from pathlib import Path
import argparse,re,shutil
p=argparse.ArgumentParser();p.add_argument('--site-url',default="https://cma-fixed-production.up.railway.app");p.add_argument('--google-verification',default='');a=p.parse_args()
root=Path(__file__).resolve().parent;source=root/'source';target=root/'site';target.mkdir(exist_ok=True)
old='https://cma-fixed-production.up.railway.app';new=a.site_url.rstrip('/')
for name in ('index.html','site.css','site.js','robots.txt','sitemap.xml','404.html'):
 s=(source/name).read_text().replace(old,new)
 if name=='index.html' and a.google_verification:
  from html import escape
  s=s.replace('</head>','<meta name="google-site-verification" content="'+escape(a.google_verification,quote=True)+'"></head>')
 (target/name).write_text(s)
print('Built site/. Copy your supplied Optima WOFF2 files into site/fonts/ before external production hosting.')
'''


def package(directory):
    html=(directory/'index.html').read_text()
    # The archive never redistributes font binaries, including embedded copies.
    clean=re.sub(r'@font-face\s*\{[^}]*\}','',html,flags=re.S)
    styles=re.findall(r'<style[^>]*>(.*?)</style>',clean,re.S)
    clean=re.sub(r'<style[^>]*>.*?</style>','',clean,flags=re.S)
    scripts=[]
    def strip_script(m):
        attrs,body=m[1],m[2]
        if 'application/ld+json' in attrs or 'src=' in attrs:return m[0]
        scripts.append(body);return ''
    clean=re.sub(r'<script([^>]*)>(.*?)</script>',strip_script,clean,flags=re.S)
    clean=clean.replace('</head>','<link rel="stylesheet" href="/site.css">\n</head>',1).replace('</body>','<script src="/site.js" defer></script>\n</body>',1)
    font_rules='@font-face{font-family:"CMA Optima";font-style:normal;font-weight:400;src:local("Optima"),url("/fonts/Optima-Regular.woff2") format("woff2");font-display:swap}@font-face{font-family:"CMA Optima";font-style:normal;font-weight:700;src:local("Optima Bold"),url("/fonts/Optima-Bold.woff2") format("woff2");font-display:swap}\n'
    css=font_rules+'\n'.join(styles);js='\n;\n'.join(scripts)
    readme='''# CM&A website v6

This archive contains the current editable HTML, CSS and JavaScript; the complete
site image library; a ready-to-host static folder; favicon and link-preview image;
robots.txt, sitemap.xml, structured data; browser tests; and deployment settings.

## Typography
Optima font binaries and embedded font data are not included. For the same
appearance on a new host, copy your supplied regular and bold Optima webfonts to
site/fonts/Optima-Regular.woff2 and site/fonts/Optima-Bold.woff2. Locally installed
Optima is used when available; otherwise the page has a readable system fallback.
The existing Railway deployment retains the supplied Optima typeface unchanged.

## Editing and preview
Edit source/index.html, source/site.css and source/site.js. Run python3 build.py.
Image files live in site/media/. Run python3 -m http.server 8080 --directory site
and open http://localhost:8080. Use an HTTP server, not a file:// URL.

## Hosting
Upload the contents of site/ to the public web root, or build the included Dockerfile.
When attaching the final domain, run python3 build.py --site-url https://YOUR-DOMAIN
first so canonical, sitemap, organization data and social URLs use that domain.
Do not point these fields at a domain that is not serving this site.

Google Search Console ownership verification and sitemap submission have not
been performed. Add the token from your own property using build.py
--google-verification TOKEN, then submit /sitemap.xml in that verified property.
Preview caches and Google recrawling are controlled by the external platforms.

The form prepares a local draft. It does not send emails or submit to a database.
The decorative note beside the button is removed; the truthful post-submit status
and Open email app action remain. No customer message is sent by the tests.

## Contents
site/ is the editable deployment output. source/ is the same document split into
HTML/CSS/JS. tooling/ contains the v6 update and its browser test suite. qa/ holds
the final build report. MOTION_NOTICES.txt retains third-party notices.
'''
    dest=directory/'downloads';dest.mkdir(exist_ok=True);path=dest/ARCHIVE
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
        z.writestr('CMA-website/README.md',readme)
        z.writestr('CMA-website/build.py',ARCHIVE_BUILD)
        for prefix in ('site','source'):
            z.writestr(f'CMA-website/{prefix}/index.html',clean)
            z.writestr(f'CMA-website/{prefix}/site.css',css)
            z.writestr(f'CMA-website/{prefix}/site.js',js)
            for name in ('robots.txt','sitemap.xml','404.html'):
                z.write(directory/name,f'CMA-website/{prefix}/{name}')
        for file in (directory/'media').rglob('*'):
            if file.is_file() and file.suffix.lower() in ('.png','.jpg','.jpeg','.webp','.gif','.svg'):
                z.write(file,'CMA-website/site/'+str(file.relative_to(directory)))
        z.write(directory/'favicon.ico','CMA-website/site/favicon.ico')
        z.writestr('CMA-website/site/fonts/README.txt','Place your separately supplied Optima-Regular.woff2 and Optima-Bold.woff2 here.\n')
        for name in ('MOTION_NOTICES.txt','build-manifest.json'):
            if (directory/name).exists():z.write(directory/name,'CMA-website/'+name)
        for name in ('refinement_v6.py','test_polish_v6.py'):
            if (HERE/name).exists():z.write(HERE/name,'CMA-website/tooling/'+name)
        for file in (directory/'__qa').glob('*.json'):
            z.write(file,'CMA-website/qa/'+file.name)
        z.writestr('CMA-website/Dockerfile','FROM nginx:alpine\nCOPY site/ /usr/share/nginx/html/\nCOPY nginx.conf /etc/nginx/conf.d/default.conf\nEXPOSE 80\n')
        conf=HERE.parent/'default.conf'
        if conf.exists():z.write(conf,'CMA-website/nginx.conf')
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        for name in z.namelist():
            if name.endswith(('.woff','.woff2','.ttf','.otf')):raise AssertionError('Font binary in archive')
            if name.endswith(('.css','.html','.json','.py')) and re.search(rb'data:(?:font/|application/(?:x-font|font-woff))',z.read(name)):
                raise AssertionError('Embedded font in archive')
    record={'filename':ARCHIVE,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'font_binaries_included':False,'version':VERSION}
    (dest/'manifest.json').write_text(json.dumps(record,indent=2)+'\n')
    print('CMA_V6_ARCHIVE '+json.dumps(record),flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--assets-source',type=Path,default=HERE.parent/'dist'/'index.html');p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--existing-release',action='store_true');p.add_argument('--package-only',action='store_true');p.add_argument('--site-url',default=os.getenv('SITE_URL',DEFAULT_URL));p.add_argument('--google-verification',default=os.getenv('GOOGLE_SITE_VERIFICATION',''));p.add_argument('--chromium',default='/usr/bin/chromium');a=p.parse_args()
    if a.package_only:package(a.output_dir);return
    origin=a.site_url.rstrip('/');parsed=urlparse(origin)
    if parsed.scheme!='https' or not parsed.netloc or parsed.path or parsed.query or parsed.fragment:raise ValueError('SITE_URL must be an HTTPS origin without a path')
    if not a.existing_release:
        subprocess.run([sys.executable,str(HERE/'motion_v5.py'),'--assets-source',str(a.assets_source),'--output-dir',str(a.output_dir)],check=True)
    refine(a.output_dir,origin,a.google_verification,a.chromium)

if __name__=='__main__':main()
