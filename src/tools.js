/* PropAnalyse calculators. Data: /data/firms.json (loaded on demand). No tracking, nothing sent. */
(function(){
const $=s=>document.querySelector(s),root=document.querySelector('.calc');if(!root)return;
const tool=root.dataset.tool;let FIRMS=null;
const fmt=(v,c)=>{if(v==null||!isFinite(v))return'-';const s=(c==='EUR'?'€':'$'),a=Math.abs(v);return(v<0?'-':'')+s+a.toLocaleString('en-US',{maximumFractionDigits:a<100?2:0})};
const n=id=>{const v=parseFloat(($('#'+id)||{}).value);return isFinite(v)?v:0};
const set=(id,v)=>{const el=$('#'+id);if(el)el.textContent=v};
const pct=s=>{const m=String(s==null?'':s).match(/(\d+(?:\.\d+)?)\s*%/);return m?parseFloat(m[1]):null};
const maxpct=s=>{const m=[...String(s==null?'':s).matchAll(/(\d+(?:\.\d+)?)\s*%/g)].map(x=>+x[1]);return m.length?Math.max(...m):null};
async function data(){if(FIRMS)return FIRMS;try{FIRMS=(await (await fetch(window.PFA_FIRMS_URL)).json()).firms}catch(e){FIRMS=[]}return FIRMS}
function fill(id,v){const el=$('#'+id);if(el&&v!=null&&isFinite(v))el.value=v}
const qs=new URLSearchParams(location.search);

if(tool==='true-cost'){
  let cur='USD';
  const calc=()=>{
    const fee=n('t-fee'),d=n('t-disc')/100,att=Math.max(1,Math.round(n('t-att'))),retry=n('t-retry')/100,act=n('t-act'),split=n('t-split')/100,g=n('t-gross'),ref=$('#t-ref').checked;
    const first=fee*(1-d),spent=first+(att-1)*fee*(1-d)*retry+act,refund=ref?first*(att>1?retry:1):0,net=spent-refund;
    set('o-spent',fmt(spent,cur));set('o-ref',ref?fmt(refund,cur):'none');set('o-net',fmt(net,cur));set('o-be',split>0?fmt(net/split,cur):'-');set('o-keep',fmt(g*split-net,cur));
    $('#o-keep').classList.toggle('neg',g*split-net<0);
    set('o-note',att>1?('Includes '+(att-1)+' retr'+(att>2?'ies':'y')+' at '+Math.round(retry*100)+'% of the fee.'):'');
  };
  const prog=$('#t-prog');
  $('#t-firm').addEventListener('change',async e=>{
    const F=(await data()).find(x=>x.slug===e.target.value);prog.innerHTML='';
    if(!F){prog.disabled=true;prog.innerHTML='<option>Pick a firm first</option>';cur='USD';calc();return}
    cur=F.fee_currency||'USD';const x=F.extra||{};document.querySelectorAll('.ninp i').forEach(i=>{if(i.textContent==='$'||i.textContent==='€')i.textContent=cur==='EUR'?'€':'$'});
    (F.programs||[]).forEach((p,i)=>(p.sizes_fees||[]).forEach((s,j)=>{if(!s.fee)return;const o=document.createElement('option');o.value=i+':'+j;o.textContent=(p.name||p.type)+' · '+fmt(s.size).replace(/\.0+$/,'')+' · '+fmt(s.fee,cur);prog.appendChild(o)}));
    prog.disabled=!prog.options.length;
    const c=pct((F.discount_code||{}).value&&/off/i.test(F.discount_code.value)?F.discount_code.value:'');fill('t-disc',c||0);
    fill('t-retry',x.retry_discount_pct!=null?100-x.retry_discount_pct:100);fill('t-act',x.activation_fee||0);$('#t-ref').checked=x.fee_refundable===true;
    prog.dispatchEvent(new Event('change'));
  });
  prog.addEventListener('change',async()=>{const F=(await data()).find(x=>x.slug===$('#t-firm').value);if(!F||!prog.value)return calc();
    const[i,j]=prog.value.split(':').map(Number),p=F.programs[i],s=p.sizes_fees[j];fill('t-fee',s.fee);const sp=pct(p.profit_split)||pct(F.profit_split);if(sp)fill('t-split',sp);
    fill('t-gross',Math.round(s.size*0.05));calc()});
  root.addEventListener('input',calc);calc();
  if(qs.get('firm')){$('#t-firm').value=qs.get('firm');$('#t-firm').dispatchEvent(new Event('change'))}
}
if(tool==='drawdown'){
  const calc=()=>{
    const size=n('d-size'),dl=n('d-daily')/100,md=n('d-max')/100,type=$('#d-type').value,lock=$('#d-lock').checked,day=n('d-day'),hi=Math.max(n('d-high'),size),eq=n('d-eq');
    const dfl=dl>0?day-size*dl:-Infinity;let mfl=size-size*md;
    if(type!=='static'){mfl=hi-size*md;if(lock)mfl=Math.min(mfl,size)}
    const bind=Math.max(dfl,mfl),room=eq-bind;
    set('o-dfl',dl>0?fmt(dfl):'none');set('o-mfl',fmt(mfl));set('o-bind',fmt(bind)+(bind===dfl?' (daily)':' (overall)'));set('o-room',fmt(room)+' · '+(size?(room/size*100).toFixed(2):'0')+'%');
    $('#o-room').classList.toggle('neg',room<=0);
    const bar=$('#o-bar');if(bar)bar.style.setProperty('--w',Math.max(0,Math.min(1,room/(size*(md||0.1)))).toFixed(3));
    set('o-dnote',room<=0?'Equity is at or below the floor: this account would be breached.':(type!=='static'&&!lock?'The floor keeps trailing above your starting balance.':''));
  };
  $('#d-firm').addEventListener('change',async e=>{const F=(await data()).find(x=>x.slug===e.target.value);if(!F)return;
    const a=pct(F.max_daily_loss),b=pct(F.max_drawdown),t=String(F.drawdown_type||'').toLowerCase();if(a!=null)fill('d-daily',a);else fill('d-daily',0);if(b!=null)fill('d-max',b);
    $('#d-type').value=/eod|end/.test(t)?'eod':/trail/.test(t)?'trailing':'static';calc()});
  $('#d-size').addEventListener('change',()=>{['d-day','d-high','d-eq'].forEach(i=>fill(i,n('d-size')));calc()});
  root.addEventListener('input',calc);root.addEventListener('change',calc);calc();
}
if(tool==='profit-target'){
  const calc=()=>{
    const size=n('p-size'),t1=n('p-t1')/100,t2=n('p-t2')/100,sp=n('p-split')/100,avg=n('p-avg')/100,mn=Math.round(n('p-min'));
    const d=t=>t<=0?0:(avg>0?Math.max(mn,Math.ceil(t/avg)):Infinity);const days=d(t1)+d(t2);
    set('o-t1',fmt(size*t1));set('o-t2',t2>0?fmt(size*t2):'none');set('o-days',isFinite(days)?days+' trading days':'-');set('o-pay',fmt(size*t1*sp)+' for '+(t1*100).toFixed(1)+'% gross');
    set('o-pnote',avg>0?('At '+(avg*100).toFixed(2)+'% a day. About '+Math.ceil(days/21)+' month'+(Math.ceil(days/21)>1?'s':'')+' of trading.'):'Enter an average daily return above 0.');
  };
  $('#p-firm').addEventListener('change',async e=>{const F=(await data()).find(x=>x.slug===e.target.value);if(!F)return;
    const p=(F.programs||[]).find(p=>/2-step/i.test(p.type||''))||(F.programs||[])[0]||{};const m=String(p.profit_target||F.profit_target||'').match(/\d+(?:\.\d+)?/g)||[];
    fill('p-t1',m[0]?+m[0]:8);fill('p-t2',/2-step/i.test(p.type||'')&&m[1]?+m[1]:0);const s=pct(p.profit_split)||pct(F.profit_split);if(s)fill('p-split',s);const md=parseInt(p.min_trading_days||F.min_trading_days);fill('p-min',isFinite(md)?md:0);calc()});
  root.addEventListener('input',calc);calc();
}
})();
