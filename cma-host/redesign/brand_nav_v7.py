#!/usr/bin/env python3
"""Apply the requested brand-list corrections and resilient active navigation.

Logo replacements are faithful crops rendered from CMA updated logos.pdf, page 1.
The source PDF and old company-profile artwork are retained in provenance, not
presented as an up-to-date approved brand list. No third-party marks are redrawn.
"""
from __future__ import annotations
import argparse, base64, hashlib, importlib.util, json, re, shutil, subprocess, sys, zipfile
from html import escape
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent
VERSION='brands-nav-v7-20260923'
OLD='studio-polish-seo-v6-20260922'
REMOVED={'illy','terranox','killem','choats','nescafé','kefalos'}
CSS='''
/* Active section indication is explicit in both navigation layouts. */
.header .nav-links a{color:#3d617b;border-radius:3px;transition:color .16s ease,background-color .16s ease}
.header .nav-links a[aria-current="location"],.header .nav-links a.active{color:#103c63;background-color:rgba(21,74,111,.09);text-shadow:.018em 0 currentColor}
.header .nav-links a::after{content:"";display:block;position:absolute;left:0;right:0;width:100%;height:3px;bottom:3px;background:#1b659b;transform:scaleX(0);transform-origin:left;transition:transform .2s ease}
.header .nav-links a[aria-current="location"]::after,.header .nav-links a.active::after{transform:scaleX(1)}
#menu-dialog .menu-list a{position:relative;padding-inline:12px;transition:color .16s ease,background-color .16s ease}
#menu-dialog .menu-list a[aria-current="location"],#menu-dialog .menu-list a.active{color:#103c63;background:rgba(21,74,111,.09);box-shadow:inset 3px 0 #1b659b;text-shadow:.018em 0 currentColor}
.brand-marquee .brand-strip img[data-updated-logo]{padding:11px;object-fit:contain}
@media(max-width:760px){.brand-marquee .brand-strip img[data-updated-logo]{padding:9px}}
@media(prefers-reduced-motion:reduce){.header .nav-links a,.header .nav-links a::after,#menu-dialog .menu-list a{transition:none}}
'''

def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def once(pattern:str,replacement:str,text:str,label:str)->str:
    value,n=re.subn(pattern,lambda _:replacement,text,count=1,flags=re.S)
    if n!=1:raise ValueError('Expected one '+label)
    return value

def approved_logos(directory:Path):
    source=HERE/'approved_logos_v7'
    new=json.loads((source/'manifest.json').read_text())
    replacements={row['name']:row for row in new['assets']}
    originals=json.loads((HERE/'client_branding'/'manifest.json').read_text())['logos']
    result=[]
    for row in originals:
        name=row['name']
        if name=='illy':
            replacement=replacements['Graniteside Chemicals']
        elif name.casefold() in REMOVED:continue
        elif name=='Standard Bank':replacement=replacements['Stanbic Bank']
        elif name in ('Savanna','Hunter’s'):replacement=replacements[name]
        else:
            result.append(dict(row,width=240,height=170,url='/media/client/'+row['file'],updated=False));continue
        asset=source/replacement['file']
        if sha(asset)!=replacement['sha256']:raise ValueError('Unverified replacement: '+replacement['name'])
        target=directory/'media/client'/replacement['file'];target.parent.mkdir(exist_ok=True,parents=True)
        shutil.copyfile(asset,target)
        result.append(dict(replacement,url='/media/client/'+replacement['file'],updated=True))
    names=[r['name'] for r in result]
    assert len(names)==len(set(names))==34
    assert 'Standard Chartered' in names and 'Nestlé' in names
    assert not REMOVED.intersection(n.casefold() for n in names)
    assert 'Stanbic Bank' in names and 'Standard Bank' not in names
    return result,new,originals

def item(row,duplicate=False):
    return ('<li><img src="'+row['url']+'" alt="'+('' if duplicate else escape(row['name'],quote=True))+'" width="'+str(row['width'])+'" height="'+str(row['height'])+'" loading="eager" decoding="async"'+(' data-updated-logo="true"' if row['updated'] else '')+'></li>')

def board(directory,html,rows,chromium):
    """Create a corrected expanded brand board from the actual approved images."""
    fonts='\n'.join(re.findall(r'@font-face\s*\{[^}]*\}',html,re.S))
    cards=[]
    for row in rows:
        image=directory/row['url'].lstrip('/')
        uri='data:image/webp;base64,'+base64.b64encode(image.read_bytes()).decode()
        cards.append('<div class="tile"><img src="'+uri+'" alt="'+escape(row['name'],quote=True)+'"></div>')
    document='<!doctype html><html><head><meta charset="utf-8"><style>'+fonts+'''*{box-sizing:border-box}body{margin:0;padding:60px 70px;width:1920px;background:#abcde7;color:#16384f;font-family:"CMA Optima",Optima,Arial,sans-serif}header{display:flex;align-items:end;justify-content:space-between;gap:80px;margin-bottom:40px}h1{font-size:58px;line-height:1.15;font-weight:400;letter-spacing:-1px;max-width:1200px;margin:0}header p{font-size:26px;margin:0 0 6px}.grid{display:grid;grid-template-columns:repeat(7,1fr);gap:18px}.tile{height:160px;display:flex;align-items:center;justify-content:center;background:white;border-radius:4px;padding:17px}.tile img{width:100%;height:100%;object-fit:contain}</style></head><body><header><h1>Brands worked with over the years</h1><p>CM&amp;A</p></header><main class="grid">'''+''.join(cards)+'</main></body></html>'
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=chromium,args=['--no-sandbox','--disable-dev-shm-usage'])
        page=browser.new_page(viewport={'width':1920,'height':1100},device_scale_factor=1)
        page.set_content(document,wait_until='load');page.evaluate('document.fonts.ready')
        if not page.locator('img').evaluate_all('els=>els.every(e=>e.complete&&e.naturalWidth>0)'):raise ValueError('Brand board image failed to decode')
        target=directory/'media/client/approved-brands-v7.png'
        page.locator('body').screenshot(path=str(target));browser.close()
    from PIL import Image
    with Image.open(target) as im:
        size=im.size;im.save(target.with_suffix('.webp'),format='WEBP',lossless=True,method=6)
    target.unlink()
    return '/media/client/approved-brands-v7.webp',size

def refine(directory:Path,chromium:str):
    html=(directory/'index.html').read_text()
    if OLD not in html:raise ValueError('Expected the v6 release')
    rows,source,originals=approved_logos(directory)
    groups=(rows[::2],rows[1::2])
    tracks=[]
    for i,group in enumerate(groups):
        tracks.append('<div class="brand-row" tabindex="0" role="group" aria-label="Brand logos, row '+str(i+1)+'"><div class="brand-track"><ul class="brand-strip brand-original profile-logo-grid" aria-label="Brands, row '+str(i+1)+'">'+''.join(item(r) for r in group)+'</ul><ul class="brand-strip brand-duplicate" aria-hidden="true" inert>'+''.join(item(r,True) for r in group)+'</ul></div></div>')
    html=once(r'<div class="brand-marquee"[^>]*>.*?</ul></div></div></div>','<div class="brand-marquee" data-running="false" data-static="true">'+''.join(tracks)+'</div>',html,'two-row brand marquee')
    board_url,size=board(directory,html,rows,chromium)
    # Replace the outdated profile-slide presentation, without editing the original PDF.
    html=once(r'(<dialog id="profile-slide-dialog".*?)(<img [^>]*>)(</dialog>)',re.search(r'<dialog id="profile-slide-dialog".*?(?=<img )',html,re.S)[0]+'<img src="'+board_url+'" width="'+str(size[0])+'" height="'+str(size[1])+'" alt="Updated selection of 34 brands CM&amp;A has worked with">'+'</dialog>',html,'expanded brands image')
    html=html.replace('View profile slide','View all brands').replace('Our brands over the years','Brands worked with over the years').replace('Close brands slide','Close brands')
    controller=(HERE/'nav_v7.js').read_text()
    html=once(r'const sections=\[\'work\'.*?(?=\$\(\'#enquiry-form\'\))',controller+'\n',html,'previous scroll tracker')
    html=html.replace('</head>','<style id="cma-nav-v7">\n'+CSS+'</style>\n</head>',1).replace(OLD,VERSION)
    # Delete superseded image files from the release, but keep all original source assets.
    retained={row['file'] for row in rows}
    removed_assets=[]
    for old in originals:
        if old['file'] not in retained:
            path=directory/'media/client'/old['file']
            if path.exists():path.unlink();removed_assets.append(old['file'])
    (directory/'media/client/profile-brands-slide.webp').unlink(missing_ok=True)
    (directory/'index.html').write_text(html)
    manifest=json.loads((directory/'build-manifest.json').read_text())
    manifest['version']=VERSION;manifest['html_sha256']=hashlib.sha256(html.encode()).hexdigest()
    manifest['motion'].update(version=VERSION,unique_brand_logos=34)
    manifest['client_identity']['version']=VERSION;manifest['client_identity']['logo_count']=34
    manifest['brand_revision']={'source_pdf':source['source_file'],'source_pdf_sha256':source['source_sha256'],'source_page':1,'removed':sorted(REMOVED),'added':['Graniteside Chemicals'],'replaced':{'Standard Bank':'Stanbic Bank'},'updated_artwork':['Savanna','Hunter’s'],'logos':rows,'expanded_board':board_url,'expanded_board_sha256':sha(directory/board_url.lstrip('/')),'superseded_release_assets_removed':removed_assets}
    manifest['navigation_revision']={'desktop_and_mobile':True,'active_attribute':'aria-current=location','strong_active_colour_and_underline':True,'header_measured_dynamically':True,'resize_observer_optional':True,'pageshow_and_hash_navigation_supported':True}
    (directory/'build-manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    (directory/'sitemap.xml').write_text((directory/'sitemap.xml').read_text().replace('2026-09-22','2026-09-23'))
    (directory/'approved-brands.json').write_text(json.dumps({'version':VERSION,'count':34,'brands':[r['name'] for r in rows]},indent=2,ensure_ascii=False)+'\n')
    print('CMA_V7_BUILD '+json.dumps({'version':VERSION,'count':34,'rows':[len(x) for x in groups],'source_pdf_sha256':source['source_sha256']}),flush=True)

def package(directory):
    # Retain the existing font-free portable archive, refreshed to the current release.
    spec=importlib.util.spec_from_file_location('previous_packager',HERE/'refinement_v6.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.VERSION=VERSION;module.ARCHIVE='CMA-website-v7.zip';module.package(directory)
    target=directory/'downloads'/module.ARCHIVE
    import tempfile
    with tempfile.TemporaryDirectory() as temp:
        rebuilt=Path(temp)/target.name
        with zipfile.ZipFile(target) as old,zipfile.ZipFile(rebuilt,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
            for name in old.namelist():
                content=old.read(name)
                if name.endswith('README.md'):
                    content=content.replace(b'website v6',b'website v7')+b'\n## Latest update\nThe approved brand list contains 34 logos. Savanna, Hunter\xe2\x80\x99s, Stanbic Bank and Graniteside Chemicals use the supplied updated PDF. Both menus show the active section.\n'
                z.writestr(name,content)
            for name in ('brand_nav_v7.py','nav_v7.js','test_brand_nav_v7.py'):
                z.write(HERE/name,'CMA-website/tooling/'+name)
            z.write(directory/'approved-brands.json','CMA-website/approved-brands.json')
        shutil.copyfile(rebuilt,target)
    record={'filename':target.name,'bytes':target.stat().st_size,'sha256':sha(target),'font_binaries_included':False,'version':VERSION}
    (directory/'downloads/manifest.json').write_text(json.dumps(record,indent=2)+'\n')
    # The previously shared download URL remains useful, now containing the latest version.
    shutil.copyfile(target,directory/'downloads/CMA-website-v6.zip')
    print('CMA_V7_ARCHIVE '+json.dumps(record),flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--assets-source',type=Path,default=HERE.parent/'index.html');p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--existing-release',action='store_true');p.add_argument('--package-only',action='store_true');p.add_argument('--chromium',default='/usr/bin/chromium');a=p.parse_args()
    if a.package_only:package(a.output_dir);return
    if not a.existing_release:subprocess.run([sys.executable,str(HERE/'refinement_v6.py'),'--assets-source',str(a.assets_source),'--output-dir',str(a.output_dir),'--chromium',a.chromium],check=True)
    refine(a.output_dir,a.chromium)
if __name__=='__main__':main()
