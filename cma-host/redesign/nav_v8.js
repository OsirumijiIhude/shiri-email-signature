// Single v8 section tracker. Active navigation is underline-only; state is aria-current.
(() => {
  'use strict';
  const ids=['work','studio','services','contact'];
  const sections=ids.map(id=>document.getElementById(id)).filter(Boolean);
  const links=Array.from(document.querySelectorAll('.nav-links a,.menu-list a')).filter(a=>ids.includes((a.getAttribute('href')||'').slice(1)));
  let frame=0;
  function documentTop(element){return element.getBoundingClientRect().top+window.scrollY;}
  function setActive(id){
    for(const link of links){
      const selected=id && link.getAttribute('href')==='#'+id;
      link.classList.toggle('active',!!selected);
      if(selected)link.setAttribute('aria-current','location');
      else link.removeAttribute('aria-current');
    }
    document.documentElement.dataset.activeSection=id||'';
  }
  function resolve(){
    frame=0;
    const header=document.querySelector('.header');
    const headerHeight=header?header.getBoundingClientRect().height:0;
    const viewport=window.innerHeight||document.documentElement.clientHeight;
    const scrollY=window.scrollY||document.documentElement.scrollTop||0;
    const probe=scrollY+headerHeight+Math.max(18,Math.min(72,viewport*.09));
    let active='';
    for(const section of sections){
      if(documentTop(section)<=probe+1)active=section.id;
      else break;
    }
    const doc=document.documentElement;
    if(scrollY+viewport>=doc.scrollHeight-4 && scrollY>0)active='contact';
    setActive(active);
  }
  function schedule(){
    if(frame)return;
    frame=requestAnimationFrame(resolve);
  }
  window.addEventListener('scroll',schedule,{passive:true});
  document.addEventListener('scroll',schedule,{passive:true,capture:true});
  for(const event of ['resize','orientationchange','hashchange','popstate','pageshow'])window.addEventListener(event,schedule);
  document.addEventListener('load',schedule,true);
  document.addEventListener('click',event=>{
    const link=event.target.closest('.nav-links a,.menu-list a');
    if(!link)return;
    const id=(link.getAttribute('href')||'').slice(1);
    if(!ids.includes(id))return;
    setActive(id);
    requestAnimationFrame(()=>requestAnimationFrame(resolve));
    setTimeout(resolve,180);
    setTimeout(resolve,650);
  });
  for(const dialog of document.querySelectorAll('dialog')){
    dialog.addEventListener('close',schedule);
    dialog.addEventListener('toggle',schedule);
  }
  if('ResizeObserver' in window){
    const observer=new ResizeObserver(schedule);
    for(const element of [document.documentElement,document.querySelector('.header'),...sections])if(element)observer.observe(element);
  }
  if('MutationObserver' in window){
    new MutationObserver(schedule).observe(document.body,{attributes:true,attributeFilter:['open','hidden'],subtree:true});
  }
  if(document.fonts&&document.fonts.ready)document.fonts.ready.then(()=>{resolve();setTimeout(resolve,80);});
  // Legacy code after this injected block still calls track(); expose the resolver deliberately.\n  window.track=resolve;\n  window.scheduleTrack=schedule;\n  resolve();\n  setTimeout(resolve,80);\n})();
