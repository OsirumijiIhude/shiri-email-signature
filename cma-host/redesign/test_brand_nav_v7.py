#!/usr/bin/env python3
"""Check the approved brands and visual scroll-navigation state at nine widths.
Use --inline only for editing environments without browser navigation. Production
runs on an HTTP origin and checks direct links and real navigation as well.
"""
from __future__ import annotations
import argparse,base64,functools,hashlib,http.server,json,mimetypes,re,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
VERSION='brands-nav-v7-20260923'
REMOVE={'illy','terranox','killem','choats','nescafé','kefalos','standard bank'}

def run(directory:Path,chromium:str,inline=False):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*a):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(directory)))
    threading.Thread(target=server.serve_forever,daemon=True).start();origin=f'http://127.0.0.1:{server.server_port}'
    raw=(directory/'index.html').read_text()
    def inline_html():
        text=raw
        for path in sorted(set(re.findall(r'/media/[A-Za-z0-9_./-]+',text)),key=len,reverse=True):
            file=directory/path.lstrip('/')
            if file.is_file():text=text.replace(path,'data:'+str(mimetypes.guess_type(file)[0])+';base64,'+base64.b64encode(file.read_bytes()).decode())
        return text
    rendered=inline_html() if inline else None
    checks=[];errors=[];qa=directory/'__qa';qa.mkdir(exist_ok=True)
    def check(name,ok,detail=None):
        checks.append({'test':name,'passed':bool(ok),**({'detail':detail} if detail is not None else {})})
        if not ok:print('FAIL',name,detail,flush=True)
    def load(page,path=''):
        if inline:page.set_content(rendered,wait_until='load')
        else:page.goto(origin+'/'+path,wait_until='load')
        page.evaluate('document.fonts.ready');page.wait_for_timeout(100)
    def section(page,key):
        page.evaluate("key=>scrollTo(0,document.getElementById(key).getBoundingClientRect().top+scrollY-document.querySelector('.header').getBoundingClientRect().height-8)",key)
        page.wait_for_timeout(180)
    manifest=json.loads((directory/'build-manifest.json').read_text())
    try:
      with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=chromium,args=['--no-sandbox','--disable-dev-shm-usage'])
        for width in (320,360,390,414,600,760,768,1024,1440):
            print("Checking",width,flush=True)
            context=browser.new_context(viewport={'width':width,'height':900},reduced_motion='reduce')
            page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));load(page)
            check(f'{width}: release identity',page.locator('meta[name=cma-build]').get_attribute('content')==VERSION)
            names=page.locator('.brand-original img').evaluate_all('els=>els.map(e=>e.alt)')
            check(f'{width}: 34 unique brands',len(names)==len(set(names))==34)
            check(f'{width}: all requested removals',not REMOVE.intersection(n.casefold() for n in names))
            check(f'{width}: new Graniteside mark',names.count('Graniteside Chemicals')==1)
            check(f'{width}: Stanbic replaces Standard Bank',names.count('Stanbic Bank')==1)
            check(f'{width}: Standard Chartered unaffected','Standard Chartered' in names)
            check(f'{width}: other Nestle marks retained',all(n in names for n in ('Nestlé','Cerevita','Nestlé EveryDay')))
            check(f'{width}: two equal rows',page.locator('.brand-row').count()==2 and all(x.locator('.brand-original img').count()==17 for x in page.locator('.brand-row').all()))
            check(f'{width}: decorative repeats match',page.locator('.brand-row').evaluate_all("rows=>rows.every(r=>JSON.stringify([...r.querySelectorAll('.brand-original img')].map(i=>i.src))===JSON.stringify([...r.querySelectorAll('.brand-duplicate img')].map(i=>i.src)))"))
            check(f'{width}: decorative repeats are inaccessible',page.locator('.brand-duplicate[aria-hidden=true][inert]').count()==2)
            check(f'{width}: four replacement images',page.locator('.brand-original img[data-updated-logo]').count()==4)
            page.locator('.brand-marquee').scroll_into_view_if_needed();page.wait_for_timeout(100)
            check(f'{width}: every logo decodes',page.locator('.brand-original img').evaluate_all('els=>els.every(e=>e.complete&&e.naturalWidth>0)'))
            check(f'{width}: rows remain unclipped',page.locator('.brand-marquee').evaluate("e=>{const b=e.getBoundingClientRect();return [...e.querySelectorAll('.brand-row')].every(r=>{const x=r.getBoundingClientRect();return x.top>=b.top-1&&x.bottom<=b.bottom+1;});}"))
            check(f'{width}: original outdated slide not linked',page.locator('img[src*=profile-brands-slide]').count()==0)
            page.locator('#profile-slide-open').click();page.wait_for_timeout(100)
            check(f'{width}: all-brands view opens',page.locator('#profile-slide-dialog').is_visible())
            check(f'{width}: corrected board loads',page.locator('#profile-slide-dialog>img').evaluate('e=>e.complete&&e.naturalWidth===1920'))
            check(f'{width}: corrected board described honestly','34 brands' in page.locator('#profile-slide-dialog>img').get_attribute('alt'))
            page.keyboard.press('Escape');page.wait_for_timeout(100)
            for direction,sequence in (('down',['work','studio','services','contact']),('up',['contact','services','studio','work'])):
                for key in sequence:
                    section(page,key)
                    check(f'{width}: {direction} {key} desktop current',page.locator('.nav-links a[aria-current=location]').count()==1 and page.locator('.nav-links a[aria-current=location]').get_attribute('href')=='#'+key)
                    check(f'{width}: {direction} {key} mobile current',page.locator('.menu-list a[aria-current=location]').count()==1 and page.locator('.menu-list a[aria-current=location]').get_attribute('href')=='#'+key)
                    if width>760:
                        check(f'{width}: {direction} {key} underline visible',page.locator('.nav-links a[aria-current=location]').evaluate("e=>getComputedStyle(e,'::after').transform==='matrix(1, 0, 0, 1, 0, 0)'&&getComputedStyle(e,'::after').height==='3px'"))
                    check(f'{width}: {direction} {key} contrast visible',page.locator('.nav-links a[aria-current=location]').evaluate("e=>getComputedStyle(e).backgroundColor!=='rgba(0, 0, 0, 0)'&&getComputedStyle(e).color==='rgb(16, 60, 99)'"))
            page.evaluate("scrollTo(0,document.documentElement.scrollHeight)");page.wait_for_timeout(100)
            check(f'{width}: footer keeps Contact active',page.locator('.nav-links a[aria-current=location]').get_attribute('href')=='#contact')
            page.evaluate('scrollTo(0,0)');page.wait_for_timeout(100)
            check(f'{width}: hero clears stale highlight',page.locator('.nav-links a[aria-current=location]').count()==0)
            section(page,'studio');page.evaluate("dispatchEvent(new Event('pageshow'))");page.wait_for_timeout(100)
            check(f'{width}: page restoration keeps state',page.locator('.nav-links a[aria-current=location]').get_attribute('href')=='#studio')
            if width<=760:
                page.locator('#menu-open').click();page.wait_for_timeout(100)
                check(f'{width}: mobile active style visible',page.locator('.menu-list a[aria-current=location]').evaluate("e=>getComputedStyle(e).boxShadow.includes('inset')&&getComputedStyle(e).backgroundColor!=='rgba(0, 0, 0, 0)'"))
                if width==390:page.screenshot(path=str(qa/'nav-menu-v7-390.png'))
                page.keyboard.press('Escape');page.wait_for_timeout(100)
            section(page,'services');page.locator('#tab-creative').click();page.wait_for_timeout(100)
            check(f'{width}: tab-height change retains Services',page.locator('.nav-links a[aria-current=location]').get_attribute('href')=='#services')
            check(f'{width}: no horizontal overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
            if width in (390,1440):
                section(page,'studio');page.screenshot(path=str(qa/f'nav-studio-v7-{width}.png'))
                page.locator('.profile-brands').screenshot(path=str(qa/f'brands-v7-{width}.png'))
            context.close()
        # Test actual link/hash navigation and reload on the HTTP production build.
        if not inline:
            context=browser.new_context(viewport={'width':1440,'height':900},reduced_motion='reduce');page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
            load(page,'#studio');page.wait_for_timeout(250)
            check('Direct studio deep link highlighted',page.locator('.nav-links a[aria-current=location]').get_attribute('href')=='#studio')
            for key in ('work','services','contact','studio'):
                page.locator('.nav-links a[href="#'+key+'"]').click();page.wait_for_timeout(200)
                check('Click scroll highlights '+key,page.locator('.nav-links a[aria-current=location]').get_attribute('href')=='#'+key)
            page.reload(wait_until='load');page.wait_for_timeout(250)
            check('Reload at hash keeps highlight',page.locator('.nav-links a[aria-current=location]').get_attribute('href')=='#studio')
            context.close()
        # Real motion is tested without replacing timers or animation implementations.
        context=browser.new_context(viewport={'width':1440,'height':900},reduced_motion='no-preference');page=context.new_page();load(page)
        page.locator('.brand-marquee').scroll_into_view_if_needed();page.mouse.move(1,1);page.wait_for_timeout(150)
        before=page.locator('.brand-track').evaluate_all('els=>els.map(e=>getComputedStyle(e).transform)');page.wait_for_timeout(700)
        after=page.locator('.brand-track').evaluate_all('els=>els.map(e=>getComputedStyle(e).transform)')
        check('Both updated rows move',all(x!=y for x,y in zip(before,after)))
        check('Opposite-direction looping retained',page.locator('.brand-track').nth(1).evaluate("e=>getComputedStyle(e).animationDirection==='reverse'"))
        context.close();browser.close()
      for row in manifest['brand_revision']['logos']:
        if row['updated']:check('Replacement source checksum '+row['name'],hashlib.sha256((directory/row['url'].lstrip('/')).read_bytes()).hexdigest()==row['sha256'])
      check('Superseded profile slide absent from deployment',not (directory/'media/client/profile-brands-slide.webp').exists())
      check('34-item public manifest',json.loads((directory/'approved-brands.json').read_text())['count']==34)
    except Exception as e:
      errors.append(repr(e));check('Suite completed',False,repr(e));raise
    finally:
      server.shutdown();check('No uncaught browser errors',not errors,errors)
      report={'version':VERSION,'origin':'in-memory original media' if inline else 'local HTTP release server','original_artwork':True,'passed':sum(x['passed'] for x in checks),'failed':sum(not x['passed'] for x in checks),'errors':errors,'results':checks}
      (qa/'brands-nav-v7-report.json').write_text(json.dumps(report,indent=2)+'\n')
      print('CMA_V7_QA '+json.dumps({k:v for k,v in report.items() if k!='results'}),flush=True)
    if report['failed']:raise SystemExit(1)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path);p.add_argument('--chromium',default='/usr/bin/chromium');p.add_argument('--inline',action='store_true');a=p.parse_args();run(a.directory.resolve(),a.chromium,a.inline)
