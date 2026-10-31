/* PropAnalyse calculators: shareable results. Inputs live in the URL (replaceState), so a copied link reopens the same result. Nothing is sent anywhere. */
(function(){
const root=document.querySelector('.calc');if(!root)return;
const tool=root.dataset.tool,$=s=>document.querySelector(s);
const els=()=>[...root.querySelectorAll('input[id],select[id]')];
const key=id=>id.replace(/^[a-z]-/,'');
const qs=new URLSearchParams(location.search);
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const txt=id=>(($('#'+id)||{}).textContent||'').trim();
const optText=id=>{const e=$('#'+id);return e&&e.selectedIndex>=0&&e.value?e.options[e.selectedIndex].textContent.trim():''};
let ready=false;
function write(){if(!ready)return;const p=new URLSearchParams();
  els().forEach(e=>{const k=key(e.id);if(e.type==='checkbox'){p.set(k,e.checked?'1':'0')}else if(e.value!==''&&!e.disabled){p.set(k,e.value)}});
  history.replaceState(null,'',location.pathname+'?'+p.toString());summary()}
async function waitFor(fn,ms){const t=Date.now();while(Date.now()-t<ms){if(fn())return true;await sleep(60)}return false}
async function restore(){
  if(![...qs.keys()].length){ready=true;summary();return}
  const firm=els().find(e=>/-firm$/.test(e.id));
  if(firm&&qs.get('firm')){
    if(tool!=='true-cost'||firm.value!==qs.get('firm')){firm.value=qs.get('firm');firm.dispatchEvent(new Event('change',{bubbles:true}))}
    const prog=$('#t-prog');
    if(prog){await waitFor(()=>!prog.disabled&&prog.options.length>0&&prog.value,4000);
      if(qs.get('prog')&&[...prog.options].some(o=>o.value===qs.get('prog'))){prog.value=qs.get('prog');prog.dispatchEvent(new Event('change',{bubbles:true}))}}
    await sleep(250);
  }
  els().forEach(e=>{const k=key(e.id);if(!qs.has(k)||/-(firm|prog)$/.test(e.id))return;
    if(e.type==='checkbox')e.checked=qs.get(k)==='1';else e.value=qs.get(k)});
  root.dispatchEvent(new Event('input',{bubbles:true}));root.dispatchEvent(new Event('change',{bubbles:true}));
  ready=true;summary();
}
function summary(){const el=$('#qw-sum');if(!el)return;let s='';
  const firm=optText(tool==='true-cost'?'t-firm':tool==='drawdown'?'d-firm':'p-firm');
  if(tool==='true-cost'){const pr=optText('t-prog').split(' · ');s=(firm?('Getting funded at '+firm+(pr[1]?' '+pr[1]:'')):'Getting funded')+' costs '+txt('o-net')+' out of pocket after '+(($('#t-att')||{}).value||1)+' attempt(s); break-even at '+txt('o-be')+' gross profit.'}
  else if(tool==='drawdown'){s=(firm?firm+': ':'')+'on a $'+Number((($('#d-size')||{}).value)||0).toLocaleString('en-US')+' account with '+(($('#d-type')||{}).value||'')+' drawdown, room before breach is '+txt('o-room')+' (binding floor '+txt('o-bind')+').'}
  else if(tool==='profit-target'){s=(firm?firm+': ':'')+'target '+txt('o-t1')+(txt('o-t2')&&txt('o-t2')!=='none'?' then '+txt('o-t2'):'')+', about '+txt('o-days')+'; payout at target '+txt('o-pay')+'.'}
  el.textContent=s;return s}
async function copy(t,msg){try{await navigator.clipboard.writeText(t);$('#qw-msg').textContent=msg}catch(e){window.prompt('Copy this link',t)}}
const sh=$('#qw-share'),cp=$('#qw-copy');
if(sh)sh.addEventListener('click',async()=>{ready=true;write();const s=summary(),u=location.href;
  if(navigator.share){try{await navigator.share({title:document.title,text:s,url:u});return}catch(e){if(e&&e.name==='AbortError')return}}
  copy(s+' '+u,'Result and link copied.')});
if(cp)cp.addEventListener('click',()=>{ready=true;write();copy(location.href,'Link copied. Anyone opening it sees this result.')});
let t;root.addEventListener('input',()=>{clearTimeout(t);t=setTimeout(write,200)});root.addEventListener('change',()=>{clearTimeout(t);t=setTimeout(write,200)});
restore();
})();
