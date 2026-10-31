(function(){
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const PORDER={daily:1,weekly:2,biweekly:3,monthly:4,other:5};
/* sort keys: [value fn (null = unpublished, always last), default direction] */
const SK={score:[d=>+d.score,-1],name:[d=>d.name,1],tp:[d=>d.tp===''?null:+d.tp,-1],fee:[d=>d.fee===''?null:+d.fee,1],maxsize:[d=>d.maxsize===''?null:+d.maxsize,-1],
  split:[d=>d.split===''?null:+d.split,-1],payout:[d=>PORDER[d.payout]||null,1],founded:[d=>d.founded===''?null:+d.founded,1]};
const RM=matchMedia('(prefers-reduced-motion: reduce)');
/* FLIP: rows glide to their new position after a sort or filter (transform only, 240ms) */
function flip(tb,mutate){
  const rows=[...tb.rows];
  if(RM.matches||rows.length>80||!('animate' in Element.prototype)){mutate();return}
  const before=new Map();rows.forEach(r=>{if(!r.hidden)before.set(r,r.getBoundingClientRect().top)});
  mutate();
  const vh=innerHeight;
  rows.forEach(r=>{
    if(r.hidden)return;const top=r.getBoundingClientRect().top;
    if(!before.has(r)){if(top<vh&&top>-60)r.animate([{opacity:0},{opacity:1}],{duration:180,easing:'ease-out'});return}
    const d=before.get(r)-top;if(!d||Math.abs(d)>vh*1.5||top>vh||top<-200)return;
    r.animate([{transform:'translateY('+d+'px)'},{transform:'none'}],{duration:240,easing:'cubic-bezier(.77,0,.175,1)'});
  });
}
let animSort=false;
function sortTable(t,k,dir){
  const tb=$('tbody',t),s=SK[k]||SK.score;dir=dir||s[1];
  const doSort=()=>[...tb.rows].sort((a,b)=>{const x=s[0](a.dataset),y=s[0](b.dataset);if(x===y)return (+b.dataset.score)-(+a.dataset.score);if(x==null)return 1;if(y==null)return -1;return (x<y?-1:1)*dir}).forEach(r=>tb.appendChild(r));
  animSort?flip(tb,doSort):doSort();
  $$('th[data-sort]',t).forEach(th=>{th.dataset.sort===k?th.setAttribute('aria-sort',dir>0?'ascending':'descending'):th.removeAttribute('aria-sort')});
  t.dataset.k=k;t.dataset.dir=dir;
}
/* sticky table head sits under the sticky filter bar */
const fb=$('#filters');
if(fb&&'ResizeObserver' in window){new ResizeObserver(()=>document.documentElement.style.setProperty('--fh',fb.offsetHeight+'px')).observe(fb)}
/* header clicks: same key toggles direction */
$$('table.firms').forEach(t=>t.addEventListener('click',e=>{
  const th=e.target.closest('th[data-sort]');if(!th)return;
  const k=th.dataset.sort,dir=t.dataset.k===k?-(+t.dataset.dir):SK[k][1];
  if(t.id==='firms'&&$('#filters')){t.dispatchEvent(new CustomEvent('pfa:sort',{detail:{k,dir}}));return}
  animSort=true;sortTable(t,k,dir);
}));

/* menu */
const mb=$('#menu');
if(mb){
  const set=o=>{document.body.classList.toggle('nav-open',o);mb.setAttribute('aria-expanded',o?'true':'false')};
  mb.addEventListener('click',()=>set(mb.getAttribute('aria-expanded')!=='true'));
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&document.body.classList.contains('nav-open')){set(false);mb.focus()}});
}

/* copy discount codes */
document.addEventListener('click',e=>{
  const b=e.target.closest('[data-copy]');if(!b)return;
  navigator.clipboard&&navigator.clipboard.writeText(b.dataset.copy);
  const s=b.querySelector('span');if(!s)return;
  if(!b.dataset.orig)b.dataset.orig=s.textContent;
  b.classList.add('ok');s.textContent='Copied';
  clearTimeout(b._t);b._t=setTimeout(()=>{s.textContent=b.dataset.orig;b.classList.remove('ok')},1400);
});

/* table filters: account-type tabs + multi-select facets (OR inside a facet, AND across facets); state lives in the URL */
const tb=$('#firms tbody'),form=$('#filters');
if(tb&&form){
  const rows=$$('tr',tb),tbl=$('#firms'),more=$('#f-more'),act=$('#f-active'),empty=$('#empty'),chipsEl=$('#achips'),hub=$('#cats-hub');
  const SEL=['f-country','f-fee','f-size','f-sort'],TOG=['f-news','f-weekend'],GROUPS=['plat','mkt','type','pay','pm'];
  const cb=n=>$$('input[name="'+n+'"]',form),radio=n=>{const r=$('input[name="'+n+'"]:checked',form);return r?r.value:''};
  const P=new URLSearchParams(location.search);
  /* links shared before 2026-10-31 used single selects: asset, payout ("or faster"), plat (platform name) */
  const legPlat=x=>{x=x.toLowerCase();return /mt5|metatrader 5/.test(x)?'mt5':/mt4|metatrader 4/.test(x)?'mt4':/ctrader/.test(x)?'ctrader':/dx ?trade/.test(x)?'dxtrade':/match/.test(x)?'matchtrader':/tradovate/.test(x)?'tradovate':/rithmic|r \| trader/.test(x)?'rithmic':/ninja/.test(x)?'ninjatrader':/bybit|blofin/.test(x)?'exchange':x};
  if(P.has('asset')&&!P.has('mkt'))P.set('mkt',P.get('asset')==='commodities'?'gold':P.get('asset'));
  if(P.has('payout')&&!P.has('pay'))P.set('pay',{daily:'daily',weekly:'daily,weekly',biweekly:'daily,weekly,biweekly'}[P.get('payout')]||'');
  if(P.has('plat'))P.set('plat',P.get('plat').split(',').map(legPlat).join(','));
  if(P.get('split')==='100')P.set('split','90');
  GROUPS.forEach(g=>{const vs=(P.get(g)||'').split(',').filter(Boolean);cb(g).forEach(i=>{i.checked=vs.includes(i.value)})});
  const pick=(n,val)=>{const r=cb(n).find(i=>i.value===(val||''));if(r)r.checked=true};
  pick('split',P.get('split'));pick('cat',P.get('cat'));
  SEL.concat('q').forEach(i=>{const el=$('#'+i),x=P.get(i.replace('f-',''));if(el&&x!=null)el.value=x});
  TOG.forEach(i=>{const el=$('#'+i);if(el)el.checked=P.get(i.replace('f-',''))==='1'});
  let dir=P.get('dir')==='asc'?1:P.get('dir')==='desc'?-1:null;
  const v=i=>{const el=$('#'+i);return !el?'':el.type==='checkbox'?el.checked:el.value.trim().toLowerCase()};
  const lab=i=>{const t=i.nextElementSibling.textContent.replace(/\s*\(.*\)$/,'').replace(' or more','+');return i.name==='split'?'Split '+t:t};
  const setOpen=o=>{form.classList.toggle('open',o);more.setAttribute('aria-expanded',o?'true':'false')};
  tbl.addEventListener('pfa:sort',e=>{$('#f-sort').value=e.detail.k;dir=e.detail.dir;run()});
  function run(){
    const c=radio('cat'),q=v('q'),split=radio('split'),F={};GROUPS.forEach(g=>F[g]=cb(g).filter(i=>i.checked).map(i=>i.value));
    const any=(want,have)=>!want.length||want.some(x=>have.includes(x));
    let n=0;
    rows.forEach(r=>{const d=r.dataset;let ok=true;
      if(c&&d.cat!==c)ok=false;
      if(ok&&q&&!d.name.includes(q))ok=false;
      if(ok&&!(any(F.plat,d.pk.split(' '))&&any(F.mkt,d.mk.split(' '))&&any(F.type,d.types.split(' '))&&any(F.pay,[d.payout])&&any(F.pm,d.pm.split(' '))))ok=false;
      if(ok&&split&&!(+d.split>=+split))ok=false;
      if(ok&&v('f-size')&&!(+d.maxsize>=+v('f-size')))ok=false;
      if(ok&&v('f-fee')&&!(d.fee!==''&&+d.fee<=+v('f-fee')))ok=false;
      if(ok&&v('f-country')&&d.restricted.split('|').includes(v('f-country')))ok=false;
      if(ok&&v('f-news')&&d.news!=='true')ok=false;
      if(ok&&v('f-weekend')&&d.weekend!=='true')ok=false;
      r.dataset.ok=ok?'1':'';if(ok)n++});
    const s=v('f-sort')||'score';
    const apply=()=>{rows.forEach(r=>{r.hidden=!r.dataset.ok});const a=animSort;animSort=false;sortTable(tbl,s,dir);animSort=a};
    animSort?flip(tb,apply):apply();animSort=true;
    $('#count').textContent=n+' of '+rows.length+' firms'+(v('f-country')?', excluding firms that restrict your country':'');
    if(empty)empty.hidden=n!==0;
    /* facet buttons show their selection */
    $$('.ms',form).forEach(m=>{const on=$$('input:checked',m).filter(i=>i.value!=='');const mv=$('.mv',m);
      mv.textContent=!on.length?'Any':on.length<3?on.map(lab).join(', '):on.length+' selected';m.classList.toggle('on',on.length>0)});
    /* removable chips for everything active */
    const on=$$('.ms input:checked',form).filter(i=>i.value!=='');
    const extra=['f-country','f-fee','f-size'].filter(i=>v(i)).map(i=>({id:i,t:$('#'+i).selectedOptions[0].textContent})).concat(TOG.filter(i=>v(i)).map(i=>({id:i,t:$('#'+i).nextElementSibling.textContent})));
    chipsEl.innerHTML='';
    on.forEach(i=>{const b=document.createElement('button');b.type='button';b.className='chip';b.innerHTML='<span></span><svg viewBox="0 0 10 10" aria-hidden="true"><path d="M2 2l6 6M8 2 2 8" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>';
      b.firstChild.textContent=lab(i);b.setAttribute('aria-label','Remove filter: '+lab(i));b.onclick=()=>{if(i.type==='radio')pick(i.name,'');else i.checked=false;run();(chipsEl.querySelector('.chip')||$('#q')).focus()};chipsEl.appendChild(b)});
    extra.forEach(x=>{const b=document.createElement('button');b.type='button';b.className='chip';b.innerHTML='<span></span><svg viewBox="0 0 10 10" aria-hidden="true"><path d="M2 2l6 6M8 2 2 8" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>';
      b.firstChild.textContent=x.t;b.setAttribute('aria-label','Remove filter: '+x.t);b.onclick=()=>{const el=$('#'+x.id);el.type==='checkbox'?el.checked=false:el.value='';run();(chipsEl.querySelector('.chip')||$('#q')).focus()};chipsEl.appendChild(b)});
    chipsEl.hidden=!chipsEl.children.length;
    const active=on.length+extra.length;act.hidden=!active;act.textContent=active;
    if(hub){const r=$('input[name="cat"]:checked',form);if(c&&r&&r.dataset.hub){hub.href=r.dataset.hub;hub.textContent=r.dataset.hubt;hub.hidden=false}else hub.hidden=true}
    /* URL: comma-separated multi-select values */
    const u=new URLSearchParams();
    if(c)u.set('cat',c);if(q)u.set('q',q);
    GROUPS.forEach(g=>{if(F[g].length)u.set(g,F[g].join(','))});if(split)u.set('split',split);
    ['f-country','f-fee','f-size'].forEach(i=>{if(v(i))u.set(i.slice(2),v(i))});TOG.forEach(i=>{if(v(i))u.set(i.slice(2),'1')});
    if(s!=='score')u.set('sort',s);if(dir&&dir!==SK[s][1])u.set('dir',dir>0?'asc':'desc');
    history.replaceState(null,'',u.toString()?'?'+u.toString().replace(/%2C/g,','):location.pathname);
  }
  const reset=()=>{GROUPS.forEach(g=>cb(g).forEach(i=>{i.checked=false}));pick('split','');$('#q').value='';
    ['f-country','f-fee','f-size'].forEach(i=>{$('#'+i).value=''});TOG.forEach(i=>{$('#'+i).checked=false});$('#f-sort').value='score';dir=null;run()};
  form.addEventListener('change',e=>{if(e.target.id==='f-sort')dir=null;run()});
  $('#q').addEventListener('input',run);
  more.addEventListener('click',()=>setOpen(more.getAttribute('aria-expanded')!=='true'));
  $('#f-reset').addEventListener('click',reset);
  $$('[data-reset]').forEach(b=>b.addEventListener('click',()=>{reset();$('#q').focus()}));
  /* facet popovers: one open at a time; Escape or a click outside closes and returns focus */
  const dets=$$('.ms details',form);
  dets.forEach(d=>d.addEventListener('toggle',()=>{if(d.open)dets.forEach(o=>{if(o!==d)o.open=false})}));
  document.addEventListener('click',e=>{dets.forEach(d=>{if(d.open&&!d.contains(e.target))d.open=false})});
  form.addEventListener('keydown',e=>{if(e.key!=='Escape')return;const d=dets.find(x=>x.open);if(d){d.open=false;$('summary',d).focus();e.stopPropagation()}});
  const mob=matchMedia('(max-width:899px)').matches;
  if(['fee','size','news','weekend'].some(k=>P.has(k))||(mob&&['plat','mkt','type','pay','pm','split','country'].some(k=>P.get(k))))setOpen(true);
  run();
}

/* hero figures count up once on first view (text is final in the HTML; this only animates it) */
const cnt=$$('[data-count]');
if(cnt.length&&!RM.matches&&'IntersectionObserver' in window){
  const run1=el=>{const to=+el.dataset.count;if(!(to>1))return;el.style.display='inline-block';el.style.minWidth=el.offsetWidth+'px';
    const t0=performance.now(),D=900,ease=p=>1-Math.pow(2,-10*p);
    const step=t=>{const p=Math.min(1,(t-t0)/D);el.textContent=Math.round(to*ease(p));if(p<1)requestAnimationFrame(step);else el.textContent=to};
    el.textContent='0';requestAnimationFrame(step)};
  const io=new IntersectionObserver(es=>es.forEach(x=>{if(x.isIntersecting){io.unobserve(x.target);run1(x.target)}}),{threshold:.6});
  cnt.forEach(el=>io.observe(el));
}
/* one-time reveal for blocks that start below the fold */
const rv=$$('.rv');
if(rv.length&&'IntersectionObserver' in window){
  const io2=new IntersectionObserver(es=>es.forEach(x=>{if(x.isIntersecting){x.target.classList.remove('pre');io2.unobserve(x.target)}}),{rootMargin:'0px 0px -8% 0px'});
  rv.forEach(el=>{if(el.getBoundingClientRect().top>innerHeight){el.classList.add('pre');io2.observe(el)}});
}

/* compare picker */
const pk=$('#picker');
if(pk){
  const pa=$('#pa'),pb=$('#pb');pb.selectedIndex=Math.min(1,pb.options.length-1);
  let data=null;
  const esc=s=>String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const f=x=>x==null||x===''||(Array.isArray(x)&&!x.length)?'<span class="nil">Not published</span>':esc(Array.isArray(x)?x.join(', '):x===true?'Allowed':x===false?'Not allowed':x);
  async function go(){
    const a=pa.value,b=pb.value;if(a===b){$('#live').innerHTML='<p class="empty"><b>Pick two different firms.</b></p>';return}
    const slug=a+'-vs-'+b,rev=b+'-vs-'+a;
    if(window.PFA_PAIRS.includes(slug)){location.href=window.PFA_BASE+'/compare/'+slug+'/';return}
    if(window.PFA_PAIRS.includes(rev)){location.href=window.PFA_BASE+'/compare/'+rev+'/';return}
    $('#live').innerHTML='<p class="small">Loading data…</p>';
    try{data=data||(await (await fetch(window.PFA_FIRMS_URL)).json()).firms}catch(err){$('#live').innerHTML='<p class="empty"><b>Could not load the dataset.</b> Check your connection and try again.</p>';return}
    const A=data.find(x=>x.slug===a),B=data.find(x=>x.slug===b);
    const R=[['PA Score',x=>x.pa_score,1],['Trustpilot',x=>x.trustpilot&&x.trustpilot.score,1],['Founded',x=>x.founded],['HQ',x=>x.hq],['Markets',x=>x.assets],['Challenge types',x=>x.challenge_types],['Fee from',x=>x.fee_from!=null?'$'+x.fee_from:null],['Profit target',x=>x.profit_target],['Daily loss',x=>x.max_daily_loss],['Max drawdown',x=>x.max_drawdown],['Drawdown type',x=>x.drawdown_type],['Profit split',x=>x.profit_split],['Leverage',x=>x.leverage],['Platforms',x=>x.platforms],['Payout frequency',x=>x.payout_frequency],['First payout (days)',x=>x.first_payout_days],['Consistency rule',x=>x.consistency_rule],['News trading',x=>x.news_trading],['Weekend holding',x=>x.weekend_holding],['Discount code',x=>x.discount_code&&x.discount_code.code]];
    const cell=(x,w)=>'<td'+(w?' class="win"':'')+'><span class="v">'+f(x)+'</span>'+(w?'<span class="sr"> (stronger figure)</span>':'')+'</td>';
    const head=X=>'<th scope="col"><a class="fn" href="'+window.PFA_BASE+'/firms/'+X.slug+'/">'+esc(X.name)+'</a></th>';
    $('#live').innerHTML='<table class="cmp"><caption class="sr">'+esc(A.name)+' compared with '+esc(B.name)+'</caption><thead><tr><td></td>'+head(A)+head(B)+'</tr></thead><tbody>'+R.map(r=>{const x=r[1](A),y=r[1](B);let wa=0,wb=0;if(r[2]&&x!=null&&y!=null&&x!==y){if(+x>+y)wa=1;else wb=1}return '<tr><th scope="row">'+r[0]+'</th>'+cell(x,wa)+cell(y,wb)+'</tr>'}).join('')+'</tbody></table>';
  }
  pk.addEventListener('submit',e=>{e.preventDefault();go()});
}
})();
