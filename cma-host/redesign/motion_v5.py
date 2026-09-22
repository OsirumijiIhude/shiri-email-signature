#!/usr/bin/env python3
"""CMA motion release: automatic campaigns, two logo loops, original-logo cutout.

Build-time changes only. Retains approved v4 identity and original media. Uses
small website-specific adaptations of Magic UI Marquee / Blur Fade and React
Bits TiltedCard; notices are included in the delivered HTML and release.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, re, shutil
from pathlib import Path

HERE=Path(__file__).resolve().parent
OLD='client-optima-blue-v4-20260922'
VERSION='campaign-motion-v5-20260922'

NOTICES='''CMA website motion adaptations, 22 September 2026

Magic UI Marquee and Blur Fade
https://magicui.design/docs/components/marquee
https://magicui.design/docs/components/blur-fade
https://github.com/magicuidesign/magicui

MIT License
Copyright (c) Magic UI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

React Bits TiltedCard
https://reactbits.dev/components/tilted-card
https://github.com/DavidHDev/react-bits/blob/main/src/content/Components/TiltedCard/TiltedCard.jsx

MIT + Commons Clause License Condition v1.0
Copyright (c) 2026 David Haz

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, and distribute the Software as part of
an application, website, or product, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

Commons Clause Restriction
You may use this Software, including for any commercial purpose, so long as
you do not sell, sublicense, or redistribute the components themselves-whether
alone, in a bundle, or as a ported version.

No Warranty
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

The adaptations are part of this CMA website, not redistributed UI components.
No React, animation CDN, tracking script or additional font is required.
'''

LOGO_FILTER='''<filter id="cma-logo-cutout" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 1 1 1 0 0"/></filter>'''

CSS='''
/* Campaign motion v5. The original logo pixels are used; black becomes alpha. */
.brand img{background:transparent!important;border-radius:0;mix-blend-mode:normal;filter:none;box-shadow:none}
#home{transition:background-color .9s cubic-bezier(.22,1,.36,1)}
#scene{--scene-ink:#14374f;--scene-muted:#315771;--scene-line:#719cb9;--scene-accent:#316ea3;--scene-glow:rgba(255,255,255,.32);isolation:isolate;color:var(--scene-ink);transition:background-color .9s cubic-bezier(.22,1,.36,1),color .7s;overflow:hidden}
#scene::before{content:"";position:absolute;z-index:0;pointer-events:none;width:min(78%,860px);aspect-ratio:1;left:50%;top:49%;transform:translate(-50%,-50%);border-radius:50%;background:radial-gradient(ellipse,var(--scene-glow),transparent 67%);transition:background .9s}
#scene .scene-top p:last-child,#scene .scene-note p,#scene .scene-tab{color:var(--scene-muted)}
#scene .scene-note strong,#scene .scene-tab[aria-pressed=true],#scene .hero-title,#scene .round,#scene .project-open{color:var(--scene-ink)}
#scene .round,#scene .project-open,#scene .scene-bottom{border-color:var(--scene-line)}
#scene .scene-tab::before{background:var(--scene-accent)}
#scene .scene-art{transition:opacity .16s ease,transform .5s cubic-bezier(.22,1,.36,1)}
#scene .scene-art.changing{opacity:0;transform:translate3d(-18px,10px,0)}
#scene .hero-title.rise{animation:none}
.scene-timer{height:2px;position:absolute;z-index:8;bottom:0;left:0;right:0;background:transparent;pointer-events:none;overflow:hidden}
.scene-timer>span{display:block;height:100%;background:var(--scene-accent);transform:scaleX(var(--scene-progress,0));transform-origin:left;opacity:.72}
.scene-tab{position:relative}
.scene-tab::after{content:"";position:absolute;left:0;right:0;bottom:2px;height:1px;background:currentColor;transform:scaleX(0);transform-origin:left;transition:transform .35s}
.scene-tab[aria-pressed=true]::after{transform:scaleX(1)}
/* Magic UI's repeated flex tracks, with original logos split across two rows. */
.profile-brands{overflow:hidden}
.profile-brands-heading{gap:22px}
.brand-actions{display:flex;align-items:center;gap:23px;flex-shrink:0}
.brands-pause{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:46px;min-width:83px;padding:8px 0;background:transparent;color:var(--ink);font-size:15px}
.brands-pause .icon{width:16px;height:16px}
.brand-marquee{--logo-width:154px;--logo-height:108px;--logo-gap:16px;display:grid;grid-template-rows:repeat(2,var(--logo-height));gap:var(--logo-gap);width:100%;overflow:hidden;mask-image:linear-gradient(to right,transparent,#000 36px,#000 calc(100% - 36px),transparent);-webkit-mask-image:linear-gradient(to right,transparent,#000 36px,#000 calc(100% - 36px),transparent)}
.brand-row{min-width:0;height:var(--logo-height);overflow:hidden;outline-offset:-3px}
.brand-track{width:max-content;display:flex;animation:cma-brand-travel var(--brand-duration,72s) linear infinite;animation-play-state:paused;will-change:transform}
.brand-row:nth-child(2) .brand-track{animation-direction:reverse}
.brand-marquee[data-running=true] .brand-track{animation-play-state:running}
.brand-marquee .brand-strip{display:flex;flex:none;gap:var(--logo-gap);list-style:none;padding:0 var(--logo-gap) 0 0;margin:0;width:max-content}
.brand-marquee .brand-strip li{flex:0 0 var(--logo-width);width:var(--logo-width);height:var(--logo-height);aspect-ratio:auto;display:flex;align-items:center;justify-content:center;background:#fff;border:0;border-radius:10px;overflow:hidden;margin:0}
.brand-marquee .brand-strip img{width:100%;height:100%;max-width:none;max-height:none;object-fit:contain;padding:10px;flex-shrink:0}
.brand-marquee[data-static=true] .brand-track{animation:none;transform:none;will-change:auto}
.brand-marquee[data-static=true] .brand-duplicate{display:none}
.brand-marquee[data-static=true] .brand-row{overflow-x:auto;scrollbar-width:thin;scrollbar-color:#739ab8 transparent}
@keyframes cma-brand-travel{from{transform:translate3d(0,0,0)}to{transform:translate3d(-50%,0,0)}}
/* Short masked heading entrances and a restrained TiltedCard treatment. */
.motion-word{display:inline-block;overflow:hidden;vertical-align:top;padding-bottom:.08em;margin-bottom:-.08em}
.motion-word>span{display:inline-block;will-change:transform}.motion-word,.motion-word>span{color:inherit!important;font:inherit}
#work .project{perspective:1000px}
#work .work-picture{transform:perspective(1000px) rotateX(var(--tilt-x,0deg)) rotateY(var(--tilt-y,0deg));transition:transform .38s cubic-bezier(.22,1,.36,1),box-shadow .38s;will-change:auto}
#work .work-picture::after{content:"";pointer-events:none;position:absolute;z-index:6;inset:0;opacity:0;background:linear-gradient(110deg,transparent 22%,rgba(255,255,255,.22) 46%,transparent 68%);transform:translateX(-100%);transition:opacity .25s}
@media(hover:hover) and (pointer:fine){#work .work-picture:hover{box-shadow:0 20px 32px -24px rgba(21,56,79,.38)}#work .work-picture:hover::after{opacity:1;animation:cma-print-sheen .95s cubic-bezier(.22,1,.36,1) both}}
@keyframes cma-print-sheen{to{transform:translateX(100%)}}
@media(max-width:760px){#scene .scene-tabs{display:flex;flex-wrap:nowrap;justify-content:space-between;gap:8px}#scene .scene-tab,#scene .scene-tab:last-child{display:flex;font-size:clamp(11px,3.1vw,13px);white-space:nowrap;gap:5px;justify-content:flex-start}}
@media(max-width:760px){.profile-brands-heading{align-items:flex-start;gap:18px}.brand-actions{gap:22px;flex-wrap:wrap}.brand-marquee{--logo-width:134px;--logo-height:96px;--logo-gap:12px;mask-image:linear-gradient(to right,transparent,#000 16px,#000 calc(100% - 16px),transparent);-webkit-mask-image:linear-gradient(to right,transparent,#000 16px,#000 calc(100% - 16px),transparent)}.brand-marquee .brand-strip img{padding:8px}}
@media(max-width:400px){.brand-marquee{--logo-width:122px;--logo-height:88px;--logo-gap:10px}.brand-actions{gap:18px}.brands-pause{font-size:14px}.profile-slide-open{font-size:14px}}
@media(prefers-reduced-motion:reduce){#scene,#home,#scene .scene-art,.scene-tab::after,#work .work-picture{transition:none!important}#work .work-picture{transform:none!important}#work .work-picture::after{display:none}.motion-word>span{will-change:auto}}
'''

CONTROLLER=r'''
// Campaign controller: one timer, independent of incidental mouse hover.
const scene=$('#scene'),art=$('#scene-art'),home=$('#home');
const themes={
 'nightsky':{bg:'#b0d4ee',surround:'#bdd9ef',ink:'#14374f',muted:'#315771',line:'#719cb9',accent:'#316ea3'},
 'gold-blend':{bg:'#e7c687',surround:'#f0dbb5',ink:'#422b15',muted:'#684927',line:'#b89561',accent:'#946017'},
 'whitestone':{bg:'#b9d7cc',surround:'#d2e6dc',ink:'#183f37',muted:'#3b6457',line:'#82aa9c',accent:'#406e59'}
};
const interval=6000;let slide=0,target=0,paused=reduce.matches,busy=false,revision=0,elapsed=0;
let keyboard=false,focusPause=false,visible=true,lastTick=performance.now();
function pauseUI(){const button=$('#pause');button.setAttribute('aria-pressed',String(paused));button.setAttribute('aria-label',paused?'Play automatic rotation':'Pause automatic rotation');$('#pause-icon').setAttribute('href',paused?'#icon-play':'#icon-pause');}
function applyTheme(key){const t=themes[key];scene.style.backgroundColor=t.bg;home.style.backgroundColor=t.surround;for(const k of ['ink','muted','line','accent'])scene.style.setProperty('--scene-'+k,t[k]);scene.dataset.slideKey=key;}
function enterArtwork(){if(reduce.matches||!Element.prototype.animate)return;for(const [i,img]of Array.from(art.children).entries()){const end=getComputedStyle(img).transform;img.animate([{opacity:0,transform:'translate3d(0,30px,0) rotate(0deg) scale(.94)'},{opacity:1,transform:end==='none'?'translate3d(0,0,0)':end}],{duration:760,delay:i*65,easing:'cubic-bezier(.22,1,.36,1)',fill:'backwards'});}$('#scene-name').animate([{opacity:0,transform:'translateY(8px)'},{opacity:1,transform:'none'}],{duration:460,easing:'ease-out'});}
async function changeSlide(index,manual=false){
 const token=++revision;target=(index+slides.length)%slides.length;const next=target,s=slides[next];busy=true;elapsed=0;scene.dataset.busy='true';
 const nodes=s.images.map((key,i)=>{const img=new Image();img.src=assets[key];img.alt=s.alts[i];img.width=450;img.height=1100;return img;});
 let timeout;await Promise.race([Promise.all(nodes.map(img=>img.decode?img.decode().catch(()=>{}):Promise.resolve())),new Promise(resolve=>{timeout=setTimeout(resolve,4000);})]);clearTimeout(timeout);
 if(token!==revision)return;
 if(!nodes.every(img=>img.complete&&img.naturalWidth)){busy=false;scene.dataset.busy='false';art.classList.remove('changing');return;}
 art.classList.add('changing');if(!reduce.matches)await new Promise(resolve=>setTimeout(resolve,160));if(token!==revision)return;
 art.replaceChildren(...nodes);slide=next;applyTheme(s.key);$('#scene-name').textContent=s.name;$('#scene-description').textContent=s.description;$('#scene-project').dataset.project=s.key;$('#scene-counter').textContent=String(slide+1).padStart(2,'0')+' / 03';
 $$('[data-slide]').forEach(button=>button.setAttribute('aria-pressed',String(+button.dataset.slide===slide)));
 art.classList.remove('changing');enterArtwork();if(manual)$('#slide-status').textContent=s.name+' project selected';busy=false;scene.dataset.busy='false';elapsed=0;lastTick=performance.now();
}
$('#next').addEventListener('click',()=>changeSlide(target+1,true));$('#prev').addEventListener('click',()=>changeSlide(target-1,true));$$('[data-slide]').forEach(b=>b.addEventListener('click',()=>changeSlide(+b.dataset.slide,true)));
$('#pause').addEventListener('click',()=>{paused=!paused;focusPause=false;elapsed=0;pauseUI();});
document.addEventListener('pointerdown',()=>{keyboard=false;focusPause=false;},true);
document.addEventListener('keydown',e=>{if(e.key==='Tab')keyboard=true;},true);
scene.addEventListener('focusin',()=>{if(keyboard)focusPause=true;});scene.addEventListener('focusout',e=>{if(!scene.contains(e.relatedTarget))focusPause=false;});
scene.addEventListener('keydown',e=>{if(e.key==='ArrowLeft'||e.key==='ArrowRight'){e.preventDefault();focusPause=true;changeSlide(target+(e.key==='ArrowRight'?1:-1),true);}});
let touchX=0,touchY=0;scene.addEventListener('touchstart',e=>{touchX=e.changedTouches[0].clientX;touchY=e.changedTouches[0].clientY;},{passive:true});scene.addEventListener('touchend',e=>{const x=e.changedTouches[0].clientX-touchX,y=e.changedTouches[0].clientY-touchY;if(Math.abs(x)>55&&Math.abs(x)>Math.abs(y)*1.5)changeSlide(target+(x<0?1:-1),true);},{passive:true});
if('IntersectionObserver'in window)new IntersectionObserver(entries=>{visible=entries[0].isIntersecting&&entries[0].intersectionRatio>=.2;lastTick=performance.now();},{threshold:[0,.2]}).observe(scene);
reduce.addEventListener('change',()=>{if(reduce.matches){paused=true;art.getAnimations({subtree:true}).forEach(a=>a.cancel());}pauseUI();});
document.addEventListener('visibilitychange',()=>{lastTick=performance.now();});
const ticker=setInterval(()=>{const now=performance.now(),dt=Math.min(300,now-lastTick);lastTick=now;const running=!paused&&!focusPause&&visible&&!document.hidden&&!$('dialog[open]')&&!busy;scene.dataset.autoplay=paused?'paused':running?'playing':'suspended';if(running)elapsed+=dt;scene.style.setProperty('--scene-progress',String(Math.min(1,elapsed/interval)));if(running&&elapsed>=interval)changeSlide(target+1);},80);
addEventListener('pagehide',()=>clearInterval(ticker),{once:true});applyTheme(slides[0].key);pauseUI();scene.dataset.autoplay=paused?'paused':'playing';scene.dataset.busy='false';enterArtwork();
'''

JS=r'''
/* Two measured, seamless tracks. Duplicate logos are hidden from assistive tech. */
(()=>{
 'use strict';const root=document.querySelector('.brand-marquee'),button=document.getElementById('brands-pause');if(!root||!button)return;
 const reduce=matchMedia('(prefers-reduced-motion: reduce)');let paused=reduce.matches,hover=false,focus=false,visible=true;
 const rows=Array.from(root.querySelectorAll('.brand-row'));
 function measure(){for(const row of rows){const group=row.querySelector('.brand-original');const speed=innerWidth<761?32:42;row.querySelector('.brand-track').style.setProperty('--brand-duration',(group.getBoundingClientRect().width/speed)+'s');}}
 function update(){const modal=!!document.querySelector('dialog[open]');root.dataset.running=String(!paused&&!hover&&!focus&&visible&&!document.hidden&&!modal);root.dataset.static=String(reduce.matches&&paused);button.setAttribute('aria-pressed',String(paused));button.setAttribute('aria-label',paused?'Play scrolling brand logos':'Pause scrolling brand logos');button.querySelector('use').setAttribute('href',paused?'#icon-play':'#icon-pause');button.querySelector('span').textContent=paused?'Play':'Pause';}
 button.addEventListener('click',()=>{paused=!paused;update();});root.addEventListener('pointerenter',e=>{if(e.pointerType==='mouse'){hover=true;update();}});root.addEventListener('pointerleave',()=>{hover=false;update();});root.addEventListener('focusin',()=>{focus=true;update();});root.addEventListener('focusout',e=>{focus=root.contains(e.relatedTarget);update();});
 if('IntersectionObserver'in window)new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;update();}).observe(root);
 if('ResizeObserver'in window)new ResizeObserver(measure).observe(root);
 for(const dialog of document.querySelectorAll('dialog'))new MutationObserver(update).observe(dialog,{attributes:true,attributeFilter:['open']});
 reduce.addEventListener('change',()=>{if(reduce.matches)paused=true;update();});document.addEventListener('visibilitychange',update);measure();update();
})();
/* Masked editorial entrances, blur-fade panels, and pointer-relative card tilt. */
(()=>{
 'use strict';const reduce=matchMedia('(prefers-reduced-motion: reduce)'),fine=matchMedia('(hover: hover) and (pointer: fine)');const animated=new Set();
 function play(el,frames,options){if(reduce.matches||!el.animate)return;const a=el.animate(frames,options);animated.add(a);a.finished.then(()=>animated.delete(a)).catch(()=>animated.delete(a));return a;}
 const observer='IntersectionObserver'in window?new IntersectionObserver(entries=>{for(const item of entries){if(!item.isIntersecting)continue;observer.unobserve(item.target);if(reduce.matches)continue;const spans=item.target.querySelectorAll('.motion-word>span');spans.forEach((span,i)=>play(span,[{transform:'translateY(110%) rotate(2deg)'},{transform:'translateY(0) rotate(0deg)'}],{duration:850,delay:i*65,easing:'cubic-bezier(.22,1,.36,1)',fill:'backwards'}));}},{threshold:.3}):null;
 for(const heading of document.querySelectorAll('#work-title,#studio-title,#services-title,#contact-title')){
  const walk=document.createTreeWalker(heading,NodeFilter.SHOW_TEXT);const nodes=[];while(walk.nextNode())nodes.push(walk.currentNode);
  for(const node of nodes){const fragment=document.createDocumentFragment();for(const word of node.textContent.split(/(\s+)/)){if(!word)continue;if(/^\s+$/.test(word)){fragment.append(document.createTextNode(word));continue;}const mask=document.createElement('span'),inner=document.createElement('span');mask.className='motion-word';inner.textContent=word;mask.append(inner);fragment.append(mask);}node.replaceWith(fragment);}
  if(observer)observer.observe(heading);
 }
 for(const card of document.querySelectorAll('#work .work-picture')){
  let frame=0;function reset(){cancelAnimationFrame(frame);card.style.removeProperty('--tilt-x');card.style.removeProperty('--tilt-y');}
  card.addEventListener('pointermove',event=>{if(reduce.matches||!fine.matches||event.pointerType!=='mouse')return;cancelAnimationFrame(frame);const x=event.clientX,y=event.clientY;frame=requestAnimationFrame(()=>{const r=card.getBoundingClientRect();const rx=Math.max(-1,Math.min(1,(x-r.left-r.width/2)/(r.width/2))),ry=Math.max(-1,Math.min(1,(y-r.top-r.height/2)/(r.height/2)));card.style.setProperty('--tilt-x',(-ry*3.5)+'deg');card.style.setProperty('--tilt-y',(rx*3.5)+'deg');});});
  card.addEventListener('pointerleave',reset);card.addEventListener('blur',reset);reduce.addEventListener('change',reset);
 }
 for(const panel of document.querySelectorAll('.capability-panel'))new MutationObserver(()=>{if(panel.hidden||reduce.matches)return;panel.querySelectorAll('.capability-item').forEach((item,i)=>{item.getAnimations().forEach(a=>a.cancel());play(item,[{opacity:.1,transform:'translateY(12px)',filter:'blur(4px)'},{opacity:1,transform:'translateY(0)',filter:'blur(0px)'}],{duration:440,delay:i*65,easing:'cubic-bezier(.22,1,.36,1)',fill:'backwards'});});}).observe(panel,{attributes:true,attributeFilter:['hidden']});
 reduce.addEventListener('change',()=>{if(reduce.matches)for(const a of animated)a.cancel();});
})();
'''

def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def once(pattern,replacement,text,label):
 value,n=re.subn(pattern,lambda _:replacement,text,count=1,flags=re.S)
 if n!=1:raise ValueError('Expected one '+label)
 return value

def prepare():
 v4=module('cma_client_v4',HERE/'client_update.py')
 if VERSION in (HERE/'site.html').read_text():return v4.ensure_assets()
 assets,manifest=v4.prepare();html=(HERE/'site.html').read_text();css=(HERE/'site.css').read_text();js=(HERE/'site.js').read_text()
 if OLD not in html:raise ValueError('Expected approved v4 input')
 html=html.replace('<div class="scene-bottom">','<div class="scene-timer" aria-hidden="true"><span></span></div><div class="scene-bottom">',1)
 m=re.search(r'<ul class="profile-logo-grid"[^>]*>(.*?)</ul>',html,re.S)
 if not m:raise ValueError('Missing authentic profile logo list')
 items=re.findall(r'<li>.*?</li>',m[1],re.S)
 if len(items)!=39:raise ValueError('Expected all 39 supplied profile logos')
 rows=[]
 for i,group in enumerate((items[::2],items[1::2])):
  originals=''.join(group)
  clones=re.sub(r'alt="[^"]*"','alt=""',originals)
  rows.append('<div class="brand-row" tabindex="0" role="group" aria-label="Brand logos, row '+str(i+1)+'"><div class="brand-track"><ul class="brand-strip brand-original profile-logo-grid" aria-label="Brands, row '+str(i+1)+'">'+originals+'</ul><ul class="brand-strip brand-duplicate" aria-hidden="true" inert>'+clones+'</ul></div></div>')
 marquee='<div class="brand-marquee" data-running="false" data-static="true">'+''.join(rows)+'</div>'
 html=html[:m.start()]+marquee+html[m.end():]
 html=once(r'(<button type="button" id="profile-slide-open".*?</button>)','<div class="brand-actions"><button class="brands-pause" id="brands-pause" type="button" aria-pressed="false" aria-label="Pause scrolling brand logos"><svg class="icon" aria-hidden="true"><use href="#icon-pause"/></svg><span>Pause</span></button>'+re.search(r'<button type="button" id="profile-slide-open".*?</button>',html,re.S)[0]+'</div>',html,'brands control')
 # Original artwork and approved marketing copy are retained.
 html=html.replace('Google Fonts supplies the website typeface and receives the technical information required to deliver it. ','The website typeface is served with the site. ')
 js=once(r'let slide=0,paused=reduce.matches.*?(?=const sections=)',CONTROLLER+'\n',js,'previous carousel controller')
 js+='\n'+JS
 html=html.replace(OLD,VERSION).replace('</body>','<!--\n'+NOTICES+'-->\n</body>')
 test=(HERE/'test_browser.py').read_text().replace(OLD,VERSION)
 # Dialog close is an asynchronous native event; wait for it before the existing assertions.
 test=re.sub(r"(?m)^([ \t]*)page\.keyboard\.press\('Escape'\)\n",lambda m:m[0]+m[1]+"page.wait_for_timeout(80)\n",test)
 compile(test,'test_browser.py','exec')
 for name,content in [('site.html',html),('site.css',css+'\n'+CSS),('site.js',js),('test_browser.py',test),('build.py',(HERE/'build.py').read_text().replace(OLD,VERSION))]:(HERE/name).write_text(content,encoding='utf-8')
 return assets,manifest

def logo_cutout(source,destination):
    """Recover alpha from the supplied black-matted mark before downsampling.

    The three original foreground colours are sampled from this exact logo.
    No traced/recreated lettering or replacement artwork is used.
    """
    from PIL import Image
    original=Image.open(source).convert('RGB')
    palette=((255,255,255),(79,138,205),(45,68,126))
    denominators=[sum(c*c for c in colour) for colour in palette]
    def pixel(p):
        if max(p)<=9:return (0,0,0,0)
        best=None
        for colour,den in zip(palette,denominators):
            a=min(1.,max(0.,sum(x*y for x,y in zip(p,colour))/den))
            error=sum((x-a*y)**2 for x,y in zip(p,colour))
            if best is None or error<best[0]:best=(error,colour,a)
        _,colour,a=best
        if a<.035:return (0,0,0,0)
        # Preserve fully opaque source colour; unmatte only antialiased edges.
        rgb=p if a>.98 else colour
        return (*rgb,round(a*255))
    output=Image.new('RGBA',original.size);output.putdata([pixel(p) for p in original.getdata()])
    output.thumbnail((672,576),Image.Resampling.LANCZOS)
    output.putalpha(output.getchannel('A').point(lambda a: 0 if a < 3 else a))
    output.save(destination,format='PNG',optimize=True)
    return {'file':'/media/'+destination.name,'method':'original black-matte alpha extraction','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'sha256':hashlib.sha256(destination.read_bytes()).hexdigest()}

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--assets-source',type=Path,default=HERE.parent/'dist'/'index.html');parser.add_argument('--output-dir',type=Path,default=HERE.parent/'release');args=parser.parse_args()
 assets,client=prepare();builder=module('cma_motion_builder',HERE/'build.py');manifest=builder.build(args.assets_source,args.output_dir,HERE/'site.html')
 logo_record=next(r for r in manifest['assets'] if r['key']=='logo')
 logo_source=args.output_dir/logo_record['file'].lstrip('/')
 cutout=logo_cutout(logo_source,args.output_dir/'media'/'cma-logo-transparent.png')
 built=(args.output_dir/'index.html').read_text()
 built=built.replace(logo_record['file'],cutout['file'])
 (args.output_dir/'index.html').write_text(built,encoding='utf-8')
 manifest['logo_derivative']=cutout
 manifest['html_sha256']=hashlib.sha256(built.encode()).hexdigest()
 target=args.output_dir/'media'/'client';target.mkdir(parents=True,exist_ok=True)
 for record in client['logos']+[client['slide']]:shutil.copyfile(assets/record['file'],target/record['file'])
 manifest['client_identity']={'font_family':'Optima','profile_source_page':7,'logo_count':39,'font_source_sha256':client['font']['source_sha256'],'approved_agency_copy':'A full service wholly owned Zimbabwean advertising agency based in Newlands, Harare, Zimbabwe.'}
 manifest['motion']={'version':VERSION,'hero_interval_ms':6000,'hero_themes':['Nightsky blue','Gold Blend Whisky amber','Whitestone botanical green'],'brand_rows':2,'unique_brand_logos':39,'decorative_duplicates_hidden':True,'original_logo_rendered_without_black_matte':True,'source_libraries':['Magic UI Marquee','Magic UI Blur Fade','React Bits TiltedCard'],'reduced_motion_supported':True}
 (args.output_dir/'build-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(args.output_dir/'MOTION_NOTICES.txt').write_text(NOTICES)
 print('CMA_MOTION_RELEASE '+json.dumps(manifest['motion']))

if __name__=='__main__':main()
