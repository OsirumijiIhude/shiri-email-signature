// Single v8 section tracker. Active navigation is underline-only; state is aria-current.
const trackedSectionIds=['work','studio','services','contact'];
const trackedSections=trackedSectionIds.map(id=>document.getElementById(id)).filter(Boolean);
const trackedNavItems=Array.from(document.querySelectorAll('.nav-links a,.menu-list a')).filter(a=>trackedSectionIds.includes((a.getAttribute('href')||'').slice(1)));
let trackedFrame=0;
function trackedDocumentTop(element){return element.getBoundingClientRect().top+window.scrollY;}
function setTrackedActive(id){
  for(const link of trackedNavItems){
    const selected=id&&link.getAttribute('href')==='#'+id;
    link.classList.toggle('active',!!selected);
    if(selected)link.setAttribute('aria-current','location');
    else link.removeAttribute('aria-current');
  }
  document.documentElement.dataset.activeSection=id||'';
}
function track(){
  trackedFrame=0;
  // Opening a modal or the mobile menu must not change the section selected
  // underneath it. Recalculate when the dialog closes.
  if(document.querySelector('dialog[open]'))return;
  const header=document.querySelector('.header');
  const headerHeight=header?header.getBoundingClientRect().height:0;
  const viewport=window.innerHeight||document.documentElement.clientHeight;
  const y=window.scrollY||document.documentElement.scrollTop||0;
  const probe=y+headerHeight+Math.max(18,Math.min(72,viewport*.09));
  let active='';
  for(const section of trackedSections){
    if(trackedDocumentTop(section)<=probe+1)active=section.id;
    else break;
  }
  const doc=document.documentElement;
  if(y+viewport>=doc.scrollHeight-4&&y>0)active='contact';
  setTrackedActive(active);
}
function scheduleTrack(){
  if(trackedFrame)return;
  trackedFrame=requestAnimationFrame(track);
}
window.addEventListener('scroll',scheduleTrack,{passive:true});
document.addEventListener('scroll',scheduleTrack,{passive:true,capture:true});
for(const event of ['resize','orientationchange','hashchange','popstate','pageshow'])window.addEventListener(event,scheduleTrack);
document.addEventListener('load',scheduleTrack,true);
document.addEventListener('click',event=>{
  const link=event.target.closest('.nav-links a,.menu-list a');
  if(!link)return;
  const id=(link.getAttribute('href')||'').slice(1);
  if(!trackedSectionIds.includes(id))return;
  const target=document.getElementById(id);
  if(!target)return;
  // Own the anchor scroll. Native hash scrolling can be interrupted when the
  // mobile dialog closes, leaving the previous section selected.
  event.preventDefault();
  const header=document.querySelector('.header');
  const headerHeight=header?header.getBoundingClientRect().height:0;
  const top=Math.max(0,trackedDocumentTop(target)-headerHeight-8);
  if(location.hash!=='#'+id)history.pushState(null,'','#'+id);
  window.scrollTo(0,top);
  setTrackedActive(id);
  requestAnimationFrame(()=>requestAnimationFrame(track));
  setTimeout(track,80);
  setTimeout(track,250);
  setTimeout(track,650);
});
for(const dialog of document.querySelectorAll('dialog')){
  dialog.addEventListener('close',scheduleTrack);
  dialog.addEventListener('toggle',scheduleTrack);
}
if('ResizeObserver' in window){
  const observer=new ResizeObserver(scheduleTrack);
  for(const element of [document.documentElement,document.querySelector('.header'),...trackedSections])if(element)observer.observe(element);
}
if('MutationObserver' in window){
  new MutationObserver(scheduleTrack).observe(document.body,{attributes:true,attributeFilter:['open','hidden'],subtree:true});
}
if(document.fonts&&document.fonts.ready)document.fonts.ready.then(()=>{track();setTimeout(track,80);});
track();
setTimeout(track,80);
