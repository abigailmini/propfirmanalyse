(function(){
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const PORDER={daily:1,weekly:2,biweekly:3,monthly:4,other:5};
/* sort keys: [value fn (null = unpublished, always last), default direction] */
const SK={score:[d=>+d.score,-1],name:[d=>d.name,1],tp:[d=>d.tp===''?null:+d.tp,-1],fee:[d=>d.fee===''?null:+d.fee,1],maxsize:[d=>d.maxsize===''?null:+d.maxsize,-1],
  split:[d=>d.split===''?null:+d.split,-1],payout:[d=>PORDER[d.payout]||null,1],founded:[d=>d.founded===''?null:+d.founded,1]};
function sortTable(t,k,dir){
  const tb=$('tbody',t),s=SK[k]||SK.score;dir=dir||s[1];
  [...tb.rows].sort((a,b)=>{const x=s[0](a.dataset),y=s[0](b.dataset);if(x===y)return (+b.dataset.score)-(+a.dataset.score);if(x==null)return 1;if(y==null)return -1;return (x<y?-1:1)*dir}).forEach(r=>tb.appendChild(r));
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
  sortTable(t,k,dir);t.dispatchEvent(new CustomEvent('pfa:sort',{detail:{k,dir}}));
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

/* table filters */
const tb=$('#firms tbody'),form=$('#filters');
if(tb&&form){
  const rows=$$('tr',tb),ids=['q','f-asset','f-type','f-size','f-plat','f-fee','f-split','f-payout','f-country','f-news','f-weekend','f-sort'];
  const more=$('#f-more'),act=$('#f-active'),empty=$('#empty');
  const P=new URLSearchParams(location.search);
  ids.forEach(i=>{const el=$('#'+i),v=P.get(i.replace('f-',''));if(el&&v!=null){el.type==='checkbox'?el.checked=v==='1':el.value=v}});
  const order=PORDER,tbl=$('#firms');let dir=P.get('dir')==='asc'?1:P.get('dir')==='desc'?-1:null;
  tbl.addEventListener('pfa:sort',e=>{$('#f-sort').value=e.detail.k;dir=e.detail.dir;run()});
  $('#f-sort').addEventListener('change',()=>{dir=null});
  const v=i=>{const el=$('#'+i);return el.type==='checkbox'?el.checked:el.value.trim().toLowerCase()};
  const setOpen=o=>{form.classList.toggle('open',o);more.setAttribute('aria-expanded',o?'true':'false')};
  function run(){
    let n=0;
    rows.forEach(r=>{const d=r.dataset;let ok=true;
      if(v('q')&&!d.name.includes(v('q')))ok=false;
      if(v('f-asset')&&!d.assets.split(' ').includes(v('f-asset')))ok=false;
      if(v('f-type')&&!d.types.split(' ').includes(v('f-type')))ok=false;
      if(v('f-size')&&!(+d.maxsize>=+v('f-size')))ok=false;
      if(v('f-plat')&&!d.platforms.split('|').includes(v('f-plat')))ok=false;
      if(v('f-fee')&&!(d.fee!==''&&+d.fee<=+v('f-fee')))ok=false;
      if(v('f-split')&&!(+d.split>=+v('f-split')))ok=false;
      if(v('f-payout')&&!(d.payout&&order[d.payout]<=order[v('f-payout')]))ok=false;
      if(v('f-country')&&d.restricted.split('|').includes(v('f-country')))ok=false;
      if(v('f-news')&&d.news!=='true')ok=false;
      if(v('f-weekend')&&d.weekend!=='true')ok=false;
      r.hidden=!ok;if(ok)n++});
    const s=v('f-sort')||'score';sortTable(tbl,s,dir);
    $('#count').textContent=n+' of '+rows.length+' firms'+(v('f-country')?', excluding firms that restrict your country':'');
    if(empty)empty.hidden=n!==0;
    const active=ids.filter(i=>i!=='q'&&i!=='f-sort'&&v(i)).length;
    act.hidden=!active;act.textContent=active;
    const q=new URLSearchParams();ids.forEach(i=>{const x=v(i);if(x&&x!==false&&!(i==='f-sort'&&x==='score'))q.set(i.replace('f-',''),x===true?'1':x)});
    if(dir&&dir!==SK[s][1])q.set('dir',dir>0?'asc':'desc');
    history.replaceState(null,'',q.toString()?'?'+q:location.pathname);
  }
  const reset=()=>{ids.forEach(i=>{const el=$('#'+i);el.type==='checkbox'?el.checked=false:el.value=i==='f-sort'?'score':''});dir=null;run()};
  ids.forEach(i=>{const el=$('#'+i);el&&el.addEventListener(i==='q'?'input':'change',run)});
  more.addEventListener('click',()=>setOpen(more.getAttribute('aria-expanded')!=='true'));
  $('#f-reset').addEventListener('click',reset);
  $$('[data-reset]').forEach(b=>b.addEventListener('click',()=>{reset();$('#q').focus()}));
  if(['size','plat','payout','country','news','weekend'].some(k=>P.has(k)))setOpen(true);
  run();
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
    const R=[['PFA Score',x=>x.pfa_score,1],['Trustpilot',x=>x.trustpilot&&x.trustpilot.score,1],['Founded',x=>x.founded],['HQ',x=>x.hq],['Markets',x=>x.assets],['Challenge types',x=>x.challenge_types],['Fee from',x=>x.fee_from!=null?'$'+x.fee_from:null],['Profit target',x=>x.profit_target],['Daily loss',x=>x.max_daily_loss],['Max drawdown',x=>x.max_drawdown],['Drawdown type',x=>x.drawdown_type],['Profit split',x=>x.profit_split],['Leverage',x=>x.leverage],['Platforms',x=>x.platforms],['Payout frequency',x=>x.payout_frequency],['First payout (days)',x=>x.first_payout_days],['Consistency rule',x=>x.consistency_rule],['News trading',x=>x.news_trading],['Weekend holding',x=>x.weekend_holding],['Discount code',x=>x.discount_code&&x.discount_code.code]];
    const cell=(x,w)=>'<td'+(w?' class="win"':'')+'><span class="v">'+f(x)+'</span>'+(w?'<span class="sr"> (stronger figure)</span>':'')+'</td>';
    const head=X=>'<th scope="col"><a class="fn" href="'+window.PFA_BASE+'/firms/'+X.slug+'/">'+esc(X.name)+'</a></th>';
    $('#live').innerHTML='<table class="cmp"><caption class="sr">'+esc(A.name)+' compared with '+esc(B.name)+'</caption><thead><tr><td></td>'+head(A)+head(B)+'</tr></thead><tbody>'+R.map(r=>{const x=r[1](A),y=r[1](B);let wa=0,wb=0;if(r[2]&&x!=null&&y!=null&&x!==y){if(+x>+y)wa=1;else wb=1}return '<tr><th scope="row">'+r[0]+'</th>'+cell(x,wa)+cell(y,wb)+'</tr>'}).join('')+'</tbody></table>';
  }
  pk.addEventListener('submit',e=>{e.preventDefault();go()});
}
})();
