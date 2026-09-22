#!/usr/bin/env python3
"""Tests actual campaign timing, seamless logo rows and mobile motion layout.

--inline uses the original release media as data URLs for a network-restricted
local browser. The production build gate defaults to a real local HTTP origin.
"""
from __future__ import annotations
import argparse,base64,functools,http.server,json,mimetypes,threading
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright
VERSION='campaign-motion-v5-20260922'

def run(directory,executable,inline=False):
 output=directory/'__qa';output.mkdir(exist_ok=True)
 class Handler(http.server.SimpleHTTPRequestHandler):
  def log_message(self,*_):pass
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(directory.resolve())))
 threading.Thread(target=server.serve_forever,daemon=True).start()
 origin=f'http://127.0.0.1:{server.server_port}'
 html=(directory/'index.html').read_text()
 if inline:
  for f in (directory/'media').rglob('*'):
   if f.is_file():html=html.replace('/'+str(f.relative_to(directory)),f'data:{mimetypes.guess_type(f.name)[0]};base64,'+base64.b64encode(f.read_bytes()).decode())
 results=[];errors=[]
 def check(name,passed,detail=None):
  results.append({'test':name,'passed':bool(passed),'detail':detail})
  if not passed:print('FAIL',name,detail,flush=True)
 def load(page):
  page.on('pageerror',lambda e:errors.append(str(e)))
  if inline:page.set_content(html,wait_until='load')
  else:page.goto(origin,wait_until='networkidle',timeout=45000)
  page.evaluate('document.fonts.ready');page.locator('img').evaluate_all("els=>els.forEach(e=>e.loading='eager')")
  page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)')
 try:
  logo=Image.open(directory/'media'/'cma-logo-transparent.png').convert('RGBA')
  check('Real transparent logo alpha',logo.getextrema()[3]==(0,255))
  check('No black rectangle in logo corners',all(logo.getpixel(p)[3]==0 for p in [(0,0),(logo.width-1,0),(0,logo.height-1),(logo.width-1,logo.height-1)]))
  with sync_playwright() as p:
   browser=p.chromium.launch(executable_path=executable,headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
   for width in (320,390,768,1024,1440):
    c=browser.new_context(viewport={'width':width,'height':1000},reduced_motion='reduce');page=c.new_page();load(page)
    check(f'{width}: latest release',page.locator('meta[name=cma-build]').get_attribute('content')==VERSION)
    check(f'{width}: no page overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
    check(f'{width}: transparent header and menu',page.locator('.brand img').evaluate_all("els=>els.every(i=>getComputedStyle(i).backgroundColor==='rgba(0, 0, 0, 0)' && i.src.includes('cma-logo-transparent') )") if not inline else page.locator('.brand img').evaluate_all("els=>els.every(i=>getComputedStyle(i).backgroundColor==='rgba(0, 0, 0, 0)' && i.src.startsWith('data:image/png'))"))
    check(f'{width}: exactly two logo rows',page.locator('.brand-row').count()==2)
    check(f'{width}: all 39 original marks',page.locator('.brand-original img').count()==39)
    check(f'{width}: decorative duplicates hidden',page.locator('.brand-duplicate[aria-hidden=true][inert]').count()==2 and page.locator('.brand-duplicate img:not([alt=""])').count()==0)
    check(f'{width}: two row height',page.locator('.brand-marquee').bounding_box()['height']<=235)
    check(f'{width}: reduced motion stops loops',page.locator('.brand-marquee').get_attribute('data-running')=='false')
    check(f'{width}: reduced motion offers scroll',page.locator('.brand-row').evaluate_all("rows=>rows.every(r=>getComputedStyle(r).overflowX==='auto')"))
    check(f'{width}: reduced motion stops autoplay',page.locator('#pause').get_attribute('aria-pressed')=='true')
    for index,key in enumerate(('nightsky','gold-blend','whitestone')):
     page.locator(f'[data-slide="{index}"]').click();page.wait_for_function("k=>document.getElementById('scene').dataset.slideKey===k",arg=key)
     page.wait_for_function("document.getElementById('scene').dataset.busy==='false'")
     check(f'{width}: {key} matching action',page.locator('#scene-project').get_attribute('data-project')==key)
     check(f'{width}: {key} all artwork present',page.locator('#scene-art img').evaluate_all('els=>els.length===3&&els.every(i=>i.complete&&i.naturalWidth)'))
    check(f'{width}: all carousel labels visible',page.locator('.scene-tab').evaluate_all("els=>els.every(e=>parseFloat(getComputedStyle(e).fontSize)>=11 && e.getBoundingClientRect().right<=document.getElementById('scene').getBoundingClientRect().right-10)"))
    check(f'{width}: correct full whisky name',page.locator('[data-slide="1"]').inner_text()=='Gold Blend Whisky')
    for section in ('work','studio','services','contact'):
     page.locator('#'+section).scroll_into_view_if_needed();page.wait_for_timeout(80)
     check(f'{width}: {section} overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
    if width in (390,1440):
     page.locator('#profile-brands').scroll_into_view_if_needed();page.screenshot(path=str(output/f'logo-rows-{width}.png'))
     page.evaluate('scrollTo(0,0)');page.screenshot(path=str(output/f'whitestone-motion-{width}.png'))
    c.close()
   # Exercise real default autoplay with the pointer held over the artwork.
   c=browser.new_context(viewport={'width':1440,'height':1050},reduced_motion='no-preference');page=c.new_page();load(page)
   page.mouse.move(700,430);page.wait_for_timeout(6700)
   check('Autoplay continues with pointer over hero',page.locator('#scene').get_attribute('data-slide-key')=='gold-blend')
   page.wait_for_timeout(6700)
   check('Autoplay reaches third campaign',page.locator('#scene').get_attribute('data-slide-key')=='whitestone')
   page.wait_for_timeout(6700)
   check('Autoplay wraps back to first campaign',page.locator('#scene').get_attribute('data-slide-key')=='nightsky')
   themes=[]
   for index in range(3):
    page.locator(f'[data-slide="{index}"]').click();page.wait_for_timeout(1000)
    themes.append(page.locator('#scene').evaluate('e=>getComputedStyle(e).backgroundColor'))
    page.screenshot(path=str(output/f'campaign-theme-{index+1}.png'))
   check('Three visually distinct campaign themes',themes==['rgb(176, 212, 238)','rgb(231, 198, 135)','rgb(185, 215, 204)'],themes)
   # Pointer focus on a carousel button does not block subsequent autoplay.
   page.locator('[data-slide="0"]').click();page.mouse.move(700,430);page.wait_for_timeout(6700)
   check('Pointer click does not leave carousel stuck',page.locator('#scene').get_attribute('data-slide-key')=='gold-blend')
   page.locator('#pause').click();title=page.locator('#scene-name').inner_text();page.mouse.move(700,430);page.wait_for_timeout(6500)
   check('Explicit pause holds campaign',page.locator('#scene-name').inner_text()==title)
   page.locator('#pause').click();page.mouse.move(700,430);page.wait_for_timeout(6700)
   check('Explicit play resumes campaign',page.locator('#scene-name').inner_text()!=title)
   page.locator('#next').evaluate('e=>{e.click();e.click();e.click()}');page.wait_for_timeout(1100)
   check('Rapid controls settle without a blank slide',page.locator('#scene').get_attribute('data-busy')=='false' and not page.locator('#scene-art').evaluate("e=>e.classList.contains('changing')"))
   page.locator('#profile-brands').scroll_into_view_if_needed();page.mouse.move(0,0);page.wait_for_timeout(200)
   x1=page.locator('.brand-track').evaluate_all('es=>es.map(e=>getComputedStyle(e).transform)');page.wait_for_timeout(500)
   x2=page.locator('.brand-track').evaluate_all('es=>es.map(e=>getComputedStyle(e).transform)')
   check('Both logo rows really move',all(a!=b for a,b in zip(x1,x2)))
   check('Rows move in opposite directions',page.locator('.brand-track').evaluate_all("es=>es.map(e=>getComputedStyle(e).animationDirection)")==['normal','reverse'])
   check('Exact repeated track widths',page.locator('.brand-track').evaluate_all("es=>es.every(e=>Math.abs(e.children[0].getBoundingClientRect().width-e.children[1].getBoundingClientRect().width)<.1)"))
   # Seek to either side of the actual animation seam; visible images must match.
   seamless=page.locator('.brand-row').evaluate_all('''rows=>rows.every(row=>{const t=row.querySelector('.brand-track'),a=t.getAnimations()[0],d=a.effect.getComputedTiming().duration;const r=row.getBoundingClientRect();function visible(){return Array.from(t.querySelectorAll('li')).map(li=>({src:li.firstElementChild.src,x:li.getBoundingClientRect().left,w:li.getBoundingClientRect().width})).filter(o=>o.x>r.left+8&&o.x+o.w<r.right-8);}a.pause();a.currentTime=d-8;const before=visible();a.currentTime=d+8;const after=visible();a.cancel();t.style.animation='none';void t.offsetWidth;t.style.removeProperty('animation');return before.length>0&&before.length===after.length&&before.every((v,i)=>v.src===after[i].src&&Math.abs(v.x-after[i].x)<2);})''')
   check('Both logo loops have a seamless boundary',seamless)
   page.locator('#brands-pause').click();page.wait_for_timeout(100)
   x1=page.locator('.brand-track').evaluate_all('es=>es.map(e=>getComputedStyle(e).transform)');page.wait_for_timeout(350)
   check('Logo Pause holds both tracks',x1==page.locator('.brand-track').evaluate_all('es=>es.map(e=>getComputedStyle(e).transform)'))
   page.locator('#brands-pause').click();page.mouse.move(0,0);page.wait_for_timeout(150)
   check('Logo Play restores scrolling',page.locator('.brand-marquee').get_attribute('data-running')=='true')
   page.locator('#profile-slide-open').click();page.wait_for_timeout(150)
   check('Full original brands slide still opens',page.locator('#profile-slide-dialog').is_visible())
   check('Modal pauses logo motion',page.locator('.brand-marquee').get_attribute('data-running')=='false')
   page.keyboard.press('Escape');page.wait_for_timeout(100)
   check('Profile closes without locking scroll',not page.evaluate("document.body.classList.contains('locked')"))
   page.locator('.work-picture').first.scroll_into_view_if_needed();rect=page.locator('.work-picture').first.bounding_box();page.mouse.move(rect['x']+rect['width']*.75,rect['y']+rect['height']*.3);page.wait_for_timeout(100)
   check('Portfolio tilt responds to pointer',bool(page.locator('.work-picture').first.evaluate("e=>e.style.getPropertyValue('--tilt-x')")))
   page.mouse.move(0,0);page.wait_for_timeout(100)
   check('Portfolio tilt resets on leave',not page.locator('.work-picture').first.evaluate("e=>e.style.getPropertyValue('--tilt-x')"))
   check('Reveal keeps approved section wording',page.locator('#studio-title').inner_text()=='Who we are.')
   page.emulate_media(reduced_motion='reduce');page.wait_for_timeout(150)
   check('Live reduced-motion preference stops autoplay',page.locator('#pause').get_attribute('aria-pressed')=='true')
   check('Live reduced-motion preference stops logo motion',page.locator('.brand-marquee').get_attribute('data-running')=='false')
   check('Live reduced-motion preference disables tilt',page.locator('.work-picture').first.evaluate("e=>getComputedStyle(e).transform==='none'"))
   c.close();browser.close()
 finally:server.shutdown()
 check('No motion runtime errors',not errors,errors)
 report={'version':VERSION,'origin':'original-media DOM rendering' if inline else 'local HTTP release server','original_artwork':True,'passed':sum(r['passed'] for r in results),'failed':sum(not r['passed'] for r in results),'errors':errors,'results':results}
 (output/'motion-report.json').write_text(json.dumps(report,indent=2)+'\n');print('CMA_MOTION_QA '+json.dumps({k:v for k,v in report.items() if k!='results'}),flush=True)
 if report['failed']:raise SystemExit(1)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('directory',type=Path);p.add_argument('--chromium',default='/usr/bin/chromium');p.add_argument('--inline',action='store_true');a=p.parse_args();run(a.directory,a.chromium,a.inline)
