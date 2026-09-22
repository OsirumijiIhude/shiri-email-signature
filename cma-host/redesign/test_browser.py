#!/usr/bin/env python3
"""Browser regression suite for a built CMA release. Never sends enquiries."""
from __future__ import annotations
import argparse
import base64
import functools
import http.server
import json
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright


def run(directory: Path, executable: str, fixture: bool = False) -> None:
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *_):
            pass
    handler = functools.partial(QuietHandler, directory=str(directory.resolve()))
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    output = directory / '__qa'
    output.mkdir(exist_ok=True)
    html = (directory / 'index.html').read_text()
    if fixture:
        for image in (directory / 'media').iterdir():
            uri='data:image/png;base64,'+base64.b64encode(image.read_bytes()).decode()
            html=html.replace('/media/'+image.name,uri)
    def navigate(page):
        if fixture:
            page.set_content(html,wait_until='domcontentloaded')
            return None
        return page.goto(origin,wait_until='networkidle',timeout=45000)
    results = []
    errors = []
    def check(name, passed, detail=None):
        record = {'test':name, 'passed':bool(passed)}
        if detail is not None: record['detail'] = detail
        results.append(record)
        if not passed: print('FAIL:',name,detail,flush=True)
    try:
      with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=executable,headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
        for width in (320,390,768,1024,1440):
          context = browser.new_context(viewport={'width':width,'height':900},reduced_motion='reduce')
          page = context.new_page()
          page.on('pageerror',lambda error: errors.append(str(error)))
          response = navigate(page)
          if not fixture: check(f'{width}: HTTP',response.status==200)
          check(f'{width}: release marker',page.locator('meta[name=cma-build]').get_attribute('content')=='studio-rebuild-20260922')
          check(f'{width}: horizontal overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
          check(f'{width}: single main heading',page.locator('h1').count()==1)
          check(f'{width}: six projects',page.locator('.portfolio .project').count()==6)
          check(f'{width}: eight services',page.locator('.service').count()==8)
          check(f'{width}: five accurate brands',page.locator('.brand-names span').count()==5 and 'Dr Klin' not in page.locator('.brand-names').inner_text() and 'Maxi' not in page.locator('.brand-names').inner_text())
          check(f'{width}: company and selector',page.locator('#company').count()==1 and page.locator('#service option').count()==9)
          check(f'{width}: floating WhatsApp',page.locator('.whatsapp-float').is_visible())
          check(f'{width}: footer contact actions',page.locator('footer a[href^="mailto:"]').count()==1 and page.locator('footer a[href*="wa.me"]').count()==1 and page.locator('footer a[href*="google.com/maps"]').count()==1)
          for image in page.locator('img').all():
            image.evaluate("el=>el.loading='eager'")
          page.wait_for_function("Array.from(document.images).every(i=>i.complete)")
          broken=page.evaluate("Array.from(document.images).filter(i=>!i.naturalWidth).map(i=>i.alt)")
          check(f'{width}: all inline media decode',not broken,broken)
          check(f'{width}: reduced motion starts paused',page.locator('#pause').get_attribute('aria-pressed')=='true')
          page.screenshot(path=str(output/f'opening-{width}.png'))
          if width in (390,1440):
            for section in ('work','studio','services','contact'):
              page.locator('#'+section).scroll_into_view_if_needed()
              page.wait_for_timeout(250)
              page.screenshot(path=str(output/f'{section}-{width}.png'))
            page.evaluate('scrollTo(0,0)')
            page.screenshot(path=str(output/f'full-{width}.png'),full_page=True)
          if width<=760:
            page.evaluate('scrollTo(0,0)')
            page.locator('#menu-open').click()
            check(f'{width}: menu opens',page.locator('#menu-dialog').is_visible())
            check(f'{width}: menu locks page',page.evaluate("getComputedStyle(document.body).overflow==='hidden'"))
            page.keyboard.press('Escape')
            check(f'{width}: menu closes and unlocks',not page.locator('#menu-dialog').is_visible() and not page.evaluate("document.body.classList.contains('locked')"))
          for key in ('nightsky','hunters','gold-blend','whitestone','land-of-gold','elegance'):
            button=page.locator('.portfolio [data-project="'+key+'"]')
            button.click()
            check(f'{width}: {key} dialog opens',page.locator('#case-dialog').is_visible())
            page.wait_for_function("Array.from(document.querySelectorAll('#case-gallery img')).every(i=>i.complete&&i.naturalWidth>0)")
            check(f'{width}: {key} gallery decodes',page.locator('#case-gallery img').count()>=2)
            page.keyboard.press('Escape')
            check(f'{width}: {key} closes',not page.locator('#case-dialog').is_visible())
          page.locator('#next').click()
          page.wait_for_function("document.querySelector('#scene-name').textContent==='Gold Blend'")
          check(f'{width}: manual carousel',page.locator('#scene-counter').inner_text()=='02 / 03')
          page.locator('.service summary').nth(3).click()
          page.wait_for_timeout(200)
          check(f'{width}: one open service',page.locator('.service[open]').count()==1)
          page.locator('#name').fill('Browser QA')
          page.locator('#email').fill('test@example.com')
          page.locator('#company').fill('QA fixture')
          page.locator('#service').select_option(label='Branding & packaging')
          page.locator('#message').fill('Browser validation only. Nothing is sent.')
          page.locator('#enquiry-form button[type=submit]').click()
          check(f'{width}: enquiry prepared locally',page.locator('#enquiry-ready').is_visible() and 'Nothing has been sent' in page.locator('#enquiry-status').inner_text())
          check(f'{width}: draft includes company/service','QA fixture' in page.locator('#enquiry-copy').input_value() and 'Branding & packaging' in page.locator('#enquiry-copy').input_value())
          check(f'{width}: valid email action',page.locator('#open-email').get_attribute('href').startswith('mailto:tendayi@cma.co.zw?'))
          page.locator('#privacy-open').click()
          check(f'{width}: privacy dialog',page.locator('#privacy-dialog').is_visible())
          page.keyboard.press('Escape')
          check(f'{width}: privacy unlock',not page.evaluate("document.body.classList.contains('locked')"))
          context.close()
        context=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='no-preference')
        page=context.new_page();page.on('pageerror',lambda error: errors.append(str(error)))
        navigate(page)
        page.mouse.move(0,0)
        page.wait_for_timeout(6700)
        check('Automatic carousel advances',page.locator('#scene-name').inner_text()=='Gold Blend')
        page.locator('#pause').click()
        title=page.locator('#scene-name').inner_text();page.mouse.move(0,0)
        page.locator('#pause').evaluate('e=>e.blur()')
        page.wait_for_timeout(6500)
        check('Explicit pause holds slide',page.locator('#scene-name').inner_text()==title)
        page.locator('#pause').click();page.locator('#pause').evaluate('e=>e.blur()');page.mouse.move(0,0)
        page.wait_for_timeout(6500)
        check('Play resumes rotation',page.locator('#scene-name').inner_text()!=title)
        page.locator('#next').evaluate('e=>{e.click();e.click();e.click()}')
        page.wait_for_timeout(550)
        check('Rapid carousel changes settle',not page.locator('#scene-art').evaluate("e=>e.classList.contains('changing')"))
        for section in ('work','studio','services','contact'):
          page.evaluate("id=>{const e=document.getElementById(id);scrollTo(0,e.offsetTop-90)}",section)
          page.wait_for_timeout(1000)
          active=page.locator('.nav-links a[aria-current=location]').get_attribute('href')
          check(f'Navigation tracks {section}',active=='#'+section,active)
        context.close();browser.close()
    finally:
      server.shutdown()
    check('No uncaught browser errors',not errors,errors)
    report={'version':'studio-rebuild-20260922','fixture_artwork':fixture,'origin':'local build server',
            'passed':sum(x['passed'] for x in results),'failed':sum(not x['passed'] for x in results),
            'errors':errors,'results':results}
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('CMA_BROWSER_QA '+json.dumps({k:v for k,v in report.items() if k!='results'}),flush=True)
    if report['failed']:raise SystemExit(1)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('directory',type=Path);parser.add_argument('--chromium',default='/usr/bin/chromium');parser.add_argument('--fixture',action='store_true');a=parser.parse_args();run(a.directory,a.chromium,a.fixture)
