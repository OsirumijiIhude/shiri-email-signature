#!/usr/bin/env python3
"""Release checks on the actual CMA v6 build, including timed motion and metadata.
No contact message is sent. All media and fonts are the real supplied assets.
"""
from __future__ import annotations
import argparse,functools,http.server,json,re,threading,time,urllib.request,xml.etree.ElementTree as ET
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
VERSION='studio-polish-seo-v6-20260922'
COPY='A full service wholly owned Zimbabwean advertising agency based in Newlands, Harare, Zimbabwe.'

def run(directory, executable='/usr/bin/chromium'):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*_):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(directory)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    origin=f'http://127.0.0.1:{server.server_port}'
    qa=directory/'__qa';qa.mkdir(exist_ok=True)
    checks=[];errors=[]
    def check(label,value,detail=None):
        checks.append({'test':label,'passed':bool(value),**({'detail':detail} if detail is not None else {})})
        if not value:print('FAIL '+label+' '+str(detail),flush=True)
    def nav(page):
        result=page.goto(origin,wait_until='networkidle',timeout=45000)
        page.evaluate('document.fonts.ready')
        return result
    def still(page):page.wait_for_timeout(120)
    try:
      with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=executable,headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
        for width in (320,360,390,414,600,760,768,1024,1440):
          ctx=browser.new_context(viewport={'width':width,'height':900},reduced_motion='reduce')
          page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
          check(f'{width}: HTTP homepage',nav(page).status==200)
          check(f'{width}: v6 identity',page.locator('meta[name=cma-build]').get_attribute('content')==VERSION)
          check(f'{width}: no horizontal overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
          check(f'{width}: one main heading',page.locator('h1').count()==1)
          check(f'{width}: six original projects',page.locator('.portfolio .project').count()==6)
          check(f'{width}: eight services retained',page.locator('.service').count()==8)
          check(f'{width}: Optima loaded',page.evaluate("Array.from(document.fonts).filter(f=>f.family.includes('CMA Optima')).length===2&&Array.from(document.fonts).filter(f=>f.family.includes('CMA Optima')).every(f=>f.status==='loaded')"))
          check(f'{width}: shorter header',page.locator('.nav').bounding_box()['height']==(88 if width<=760 else 108))
          b=page.locator('.header .brand img').bounding_box();h=page.locator('.header').bounding_box()
          check(f'{width}: logo unchanged size',b['width']==(92 if width<=760 else 112) and b['height']==(79 if width<=760 else 96))
          check(f'{width}: logo fits header',b['y']>=h['y'] and b['y']+b['height']<=h['y']+h['height'])
          check(f'{width}: approved copy unchanged',page.locator('.studio-narrative>p').inner_text()==COPY)
          check(f'{width}: no studio disclosure',page.locator('#studio details').count()==0 and page.locator('#studio summary').count()==0)
          check(f'{width}: all three studio articles visible',page.locator('.studio-detail:visible').count()==3)
          check(f'{width}: studio has history mission vision',page.locator('.studio-detail h3').all_text_contents()==['Our history','Our mission','Our vision'])
          check(f'{width}: studio paragraphs not truncated',page.locator('.studio-detail p').evaluate_all("els=>els.every(e=>e.scrollHeight<=e.clientHeight+1&&getComputedStyle(e).webkitLineClamp==='none')"))
          if width>760:
              boxes=[x.bounding_box() for x in page.locator('.studio-detail').all()]
              check(f'{width}: studio columns balanced',max(b['y'] for b in boxes)-min(b['y'] for b in boxes)<1 and max(b['width'] for b in boxes)-min(b['width'] for b in boxes)<1)
          check(f'{width}: enquiry helper removed',page.locator('.form-bottom p').count()==0)
          check(f'{width}: company and service retained',page.locator('#company').count()==1 and page.locator('#service option').count()==9)
          check(f'{width}: two logo rows',page.locator('.brand-row').count()==2)
          check(f'{width}: all 39 real logos',page.locator('.brand-original img').count()==39)
          check(f'{width}: repeated logos accessible once',page.locator('.brand-duplicate[aria-hidden=true][inert]').count()==2)
          page.locator('.profile-brands').evaluate("e=>scrollTo(0,e.getBoundingClientRect().top+scrollY-document.querySelector('.header').offsetHeight-12)")
          still(page)
          geometry=page.locator('.brand-marquee').evaluate('''e=>{const b=e.getBoundingClientRect();return [...e.querySelectorAll('.brand-row')].map(r=>{const x=r.getBoundingClientRect(),t=r.querySelector('.brand-strip li').getBoundingClientRect();return {top:x.top-b.top,bottom:b.bottom-x.bottom,height:x.height,logo:t.height,margin:getComputedStyle(r).marginTop,padding:getComputedStyle(r).paddingTop,viewBottom:x.bottom};});}''')
          check(f'{width}: neither logo row clipped',all(r['top']>=-1 and r['bottom']>=-1 and abs(r['height']-r['logo'])<=1 for r in geometry),geometry)
          check(f'{width}: no inherited mobile row margin',all(r['margin']=='0px' and r['padding']=='0px' for r in geometry))
          check(f'{width}: both rows fully in viewport',all(r['viewBottom']<=900 for r in geometry))
          check(f'{width}: reduced edge fade',page.locator('.brand-marquee').evaluate("e=>getComputedStyle(e).maskImage.includes(innerWidth<=760?'8px':'20px')"))
          check(f'{width}: paused reduced motion logos',page.locator('.brand-marquee').get_attribute('data-running')=='false')
          page.locator('img').evaluate_all("els=>els.forEach(e=>e.loading='eager')")
          page.wait_for_function('Array.from(document.images).every(e=>e.complete)',timeout=30000)
          broken=page.locator('img').evaluate_all('els=>els.filter(e=>!e.naturalWidth).map(e=>e.alt)')
          check(f'{width}: all supplied image assets decode',not broken,broken)
          if width in (390,768,1440):
              page.locator('.profile-brands').screenshot(path=str(qa/f'brands-v6-{width}.png'))
              page.locator('#studio').screenshot(path=str(qa/f'studio-v6-{width}.png'))
          for category,count in [('strategy',2),('creative',3),('communication',3)]:
              page.locator('#tab-'+category).click();still(page)
              check(f'{width}: {category} panel opens',page.locator('#panel-'+category).is_visible())
              check(f'{width}: {category} services readable',page.locator('#panel-'+category+' .service').count()==count)
              check(f'{width}: only one panel active '+category,page.locator('.capability-panel:visible').count()==1)
          page.locator('#tab-strategy').focus();page.keyboard.press('End')
          check(f'{width}: keyboard service tabs',page.locator('#tab-communication').get_attribute('aria-selected')=='true')
          page.locator('#profile-slide-open').click()
          check(f'{width}: original profile slide opens',page.locator('#profile-slide-dialog').is_visible())
          check(f'{width}: original profile slide decodes',page.locator('#profile-slide-dialog>img').evaluate('e=>e.complete&&e.naturalWidth>=1600'))
          page.keyboard.press('Escape');still(page)
          check(f'{width}: profile closes and unlocks',not page.locator('#profile-slide-dialog').is_visible() and not page.evaluate("document.body.classList.contains('locked')"))
          for key in ('nightsky','hunters','gold-blend','whitestone','land-of-gold','elegance'):
              page.locator('.portfolio [data-project="'+key+'"]').click()
              page.wait_for_function("Array.from(document.querySelectorAll('#case-gallery img')).every(i=>i.complete&&i.naturalWidth>0)")
              check(f'{width}: {key} original gallery',page.locator('#case-dialog').is_visible() and page.locator('#case-gallery img').count()>=2)
              page.keyboard.press('Escape');still(page)
          for index,key in enumerate(('nightsky','gold-blend','whitestone')):
              page.locator(f'[data-slide="{index}"]').click()
              page.wait_for_function("key=>document.getElementById('scene').dataset.slideKey===key",arg=key)
              check(f'{width}: slide '+key,page.locator('#scene-project').get_attribute('data-project')==key)
          check(f'{width}: hero dwell is 4500ms',page.locator('#scene').get_attribute('data-interval-ms')=='4500')
          page.locator('#name').fill('Browser QA');page.locator('#email').fill('test@example.com');page.locator('#company').fill('QA company')
          page.locator('#service').select_option(label='Branding & packaging');page.locator('#message').fill('Validation only. Nothing is sent.')
          page.locator('.form-bottom button[type=submit]').click()
          check(f'{width}: enquiry remains truthful',page.locator('#enquiry-ready').is_visible() and 'Nothing has been sent' in page.locator('#enquiry-status').inner_text())
          check(f'{width}: company in prepared draft','QA company' in page.locator('#enquiry-copy').input_value())
          check(f'{width}: open-email link still works',page.locator('#open-email').get_attribute('href').startswith('mailto:tendayi@cma.co.zw?'))
          check(f'{width}: compact footer retained',page.locator('footer').bounding_box()['height']<140)
          check(f'{width}: footer has three contact icons',page.locator('footer nav a').count()==3)
          page.locator('#privacy-open').click();check(f'{width}: privacy opens',page.locator('#privacy-dialog').is_visible())
          page.keyboard.press('Escape');still(page)
          if width<=760:
              page.evaluate('scrollTo(0,0)');page.locator('#menu-open').click()
              check(f'{width}: mobile menu opens',page.locator('#menu-dialog').is_visible())
              page.keyboard.press('Escape');still(page)
              check(f'{width}: mobile menu closes',not page.locator('#menu-dialog').is_visible())
          check(f'{width}: no stray scroll lock',not page.evaluate("document.body.classList.contains('locked')"))
          check(f'{width}: title singleton',page.locator('title').count()==1 and page.title()=='CM&A | Advertising & marketing agency in Harare')
          check(f'{width}: canonical absolute',page.locator('link[rel=canonical]').get_attribute('href').startswith('https://'))
          check(f'{width}: one description',page.locator('meta[name=description]').count()==1)
          check(f'{width}: Open Graph dimensions',page.locator('meta[property="og:image:width"]').get_attribute('content')=='1200' and page.locator('meta[property="og:image:height"]').get_attribute('content')=='630')
          check(f'{width}: social image absolute',page.locator('meta[property="og:image"]').get_attribute('content').startswith('https://'))
          check(f'{width}: Twitter large image',page.locator('meta[name="twitter:card"]').get_attribute('content')=='summary_large_image')
          graph=json.loads(page.locator('script[type="application/ld+json"]').text_content())
          check(f'{width}: organization and website schema',{x['@type'] for x in graph['@graph']}=={'Organization','WebSite'})
          check(f'{width}: no fabricated verification',page.locator('meta[name=google-site-verification]').count()==0)
          if width in (390,1440):
              page.evaluate('scrollTo(0,0)');still(page);page.screenshot(path=str(qa/f'hero-v6-{width}.png'))
          ctx.close()
        # Timed tests use real elapsed time, not timer overrides.
        ctx=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='no-preference');page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        nav(page);page.mouse.move(1,1);start=time.monotonic()
        page.wait_for_function("document.querySelector('#scene').dataset.slideKey==='gold-blend'",timeout=5600)
        elapsed=time.monotonic()-start
        check('Autoplay reaches second slide within shorter interval',elapsed<5.6,round(elapsed,3))
        check('Gold theme is preserved',page.locator('#scene').evaluate("e=>e.style.backgroundColor==='rgb(231, 198, 135)'"))
        page.wait_for_function("document.querySelector('#scene').dataset.slideKey==='whitestone'",timeout=5700)
        check('Botanical third theme preserved',page.locator('#scene').evaluate("e=>e.style.backgroundColor==='rgb(185, 215, 204)'"))
        page.wait_for_function("document.querySelector('#scene').dataset.slideKey==='nightsky'",timeout=5700)
        check('Automatic carousel wraps',True)
        page.locator('#pause').click();page.locator('#pause').evaluate('e=>e.blur()');title=page.locator('#scene-name').inner_text();page.wait_for_timeout(4900)
        check('Explicit pause respected',page.locator('#scene-name').inner_text()==title)
        page.locator('#pause').click();page.locator('#pause').evaluate('e=>e.blur()');page.mouse.move(1,1);page.wait_for_timeout(4900)
        check('Play resumes shortened interval',page.locator('#scene-name').inner_text()!=title)
        page.locator('#next').evaluate('e=>{e.click();e.click();e.click()}');page.wait_for_timeout(600)
        check('Rapid slide input settles',page.locator('#scene').get_attribute('data-busy')=='false')
        page.locator('.brand-marquee').scroll_into_view_if_needed();page.mouse.move(0,0);still(page)
        transforms=page.locator('.brand-track').evaluate_all('els=>els.map(e=>getComputedStyle(e).transform)');page.wait_for_timeout(700)
        after=page.locator('.brand-track').evaluate_all('els=>els.map(e=>getComputedStyle(e).transform)')
        check('Both logo rows continue scrolling',all(a!=b for a,b in zip(transforms,after)))
        check('Second row reverses direction',page.locator('.brand-track').nth(1).evaluate("e=>getComputedStyle(e).animationDirection==='reverse'"))
        page.locator('#brands-pause').click();still(page);t=page.locator('.brand-track').evaluate_all('els=>els.map(e=>getComputedStyle(e).transform)');page.wait_for_timeout(400)
        check('Logo Pause still works',page.locator('.brand-track').evaluate_all('els=>els.map(e=>getComputedStyle(e).transform)')==t)
        for section in ('work','studio','services','contact'):
            page.evaluate("id=>scrollTo(0,document.getElementById(id).offsetTop-document.querySelector('.header').offsetHeight-8)",section);page.wait_for_timeout(700)
            check('Navigation tracks '+section,page.locator('.nav-links a[aria-current=location]').get_attribute('href')=='#'+section)
        ctx.close()
        # No JavaScript: the newly visible studio is never hidden by motion code.
        ctx=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844});page=ctx.new_page();page.goto(origin,wait_until='load')
        check('Without JS all studio copy is visible',page.locator('.studio-detail:visible').count()==3)
        check('Without JS both logo rows retained',page.locator('.brand-row').count()==2)
        ctx.close();browser.close()
      for name in ('robots.txt','sitemap.xml','media/cma-social-v6.jpg','favicon.ico','media/cma-icon-192-v6.png'):
          with urllib.request.urlopen(origin+'/'+name) as r:check('HTTP asset '+name,r.status==200)
      check('Sitemap parses',ET.parse(directory/'sitemap.xml').getroot().tag.endswith('urlset'))
      check('Social card JPEG exact dimensions',Image.open(directory/'media/cma-social-v6.jpg').size==(1200,630))
      check('Logo remains transparent',Image.open(directory/'media/cma-logo-transparent.png').getchannel('A').getextrema()[0]==0)
    except Exception as error:
      errors.append(repr(error));check('Suite completed without exception',False,repr(error))
      raise
    finally:
      server.shutdown();check('No uncaught browser errors',not errors,errors)
      report={'version':VERSION,'origin':'local HTTP release server','original_artwork':True,'passed':sum(c['passed'] for c in checks),'failed':sum(not c['passed'] for c in checks),'errors':errors,'results':checks}
      (qa/'polish-v6-report.json').write_text(json.dumps(report,indent=2)+'\n');(qa/'report.json').write_text(json.dumps(report,indent=2)+'\n')
      print('CMA_V6_QA '+json.dumps({k:v for k,v in report.items() if k!='results'}),flush=True)
    if report['failed']:raise SystemExit(1)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path);p.add_argument('--chromium',default='/usr/bin/chromium');a=p.parse_args();run(a.directory.resolve(),a.chromium)
