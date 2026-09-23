#!/usr/bin/env python3
"""Focused v8 tests: every nav section, underline-only styling, WhatsApp and SEO."""
from __future__ import annotations
import argparse,functools,http.server,json,threading,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
VERSION='nav-whatsapp-v8-20260923'
NEW='263713338890'
OLD='263712407662'

def run(directory:Path,chromium='/usr/bin/chromium'):
  class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*_):pass
  server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(directory)))
  threading.Thread(target=server.serve_forever,daemon=True).start();origin=f'http://127.0.0.1:{server.server_port}'
  qa=directory/'__qa';qa.mkdir(exist_ok=True);checks=[];errors=[]
  def check(name,ok,detail=None):
    checks.append({'test':name,'passed':bool(ok),**({'detail':detail} if detail is not None else {})})
    if not ok:print('FAIL',name,detail,flush=True)
  def active(page,selector='.nav-links'):
    return page.locator(selector+' a[aria-current="location"]').get_attribute('href') if page.locator(selector+' a[aria-current="location"]').count() else None
  def section_top(page,id):
    return page.evaluate("id=>document.getElementById(id).getBoundingClientRect().top+scrollY",id)
  def go(page,id):
    page.evaluate("id=>scrollTo(0,document.getElementById(id).getBoundingClientRect().top+scrollY-document.querySelector('.header').getBoundingClientRect().height-8)",id)
    page.wait_for_timeout(280)
  try:
    with sync_playwright() as p:
      browser=p.chromium.launch(executable_path=chromium,args=['--no-sandbox','--disable-dev-shm-usage'])
      for width in (320,390,600,768,1024,1440):
        ctx=browser.new_context(viewport={'width':width,'height':900},reduced_motion='reduce')
        page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        result=page.goto(origin,wait_until='networkidle');page.evaluate('document.fonts.ready')
        check(f'{width}: HTTP 200',result.status==200)
        check(f'{width}: v8 identity',page.locator('meta[name=cma-build]').get_attribute('content')==VERSION)
        check(f'{width}: no horizontal overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
        # Forward and backward scroll proves that tracking works past Studio and on Services.
        for id in ('work','studio','services','contact'):
          go(page,id);check(f'{width}: forward highlights {id}',active(page)=='#'+id,active(page))
          check(f'{width}: exactly one desktop current after {id}',page.locator('.nav-links a[aria-current=location]').count()==1)
        for id in ('services','studio','work'):
          go(page,id);check(f'{width}: reverse highlights {id}',active(page)=='#'+id,active(page))
        # Services direct link is the previously reported failure path.
        page.evaluate('scrollTo(0,0)');page.wait_for_timeout(180)
        page.locator('.nav-links a[href="#services"]').click();page.wait_for_timeout(850)
        check(f'{width}: direct Services click highlights Services',active(page)=='#services',active(page))
        services_y=page.locator('#services').bounding_box()['y'];header_h=page.locator('.header').bounding_box()['height']
        check(f'{width}: direct Services click lands below header',services_y>=header_h-2 and services_y<header_h+80,(services_y,header_h))
        # Active state is only the underline: no fill, shadow or colour change.
        if width>=768:
          active_style=page.locator('.nav-links a[href="#services"]').evaluate("""e=>({bg:getComputedStyle(e).backgroundColor,shadow:getComputedStyle(e).textShadow,box:getComputedStyle(e).boxShadow,color:getComputedStyle(e).color,underline:getComputedStyle(e,'::after').transform,height:getComputedStyle(e,'::after').height})""")
          inactive_style=page.locator('.nav-links a[href="#work"]').evaluate("""e=>({bg:getComputedStyle(e).backgroundColor,shadow:getComputedStyle(e).textShadow,box:getComputedStyle(e).boxShadow,color:getComputedStyle(e).color,underline:getComputedStyle(e,'::after').transform})""")
          check(f'{width}: active nav has transparent background',active_style['bg']=='rgba(0, 0, 0, 0)',active_style)
          check(f'{width}: active nav has no shadow',active_style['shadow']=='none' and active_style['box']=='none',active_style)
          check(f'{width}: active nav colour unchanged',active_style['color']==inactive_style['color'],(active_style,inactive_style))
          check(f'{width}: only active underline is visible',active_style['underline']!=inactive_style['underline'] and active_style['height']=='2px',(active_style,inactive_style))
        # Mobile menu uses the same underline-only state.
        if width<=600:
          page.locator('#menu-open').click();page.wait_for_timeout(120)
          check(f'{width}: mobile Services current',active(page,'.menu-list')=='#services',active(page,'.menu-list'))
          st=page.locator('.menu-list a[href="#services"]').evaluate("""e=>({bg:getComputedStyle(e).backgroundColor,shadow:getComputedStyle(e).textShadow,box:getComputedStyle(e).boxShadow,underline:getComputedStyle(e,'::after').transform})""")
          check(f'{width}: mobile active is underline only',st['bg']=='rgba(0, 0, 0, 0)' and st['shadow']=='none' and st['box']=='none' and st['underline']!='matrix(0, 0, 0, 1, 0, 0)',st)
          page.keyboard.press('Escape');page.wait_for_timeout(100)
        # Every WhatsApp destination uses the approved number.
        hrefs=page.locator('a[href*="wa.me"]').evaluate_all('els=>els.map(e=>e.href)')
        check(f'{width}: WhatsApp links exist',len(hrefs)>=2,hrefs)
        check(f'{width}: every WhatsApp link uses approved number',all(NEW in h and OLD not in h for h in hrefs),hrefs)
        float_style=page.locator('.whatsapp-float').evaluate("e=>({bg:getComputedStyle(e).backgroundColor,color:getComputedStyle(e).color})")
        check(f'{width}: floating WhatsApp icon is green',float_style['bg']=='rgb(37, 211, 102)' and float_style['color']=='rgb(255, 255, 255)',float_style)
        footer_green=page.locator('.cma-footer-actions a[href*="wa.me"]').evaluate("e=>getComputedStyle(e).color")
        check(f'{width}: footer WhatsApp icon is green',footer_green=='rgb(37, 211, 102)',footer_green)
        # SEO remains present after the navigation/phone patch.
        check(f'{width}: title present',page.title()=='CM&A | Advertising & marketing agency in Harare')
        check(f'{width}: one canonical HTTPS URL',page.locator('link[rel=canonical]').count()==1 and page.locator('link[rel=canonical]').get_attribute('href').startswith('https://'))
        check(f'{width}: description and robots present',page.locator('meta[name=description]').count()==1 and 'index' in page.locator('meta[name=robots]').get_attribute('content'))
        check(f'{width}: Open Graph preview present',page.locator('meta[property="og:image"]').count()==1 and page.locator('meta[property="og:image:width"]').get_attribute('content')=='1200')
        check(f'{width}: Twitter large card present',page.locator('meta[name="twitter:card"]').get_attribute('content')=='summary_large_image')
        graph=json.loads(page.locator('script[type="application/ld+json"]').text_content())
        check(f'{width}: Organization and WebSite schema', {x['@type'] for x in graph['@graph']}=={'Organization','WebSite'})
        check(f'{width}: no fabricated Search Console verification',page.locator('meta[name=google-site-verification]').count()==0)
        ctx.close()
      browser.close()
    for path in ('robots.txt','sitemap.xml','media/cma-social-v6.jpg'):
      with urllib.request.urlopen(origin+'/'+path) as r:check('HTTP '+path,r.status==200)
    check('social card remains 1200x630',Image.open(directory/'media/cma-social-v6.jpg').size==(1200,630))
  except Exception as e:
    errors.append(repr(e));check('suite exception',False,repr(e));raise
  finally:
    server.shutdown();check('no browser errors',not errors,errors)
    report={'version':VERSION,'passed':sum(x['passed'] for x in checks),'failed':sum(not x['passed'] for x in checks),'errors':errors,'results':checks}
    (qa/'nav-whatsapp-v8-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('CMA_V8_QA '+json.dumps({k:v for k,v in report.items() if k!='results'}),flush=True)
  if report['failed']:raise SystemExit(1)

if __name__=='__main__':
  p=argparse.ArgumentParser();p.add_argument('directory',type=Path);p.add_argument('--chromium',default='/usr/bin/chromium');a=p.parse_args();run(a.directory.resolve(),a.chromium)
