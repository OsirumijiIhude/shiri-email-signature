#!/usr/bin/env python3
"""Build the client-approved Optima and baby-blue CMA release.

Run with --assets-source and --output-dir. Earlier design migrations are applied
first. The client's font stylesheet and page-7 logo artwork are hash-checked;
original portfolio assets remain byte-for-byte unchanged.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import re
import runpy
import shutil
import urllib.request
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLD = 'studio-rhythm-v3-20260922'
VERSION = 'client-optima-blue-v4-20260922'
COPY = 'A full service wholly owned Zimbabwean advertising agency based in Newlands, Harare, Zimbabwe.'
ASSET_MANIFEST_SHA256 = '4a5ad1bf480088f5e7fadcf6c1ca560f435ed4947eedde46066cdfae6702211c'
ASSET_COMMIT = '629f9ff634f24191522f5fb7dfdb2878553f60f9'
ASSET_ORIGIN = 'https://raw.githubusercontent.com/OsirumijiIhude/shiri-email-signature/' + ASSET_COMMIT + '/cma-host/redesign/client_branding/'

CSS = '''
/* Approved client identity: Optima, logo-blue tints and sentence-case interface. */
:root{--paper:#bdd9ef;--ink:#16384f;--muted:#3d5e76;--accent:#285e93;--line:#9bbcd5;--surface-work:#dbeaf6;--surface-studio:#abcde7;--surface-services:#eaf3fa;--surface-contact:#c7e0f2;--surface-footer:#15384f;font-family:"CMA Optima",Optima,Arial,sans-serif;font-synthesis:none}
html{scroll-padding-top:140px}
body{font-family:inherit;font-size:18px;line-height:1.7;color:var(--ink)}
h1,h2,h3,h4{font-family:inherit;letter-spacing:-.018em;font-weight:700}
a,button,input,select,textarea,summary{font-family:inherit;text-transform:none}
::selection{background:#739fc6;color:#102c42}
.header{background:rgba(189,217,239,.97);border-color:#a6c3dc}
.nav{height:122px;gap:32px}
.brand{flex-shrink:0}.brand img{width:112px;height:96px;max-width:none;border-radius:3px;background:#000}
.brand-caption{display:none}
.nav-links{gap:34px}.nav-links a{font-size:17px;color:#31556e}
.nav-links a.active,.nav-links a:hover{color:#102f45}
.nav-right .btn{font-size:15px;padding:12px 24px;min-height:46px}
.btn{font-size:16px;background:#183e5c;color:#fff;font-weight:700;border-radius:4px}
.btn:hover{background:#285a7b}.text-link{font-size:16px}
.label{text-transform:none;letter-spacing:.015em;font-size:15px;font-weight:400}
.hero{background:var(--paper);padding:12px 18px 0}
.scene{background:#b0d4ee;color:#14374f;border-radius:8px;height:calc(100svh - 144px);min-height:690px}
.hero-title{font-size:clamp(76px,8.4vw,122px);font-weight:400;letter-spacing:-.045em;line-height:1;top:82px}
.scene-top{font-size:15px}.scene-top p:last-child{font-size:15px;color:#315771}
.scene-note{max-width:205px;font-size:15px}.scene-note strong{font-size:20px;font-weight:700}.scene-note p{color:#315771;font-size:15px}
.project-open{font-size:15px;border-color:#719cb9}
.scene-tab{font-size:15px;color:#325b76}.scene-tab[aria-pressed=true]{color:#102e44}
.scene-tabs{gap:24px}.scene-controls{gap:7px}.scene-counter{font-size:13px}
.scene-bottom{border-color:#749eba}.round{border-color:#779bb5}
.hero-after{padding-block:30px}.hero-after p{font-size:20px;line-height:1.6}.hero-after .text-link{font-size:16px}
#work .work-heading .label,#studio .studio-introduction .label,#services .capabilities-heading .label{font-size:15px;color:#3d5e76;margin-bottom:17px}
#work .work-heading h2,#studio .studio-introduction h2,#services .capabilities-heading h2{font-size:clamp(39px,4.2vw,62px);font-weight:400;letter-spacing:-.026em;line-height:1.13}
#work .work-heading .text-link{font-size:16px}
#work .project figcaption h3{font-size:clamp(22px,2vw,29px);font-weight:700;letter-spacing:-.01em}
#work .project figcaption p{font-size:16px;color:#3d5e76;margin-top:6px}
#work .work-picture{border-radius:4px}
#work .promotion-art{position:absolute;inset:0;display:block}
#work .promotion-art>img{position:absolute;height:80%;width:27%;object-fit:contain;left:63%;top:10%;filter:drop-shadow(0 9px 6px rgba(37,25,9,.13))}
#work .promotion-copy{position:absolute;left:11%;top:18%;width:49%;color:#3f3020}
#work .promotion-copy small{display:block;font-size:clamp(12px,1.2vw,17px);line-height:1.4;margin-bottom:18px}
#work .promotion-copy strong{display:block;font-size:clamp(34px,4vw,60px);font-weight:400;line-height:1.03;letter-spacing:-.025em}
#studio{color:var(--ink)}
#studio .studio-introduction{grid-template-columns:minmax(0,.8fr) minmax(0,1.2fr)}
#studio .studio-narrative>p{font-size:clamp(22px,2.15vw,30px);line-height:1.5;max-width:37ch;color:#193e58}
#studio .studio-notes summary{font-size:16px;border-color:#80a7c4;min-height:50px}
#studio .studio-notes p{font-size:17px;line-height:1.75;color:#315571}
#studio .studio-notes h3{font-size:18px;color:#16384f}
.profile-brands{margin-top:64px;padding-top:32px;border-top:1px solid #80a7c4}
.profile-brands-heading{display:flex;justify-content:space-between;align-items:center;gap:28px;margin-bottom:24px}
.profile-brands h3{font-size:clamp(24px,2.3vw,33px);font-weight:400;line-height:1.25;letter-spacing:-.015em;max-width:25ch}
.profile-slide-open{display:inline-flex;align-items:center;gap:12px;min-height:46px;background:transparent;padding:8px 0;border-bottom:1px solid #416f91;font-size:16px;flex-shrink:0}
.profile-slide-open .icon{width:16px;height:16px}
.profile-logo-grid{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:10px;list-style:none;padding:0;margin:0}
.profile-logo-grid li{margin:0;display:flex;justify-content:center;align-items:center;background:#fff;min-width:0;aspect-ratio:1.42;border:1px solid rgba(40,84,116,.07);border-radius:3px}
.profile-logo-grid img{display:block;width:100%;height:100%;object-fit:contain;padding:10px;max-width:180px;max-height:130px}
.profile-slide-dialog{inset:20px;margin:auto;width:min(1140px,calc(100% - 40px));height:auto;max-height:calc(100dvh - 40px);overflow:auto;padding:0;border:0;border-radius:6px;background:#eaf3fa;color:#16384f}
.profile-slide-bar{position:sticky;top:0;display:flex;justify-content:space-between;align-items:center;gap:20px;padding:15px 22px;background:#eaf3fa;z-index:2}
.profile-slide-bar h2{font-size:22px;letter-spacing:0;font-weight:400}
.profile-slide-dialog>img{width:100%;height:auto;margin:0;display:block}
#services .capabilities-heading>p{font-size:19px;line-height:1.7;color:#3d5e76;max-width:33ch}
#services .capability-tabs{border-color:#9ebbd1}
#services .capability-tabs button{font-size:20px;font-weight:400;color:#42637a}
#services .capability-tabs button[aria-selected=true]{color:#123954;font-weight:700}
#services .capability-tabs button::after{background:#2f6a9e}
#services .capability-item h4{font-size:22px;line-height:1.35;letter-spacing:-.01em;font-weight:700}
#services .capability-item p{font-size:18px;line-height:1.7;color:#3d5e76}
#contact{color:#16384f}.contact .label,.contact-intro>p,.more-contact{color:#3d5e76;font-size:17px}
.contact .contact-intro h2{font-weight:400;letter-spacing:-.025em;font-size:clamp(40px,4.4vw,62px)}
.contact .email-main{font-size:clamp(22px,2.2vw,31px);border-color:#86a7c0;letter-spacing:0;color:#173f5d}
.contact .more-contact{font-size:16px}.form-heading h3{font-size:27px;font-weight:400;letter-spacing:0}.form-heading span{font-size:13px}
.field label{font-size:15px;color:#315571}.field input,.field select,.field textarea{font-size:17px;border-color:#88abc5;min-height:48px}
.field input::placeholder,.field textarea::placeholder{color:#4b6b82}
.form-note,.form-bottom p{font-size:14px;color:#3d5e76}
.cma-footer{color:#e9f4fc;background:#15384f}
.cma-footer-inner{min-height:72px}.footer-credit{font-size:14px;color:#e9f4fc}
.cma-footer-actions button{font-size:14px;color:#e9f4fc}
.cma-footer-actions a{color:#e9f4fc}.cma-footer-actions a:hover{background:#28526e}
.whatsapp-float{background:#183f5c;color:#fff;border-color:#8eb7d3}
.case-dialog,.privacy-dialog,.menu-dialog{font-family:inherit;background:#eaf3fa;color:#16384f}
.case-title{font-weight:400;letter-spacing:-.025em}.case-copy,.case-story,.case-gallery figcaption{font-size:17px}
@media(max-width:1050px){.nav{gap:20px}.nav-links{gap:24px}.nav-links a{font-size:16px}.scene-tabs{gap:15px}.scene-tab{font-size:14px}.profile-logo-grid{grid-template-columns:repeat(6,minmax(0,1fr))}.profile-logo-grid img{padding:8px}.hero-title{font-size:104px}.scene-note{max-width:175px}.scene-note strong{font-size:18px}}
@media(max-width:760px){html{scroll-padding-top:114px}.nav{height:100px}.brand img{width:92px;height:79px}.nav-right .btn{font-size:14px;min-height:44px;padding-inline:19px}.hero{padding:8px 12px 0}.scene{min-height:660px;height:calc(100svh - 124px);max-height:820px}.hero-title{top:92px;font-size:clamp(69px,12vw,92px);line-height:1;letter-spacing:-.03em}.scene-top{font-size:13px;left:24px;right:24px;top:25px}.scene-top p:last-child{font-size:12px}.scene-art{inset:280px 10% 173px}.scene-note{bottom:100px;left:24px;max-width:calc(100% - 48px);display:flex;gap:20px;align-items:end;justify-content:space-between;width:calc(100% - 48px)}.scene-note strong{font-size:19px}.scene-note p{font-size:13px;max-width:25ch}.scene-note .project-open{font-size:13px;flex-shrink:0;gap:8px}.scene-bottom{left:24px;right:24px;bottom:18px;padding-top:12px}.scene-tabs{display:flex;gap:12px}.scene-tab{font-size:13px}.scene-controls .scene-counter{display:none}.scene-controls{gap:5px}.scene-controls .round{width:38px;height:38px}.hero-after p{font-size:18px}.hero-after .text-link{font-size:15px}#studio .studio-introduction{grid-template-columns:1fr}#studio .studio-narrative>p{font-size:25px}.profile-brands{margin-top:40px;padding-top:28px}.profile-brands-heading{align-items:start;flex-direction:column;gap:12px}.profile-brands h3{font-size:29px;max-width:22ch}.profile-slide-open{font-size:15px}.profile-logo-grid{grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}.profile-logo-grid img{padding:6px}.profile-slide-dialog{width:calc(100% - 24px);max-height:calc(100dvh - 24px);inset:12px}.profile-slide-bar{padding:12px 16px}.profile-slide-bar h2{font-size:18px}#services .capability-tabs button{font-size:17px}#services .capability-item h4{font-size:21px}#services .capability-item p{font-size:17px}.cma-footer-inner{min-height:72px}.footer-credit,.cma-footer-actions button{font-size:13px}}
@media(max-width:480px){.profile-logo-grid{grid-template-columns:repeat(3,minmax(0,1fr))}.profile-logo-grid img{padding:7px}.scene{min-height:665px}.scene-top p:last-child{display:none}.scene-note{bottom:139px;display:block}.scene-note>div{max-width:100%}.scene-note p{display:none}.scene-note .project-open{margin-top:3px}.scene-bottom{flex-direction:column;align-items:stretch;gap:4px}.scene-tabs{display:flex;justify-content:space-between;width:100%;gap:9px}.scene-tab{font-size:13px;white-space:nowrap}.scene-controls{justify-content:flex-end;align-self:end}.scene-art{inset:272px 7% 202px}.hero-title{font-size:74px;top:91px}.hero-after{align-items:start}#work .project figcaption h3{font-size:23px}#services .capability-tabs button{font-size:16px}#services .capabilities-heading>p{font-size:18px}.contact .contact-intro h2{font-size:42px}}
@media(max-width:350px){.scene-tab{font-size:12px}.scene-tab::before{display:none}.scene-note{left:20px}.hero-title{font-size:68px}.nav-right .btn{padding-inline:14px}.profile-logo-grid{gap:6px}.profile-logo-grid img{padding:5px}}
'''

JS = '''
/* The full original profile slide remains available without redrawing any mark. */
(() => {
 const trigger=document.getElementById('profile-slide-open');
 const dialog=document.getElementById('profile-slide-dialog');
 const close=document.getElementById('profile-slide-close');
 if(!trigger||!dialog||!close)return;
 trigger.addEventListener('click',()=>{dialog.showModal();document.body.classList.add('locked');close.focus();});
 function finish(){document.body.classList.toggle('locked',!!document.querySelector('dialog[open]'));trigger.focus({preventScroll:true});}
 close.addEventListener('click',()=>dialog.close());
 dialog.addEventListener('close',finish);
 dialog.addEventListener('click',event=>{if(event.target!==dialog)return;const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();});
})();
'''

TESTS = '''          page.evaluate('document.fonts.ready')
          check(f'{width}: supplied Optima loaded',page.evaluate("Array.from(document.fonts).filter(f=>f.family.includes('CMA Optima')).length===2 && Array.from(document.fonts).filter(f=>f.family.includes('CMA Optima')).every(f=>f.status==='loaded')"))
          check(f'{width}: Optima used across interface',page.locator('body,h1,h2,h3,h4,button,input,select,textarea').evaluate_all("els=>els.every(e=>getComputedStyle(e).fontFamily.includes('CMA Optima'))"))
          check(f'{width}: approved agency copy',page.locator('.studio-narrative>p').inner_text()==COPY)
          check(f'{width}: enlarged actual logo',page.locator('.header .brand img').bounding_box()['width']>=(90 if width<=760 else 110))
          check(f'{width}: no external font dependency',page.locator('link[href*=fonts]').count()==0)
          check(f'{width}: original logo identities',page.locator('.profile-logo-grid img').count()==39)
          check(f'{width}: full whisky name in editable text',page.evaluate("!/(?<![a-z])Gold Blend(?! Whisky)/.test(document.body.innerText)"))
          check(f'{width}: readable brand logo frames',page.locator('.profile-logo-grid li').evaluate_all('els=>els.every(e=>e.getBoundingClientRect().width>=75)'))
          page.locator('#profile-slide-open').click()
          check(f'{width}: original profile slide opens',page.locator('#profile-slide-dialog').is_visible())
          check(f'{width}: original profile slide decodes',page.locator('#profile-slide-dialog>img').evaluate('e=>e.complete&&e.naturalWidth>=1600'))
          check(f'{width}: profile locks background',page.evaluate("document.body.classList.contains('locked')"))
          if width in (390,1440): page.screenshot(path=str(output/f'profile-slide-{width}.png'))
          page.keyboard.press('Escape')
          check(f'{width}: profile closes and restores focus',not page.locator('#profile-slide-dialog').is_visible() and page.locator('#profile-slide-open').evaluate('e=>e===document.activeElement'))
          check(f'{width}: profile unlocks background',not page.evaluate("document.body.classList.contains('locked')"))
          page.locator('#profile-slide-open').evaluate('e=>e.blur()')
          page.evaluate('scrollTo(0,0)')
          page.wait_for_timeout(100)
'''


def once(pattern: str, replacement: str, source: str, label: str) -> str:
    result,count=re.subn(pattern,lambda _:replacement,source,count=1,flags=re.S)
    if count!=1: raise ValueError('Expected exactly one '+label)
    return result


def ensure_assets() -> tuple[Path,dict]:
    directory=HERE/'client_branding'
    directory.mkdir(exist_ok=True)
    manifest_path=directory/'manifest.json'
    if not manifest_path.exists():
        request=urllib.request.Request(ASSET_ORIGIN+'manifest.json',headers={'User-Agent':'CMA-release-builder'})
        with urllib.request.urlopen(request,timeout=30) as response: manifest_path.write_bytes(response.read(50000))
    if hashlib.sha256(manifest_path.read_bytes()).hexdigest()!=ASSET_MANIFEST_SHA256: raise ValueError('Unexpected client asset manifest')
    manifest=json.loads(manifest_path.read_text())
    if manifest['source_page']!=7 or len(manifest['logos'])!=39: raise ValueError('Wrong company profile assets')
    records=manifest['logos']+[manifest['slide'],{'file':manifest['font']['stylesheet'],'sha256':manifest['font']['stylesheet_sha256']}]
    for item in records:
        path=directory/item['file']
        if path.parent!=directory: raise ValueError('Unsafe asset filename')
        if not path.exists():
            request=urllib.request.Request(ASSET_ORIGIN+item['file'],headers={'User-Agent':'CMA-release-builder'})
            with urllib.request.urlopen(request,timeout=30) as response: path.write_bytes(response.read(1000000))
        if hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256']: raise ValueError('Client asset integrity failure: '+item['file'])
    return directory,manifest


def prepare() -> tuple[Path,dict]:
    directory,manifest=ensure_assets()
    if VERSION in (HERE/'site.html').read_text(): return directory,manifest
    runpy.run_path(str(HERE/'refine_v3.py'))['prepare'](HERE)
    html=(HERE/'site.html').read_text();css=(HERE/'site.css').read_text();js=(HERE/'site.js').read_text()
    if OLD not in html: raise ValueError('Unexpected source revision')
    html=once(r'<div class="studio-narrative"><p>.*?</p>','<div class="studio-narrative"><p>'+COPY+'</p>',html,'agency introduction')
    logos=''.join('<li><img src="/media/client/'+item['file']+'" alt="'+escape(item['name'],quote=True)+'" width="240" height="170" loading="lazy"></li>' for item in manifest['logos'])
    gallery='<div class="profile-brands" id="profile-brands"><div class="profile-brands-heading"><h3>Brands worked with<br>over the years</h3><button type="button" id="profile-slide-open" class="profile-slide-open" aria-haspopup="dialog">View profile slide <svg class="icon" aria-hidden="true"><use href="#icon-plus"/></svg></button></div><ul class="profile-logo-grid" aria-label="Brands from our company profile">'+logos+'</ul></div>'
    html=once(r'<div class="studio-brandline">.*?</div>\s*</div>',gallery,html,'historical brands block')
    slide='<dialog id="profile-slide-dialog" class="profile-slide-dialog" aria-labelledby="profile-slide-title"><div class="profile-slide-bar"><h2 id="profile-slide-title">Our brands over the years</h2><button class="round" type="button" id="profile-slide-close" aria-label="Close brands slide"><svg class="icon" aria-hidden="true"><use href="#icon-close"/></svg></button></div><img src="/media/client/'+manifest['slide']['file']+'" width="'+str(manifest['slide']['width'])+'" height="'+str(manifest['slide']['height'])+'" alt="Original company profile page 7: Our brands over the years, featuring 39 logos"></dialog>'
    html=html.replace('</main>','</main>\n'+slide,1)
    cover=re.search(r'(<button class="work-picture land"[^>]*>)(.*?)(</button>)',html,re.S)
    if not cover: raise ValueError('Missing Land of Gold portfolio cover')
    promotion='<span class="promotion-art"><span class="promotion-copy"><small>Gold Blend Whisky</small><strong>Land<br>of Gold</strong></span><img src="{{asset:gold-standard}}" alt="Gold Blend Whisky bottle" loading="lazy"></span><span class="project-cue" aria-hidden="true"><svg class="icon"><use href="#icon-plus"/></svg></span>'
    html=html[:cover.start(2)]+promotion+html[cover.end(2):]
    html=re.sub(r'<link[^>]+href="https://fonts\.(?:googleapis|gstatic)\.com[^>]*>','',html)
    html=once(r'<meta name="description"[^>]*>','<meta name="description" content="'+COPY+'">',html,'meta description')
    html=once(r'<meta property="og:description"[^>]*>','<meta property="og:description" content="'+COPY+'">',html,'sharing description')
    html=html.replace('Advertising &amp; Marketing<br>Harare, Zimbabwe','Advertising &amp; marketing<br>Harare, Zimbabwe')
    html=re.sub(r'\bGold\s+Blend\b(?!\s+Whisky)','Gold Blend Whisky',html,flags=re.I)
    js=re.sub(r'\bGold\s+Blend\b(?!\s+Whisky)','Gold Blend Whisky',js,flags=re.I)
    for old,new in [('#e8edbe','#b0d4ee'),('#ebd1ac','#c2def1'),('#d4e1df','#a5cbe6')]: js=js.replace(old,new)
    css=css.replace("'Plus Jakarta Sans',Inter,Arial,sans-serif",'"CMA Optima",Optima,Arial,sans-serif').replace("'Plus Jakarta Sans',Arial,sans-serif",'"CMA Optima",Optima,Arial,sans-serif')
    css=(directory/manifest['font']['stylesheet']).read_text()+'\n'+css+'\n'+CSS
    html=html.replace(OLD,VERSION);js+='\n'+JS
    test=(HERE/'test_browser.py').read_text().replace(OLD,VERSION).replace("'Gold Blend'","'Gold Blend Whisky'")
    test=once(r"          check\(f'\{width\}: five accurate brands'.*?\n",'',test,'superseded five-brand assertion')
    test=test.replace('from playwright.sync_api import sync_playwright','from playwright.sync_api import sync_playwright\nCOPY = '+repr(COPY))
    needle="          check(f'{width}: reduced motion starts paused'"
    if needle not in test: raise ValueError('Missing browser regression insertion point')
    test=test.replace(needle,TESTS+needle,1)
    test=test.replace("e.offsetTop-90","e.offsetTop-document.querySelector('.header').offsetHeight-8")
    compile(test,'test_browser.py','exec')
    for name,data in [('site.html',html),('site.css',css),('site.js',js),('test_browser.py',test),('build.py',(HERE/'build.py').read_text().replace(OLD,VERSION))]:
        (HERE/name).write_text(data,encoding='utf-8')
    return directory,manifest


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets-source',type=Path,default=HERE.parent/'dist'/'index.html')
    parser.add_argument('--output-dir',type=Path,default=HERE.parent/'release')
    args=parser.parse_args()
    directory,client=prepare()
    spec=importlib.util.spec_from_file_location('cma_release_build',HERE/'build.py')
    builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
    manifest=builder.build(args.assets_source,args.output_dir,HERE/'site.html')
    target=args.output_dir/'media'/'client';target.mkdir(parents=True,exist_ok=True)
    for record in client['logos']+[client['slide']]: shutil.copyfile(directory/record['file'],target/record['file'])
    manifest['client_identity']={'version':VERSION,'font_family':'Optima','font_source_sha256':client['font']['source_sha256'],'logo_count':39,'profile_source_page':7,'profile_source_sha256':client['profile_sha256'],'profile_slide_sha256':client['slide']['sha256'],'approved_agency_copy':COPY,'section_palette':'logo-derived baby blue tints'}
    (args.output_dir/'build-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('CMA_CLIENT_IDENTITY '+json.dumps(manifest['client_identity']))

if __name__=='__main__': main()
