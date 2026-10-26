/* PropAnalyse firm finder. Filters /data/firms.json in the browser. */
(function(){
const f=document.getElementById('quiz'),out=document.getElementById('qres');if(!f)return;let D=null;
const B=window.PFA_BASE||'',esc=s=>String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const val=n=>(f.querySelector('input[name='+n+']:checked')||{}).value||'';const musts=()=>[...f.querySelectorAll('input[name=must]:checked')].map(x=>x.value);
const tri=v=>v===true||/^(true|yes|allowed)$/i.test(String(v));
const PB={daily:1,weekly:.8,biweekly:.6,monthly:.3,other:.5};
async function run(){
  if(!D){try{D=(await (await fetch(window.PFA_FIRMS_URL)).json()).firms}catch(e){out.innerHTML='<p class="empty"><b>Could not load the dataset.</b> Check your connection and try again.</p>';return}}
  const mkt=val('mkt'),fee=+val('fee')||0,type=val('type'),size=+val('size')||0,pri=val('pri')||'score',m=musts(),ct=document.getElementById('q-ctry').value;
  const why=[];const ok=D.filter(x=>{
    const a=(x.assets||[]).map(s=>s.toLowerCase()),t=(x.challenge_types||[]).map(s=>s.toLowerCase()),pl=(x.platforms||[]).join(' ').toLowerCase();
    if(mkt&&!a.includes(mkt))return false;if(fee&&!(x.pa_fee_from!=null&&x.pa_fee_from<=fee))return false;if(type&&!t.includes(type))return false;
    if(size&&!(x.pa_max_size>=size))return false;if(m.includes('news')&&!tri(x.news_trading))return false;if(m.includes('weekend')&&!tri(x.weekend_holding))return false;
    if(m.includes('static')&&!/static/i.test(x.drawdown_type||''))return false;if(m.includes('mt5')&&!/mt5|metatrader 5/.test(pl))return false;
    if(ct&&(x.countries_restricted||[]).map(s=>s.toLowerCase()).includes(ct))return false;return true});
  const c=x=>x.pa_components||{},key={score:x=>x.pa_score,cost:x=>c(x).cost*2+x.pa_score/5,payout:x=>c(x).payout*2+x.pa_score/5,split:x=>(x.pa_split_max||0)/10+x.pa_score/5,trust:x=>c(x).trust*2+x.pa_score/5,rules:x=>c(x).rules*2+x.pa_score/5}[pri];
  ok.sort((a,b)=>key(b)-key(a));
  if(!ok.length){out.innerHTML='<div class="empty"><p><b>No firm meets every answer.</b> Loosen the budget, size or a must-have.</p></div>';return}
  const reason=x=>{const r=[];if(x.pa_fee_from!=null)r.push('from $'+x.pa_fee_from);if(x.profit_split)r.push(x.profit_split+' split');if(x.pa_payout_bucket)r.push({daily:'daily payouts',weekly:'weekly payouts',biweekly:'bi-weekly payouts',monthly:'monthly payouts',other:'payouts vary'}[x.pa_payout_bucket]);if(x.drawdown_type)r.push(x.drawdown_type+' drawdown');return r.join(' · ')};
  out.innerHTML='<p class="qcount"><b class="n">'+ok.length+'</b> of '+D.length+' firms fit. Top picks:</p><ol class="qtop">'+ok.slice(0,3).map((x,i)=>'<li><a href="'+B+'/firms/'+x.slug+'/"><span class="n qi">'+(i+1)+'</span><b>'+esc(x.name)+'</b><span class="n qs">'+x.pa_score.toFixed(1)+'</span><small>'+esc(reason(x))+'</small></a></li>').join('')+'</ol>'+
    (ok.length>3?'<p class="small">Also fit: '+ok.slice(3,12).map(x=>'<a href="'+B+'/firms/'+x.slug+'/">'+esc(x.name)+'</a>').join(', ')+(ok.length>12?' and '+(ok.length-12)+' more':'')+'.</p>':'')+
    '<p class="small">Ranked by '+({score:'PA Score',cost:'cost, then PA Score',payout:'payout speed, then PA Score',split:'split, then PA Score',trust:'track record, then PA Score',rules:'rule flexibility, then PA Score'}[pri])+'. <a href="'+B+'/tools/true-cost/?firm='+ok[0].slug+'">True cost of '+esc(ok[0].name)+'</a></p>';
}
f.addEventListener('change',run);document.getElementById('q-ctry').addEventListener('change',run);run();
})();
