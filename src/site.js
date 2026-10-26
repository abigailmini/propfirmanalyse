(function(){
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
document.addEventListener('click',e=>{const b=e.target.closest('[data-copy]');if(!b)return;navigator.clipboard&&navigator.clipboard.writeText(b.dataset.copy);b.classList.add('ok');const o=b.firstChild.textContent;b.firstChild.textContent='Copied';setTimeout(()=>{b.firstChild.textContent=o;b.classList.remove('ok')},1400)});
const tb=$('#firms tbody');
if(tb&&$('#filters')){
 const rows=$$('tr',tb),ids=['q','f-asset','f-type','f-size','f-plat','f-fee','f-split','f-payout','f-country','f-news','f-weekend','f-sort'];
 const P=new URLSearchParams(location.search);ids.forEach(i=>{const el=$('#'+i),v=P.get(i.replace('f-',''));if(el&&v!=null){el.type==='checkbox'?el.checked=v==='1':el.value=v}});
 const order={daily:1,weekly:2,biweekly:3,monthly:4,other:5};
 function run(){
  const v=i=>{const el=$('#'+i);return el.type==='checkbox'?el.checked:el.value.trim().toLowerCase()};
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
  const s=v('f-sort'),key={score:r=>-r.dataset.score,fee:r=>r.dataset.fee===''?1e9:+r.dataset.fee,split:r=>-(+r.dataset.split||0),tp:r=>-(+r.dataset.tp||0),founded:r=>+r.dataset.founded||9999,name:r=>r.dataset.name}[s]||(r=>-r.dataset.score);
  rows.slice().sort((a,b)=>{const x=key(a),y=key(b);return x<y?-1:x>y?1:0}).forEach(r=>tb.appendChild(r));
  $('#count').textContent=n+' of '+rows.length+' firms shown'+(v('f-country')?' (excluding firms that list your country as restricted)':'');
  const q=new URLSearchParams();ids.forEach(i=>{const x=v(i);if(x&&x!==false&&!(i==='f-sort'&&x==='score'))q.set(i.replace('f-',''),x===true?'1':x)});
  history.replaceState(null,'',q.toString()?'?'+q:location.pathname);
 }
 ids.forEach(i=>{const el=$('#'+i);el&&el.addEventListener(i==='q'?'input':'change',run)});
 $('#f-reset').addEventListener('click',()=>{ids.forEach(i=>{const el=$('#'+i);el.type==='checkbox'?el.checked=false:el.value=i==='f-sort'?'score':''});run()});
 run();
}
const pk=$('#picker');
if(pk){
 const pa=$('#pa'),pb=$('#pb');pb.selectedIndex=Math.min(1,pb.options.length-1);
 let data=null;
 const esc=s=>String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
 const f=(x)=>x==null||x===''||(Array.isArray(x)&&!x.length)?'<span class="na">Not published</span>':esc(Array.isArray(x)?x.join(', '):x===true?'Allowed':x===false?'Not allowed':x);
 async function go(){
  const a=pa.value,b=pb.value;if(a===b)return;
  const slug=a+'-vs-'+b,rev=b+'-vs-'+a;
  if(window.PFA_PAIRS.includes(slug)){location.href=window.PFA_BASE+'/compare/'+slug+'/';return}
  if(window.PFA_PAIRS.includes(rev)){location.href=window.PFA_BASE+'/compare/'+rev+'/';return}
  data=data||(await (await fetch(window.PFA_FIRMS_URL)).json()).firms;
  const A=data.find(x=>x.slug===a),B=data.find(x=>x.slug===b);
  const R=[['PFA Score',x=>x.pfa_score],['Trustpilot',x=>x.trustpilot&&x.trustpilot.score],['Founded',x=>x.founded],['HQ',x=>x.hq],['Markets',x=>x.assets],['Challenge types',x=>x.challenge_types],['Fee from',x=>x.fee_from!=null?'$'+x.fee_from:null],['Profit target',x=>x.profit_target],['Daily loss',x=>x.max_daily_loss],['Max drawdown',x=>x.max_drawdown],['Drawdown type',x=>x.drawdown_type],['Profit split',x=>x.profit_split],['Leverage',x=>x.leverage],['Platforms',x=>x.platforms],['Payout frequency',x=>x.payout_frequency],['First payout (days)',x=>x.first_payout_days],['Consistency rule',x=>x.consistency_rule],['News trading',x=>x.news_trading],['Weekend holding',x=>x.weekend_holding],['Discount code',x=>x.discount_code&&x.discount_code.code]];
  $('#live').innerHTML='<table class="cmp"><thead><tr><th></th><th><a href="'+window.PFA_BASE+'/firms/'+a+'/">'+esc(A.name)+'</a></th><th><a href="'+window.PFA_BASE+'/firms/'+b+'/">'+esc(B.name)+'</a></th></tr></thead><tbody>'+R.map(r=>'<tr><th>'+r[0]+'</th><td>'+f(r[1](A))+'</td><td>'+f(r[1](B))+'</td></tr>').join('')+'</tbody></table>';
 }
 $('#pgo').addEventListener('click',go);
}
})();