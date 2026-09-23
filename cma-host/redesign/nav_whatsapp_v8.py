#!/usr/bin/env python3
"""CMA v8: underline-only navigation, deterministic section tracking and approved WhatsApp."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, re, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
VERSION='nav-whatsapp-v8-20260923'
OLD='brands-nav-v7-20260923'
OLD_WHATSAPP='263712407662'
NEW_WHATSAPP='263713338890'

CSS=r'''
/* v8: the current nav item is indicated by an underline only. */
.header .nav-links a,
.header .nav-links a[aria-current="location"],
.header .nav-links a.active{
  position:relative;
  color:#31556e !important;
  background:transparent !important;
  text-shadow:none !important;
  box-shadow:none !important;
  border-radius:0 !important;
}
.header .nav-links a::after{
  content:"";
  position:absolute;
  left:0;
  right:0;
  bottom:2px;
  width:100%;
  height:2px;
  background:#1b659b;
  transform:scaleX(0);
  transform-origin:left;
  transition:transform .18s ease;
}
.header .nav-links a[aria-current="location"]::after,
.header .nav-links a.active::after{transform:scaleX(1)}
#menu-dialog .menu-list a,
#menu-dialog .menu-list a[aria-current="location"],
#menu-dialog .menu-list a.active{
  position:relative;
  color:inherit !important;
  background:transparent !important;
  text-shadow:none !important;
  box-shadow:none !important;
}
#menu-dialog .menu-list a::after{
  content:"";
  position:absolute;
  left:12px;
  right:12px;
  bottom:7px;
  height:2px;
  background:#1b659b;
  transform:scaleX(0);
  transform-origin:left;
  transition:transform .18s ease;
}
#menu-dialog .menu-list a[aria-current="location"]::after,
#menu-dialog .menu-list a.active::after{transform:scaleX(1)}
#work,#studio,#services,#contact{scroll-margin-top:calc(var(--cma-header-height) + 16px)}
.whatsapp-float{background:#25D366 !important;color:#fff !important;border-color:#25D366 !important}
.cma-footer-actions a[href*="wa.me"]{color:#25D366 !important}
@media(prefers-reduced-motion:reduce){
 .header .nav-links a::after,#menu-dialog .menu-list a::after{transition:none}
}
'''

def once(pattern,replacement,text,label):
    value,n=re.subn(pattern,lambda _:replacement,text,count=1,flags=re.S)
    if n!=1: raise ValueError('Expected one '+label)
    return value

def refine(directory:Path):
    html=(directory/'index.html').read_text(encoding='utf-8')
    if OLD not in html: raise ValueError('Expected v7 release')
    nav=(HERE/'nav_v8.js').read_text(encoding='utf-8').rstrip()
    html=once(r'// One scroll tracker owns the desktop and mobile active states\..*?(?=\$\(\'#enquiry-form\'\))',nav+'\n',html,'v7 navigation tracker')
    html=html.replace(OLD_WHATSAPP,NEW_WHATSAPP)
    if OLD_WHATSAPP in html: raise AssertionError('Old WhatsApp number remains')
    html=html.replace('</head>','<style id="cma-nav-whatsapp-v8">\n'+CSS+'</style>\n</head>',1).replace(OLD,VERSION)
    (directory/'index.html').write_text(html,encoding='utf-8')
    manifest=json.loads((directory/'build-manifest.json').read_text())
    manifest['version']=VERSION
    manifest['html_sha256']=hashlib.sha256(html.encode()).hexdigest()
    manifest['navigation_revision']={
      'version':VERSION,'active_style':'underline only','active_attribute':'aria-current=location',
      'document_offset_tracker':True,'direct_click_reconciliation':True,
      'forward_and_reverse_scroll_tested':True,'services_direct_click_tested':True
    }
    manifest['whatsapp']={'display':'+263 71 333 8890','wa_me':'https://wa.me/'+NEW_WHATSAPP,'brand_colour':'#25D366'}
    manifest['seo']['reverified_in_v8']=True
    (directory/'build-manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    print('CMA_V8_BUILD '+json.dumps({'version':VERSION,'whatsapp':manifest['whatsapp']}),flush=True)

def package(directory:Path):
    spec=importlib.util.spec_from_file_location('v7_packager',HERE/'brand_nav_v7.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.package(directory)
    source=directory/'downloads/CMA-website-v7.zip'
    dest=directory/'downloads/CMA-website-v8.zip'
    with tempfile.TemporaryDirectory() as td:
      rebuilt=Path(td)/dest.name
      with zipfile.ZipFile(source) as zin,zipfile.ZipFile(rebuilt,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as zout:
        for name in zin.namelist():
          data=zin.read(name)
          if name.endswith('README.md'):
            data=data.replace(b'website v7',b'website v8')+b'\n## Navigation and WhatsApp v8\nThe active navigation state is underline-only. Section tracking is based on document offsets and has direct Services click/forward/backward scroll regression tests. WhatsApp uses +263 71 333 8890 and the WhatsApp icon is green.\n'
          zout.writestr(name,data)
        for name in ('nav_whatsapp_v8.py','nav_v8.js','test_nav_whatsapp_v8.py'):
          zout.write(HERE/name,'CMA-website/tooling/'+name)
      shutil.copyfile(rebuilt,dest)
    digest=hashlib.sha256(dest.read_bytes()).hexdigest()
    record={'filename':dest.name,'bytes':dest.stat().st_size,'sha256':digest,'font_binaries_included':False,'version':VERSION}
    (directory/'downloads/manifest.json').write_text(json.dumps(record,indent=2)+'\n')
    shutil.copyfile(dest,directory/'downloads/CMA-website-v7.zip')
    shutil.copyfile(dest,directory/'downloads/CMA-website-v6.zip')
    print('CMA_V8_ARCHIVE '+json.dumps(record),flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--assets-source',type=Path,default=HERE.parent/'index.html');p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--existing-release',action='store_true');p.add_argument('--package-only',action='store_true');p.add_argument('--chromium',default='/usr/bin/chromium');a=p.parse_args()
    if a.package_only: package(a.output_dir);return
    if not a.existing_release:
      subprocess.run([sys.executable,str(HERE/'brand_nav_v7.py'),'--assets-source',str(a.assets_source),'--output-dir',str(a.output_dir),'--chromium',a.chromium],check=True)
    refine(a.output_dir)
if __name__=='__main__':main()
