// One scroll tracker owns the desktop and mobile active states.
const sections=['work','studio','services','contact'].map(id=>document.getElementById(id)).filter(Boolean);
const navItems=Array.from(document.querySelectorAll('.nav-links a,.menu-list a'));
let scrollPending=false;
function track(){
  scrollPending=false;
  // Keep the underlying section selected while a menu or project is open.
  if(document.querySelector('dialog[open]'))return;
  const header=document.querySelector('.header');
  const headerBottom=header?Math.max(0,header.getBoundingClientRect().bottom):0;
  const viewport=window.innerHeight||document.documentElement.clientHeight;
  const marker=Math.min(viewport-1,headerBottom+Math.min(120,Math.max(40,(viewport-headerBottom)*.18)));
  let active='';
  for(const section of sections){
    if(section.getBoundingClientRect().top<=marker)active=section.id;
  }
  const scroller=document.scrollingElement||document.documentElement;
  if(scroller.scrollTop+viewport>=scroller.scrollHeight-3&&scroller.scrollTop>0)active='contact';
  for(const link of navItems){
    const selected=active!==''&&link.getAttribute('href')==='#'+active;
    link.classList.toggle('active',selected);
    if(selected)link.setAttribute('aria-current','location');
    else link.removeAttribute('aria-current');
  }
  document.documentElement.dataset.activeSection=active;
}
function scheduleTrack(){
  if(!scrollPending){scrollPending=true;requestAnimationFrame(track);}
}
window.addEventListener('scroll',scheduleTrack,{passive:true});
document.addEventListener('scroll',scheduleTrack,{passive:true,capture:true});
for(const event of ['resize','orientationchange','hashchange','popstate','pageshow'])window.addEventListener(event,scheduleTrack);
document.addEventListener('load',scheduleTrack,true);
for(const dialog of document.querySelectorAll('dialog')){
  dialog.addEventListener('close',scheduleTrack);
  dialog.addEventListener('toggle',scheduleTrack);
}
if('ResizeObserver' in window){
  const observer=new ResizeObserver(scheduleTrack);
  for(const element of [document.documentElement,document.querySelector('.header'),...sections])if(element)observer.observe(element);
}
if('MutationObserver' in window){
  new MutationObserver(scheduleTrack).observe(document.body,{attributes:true,attributeFilter:['open','hidden'],subtree:true});
}
if(document.fonts&&document.fonts.ready)document.fonts.ready.then(scheduleTrack);
scheduleTrack();
