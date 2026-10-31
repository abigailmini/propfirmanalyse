/*! PropAnalyse badge | no cookies, no tracking | stars = score/2 */
(function(){var A="__ABS__",d=document,P,
T={light:["#fff","#d5dae3","#0b1730","#5a6680","#3424f8","#3424f8","#d5d9e2"],dark:["#18233a","#3a4968","#eef1f8","#a3adc4","#9a94ff","#8f88ff","#3a4968"]};
function V(t){var c=T[t];return"--bg:"+c[0]+";--ln:"+c[1]+";--ink:"+c[2]+";--mu:"+c[3]+";--ac:"+c[4]+";--mk:"+c[5]+";--off:"+c[6]}
function E(s){return String(s).replace(/[&<>"]/g,function(c){return"&#"+c.charCodeAt(0)+";"})}
var S='<svg viewBox="-16 0 288 256"><path d="__STAR__"/></svg>',M='<svg class="mk" viewBox="0 0 141 96"><path d="__MARK__"/></svg>';
function st(s){var k=s/2,n=Math.floor(k),p=k-n,w=(n*288+(p>0?16+p*256:0))/14.4,x=S+S+S+S+S;
return'<span class="st"><span class="o">'+x+'</span><span class="f" style="width:'+w.toFixed(2)+'%">'+x+"</span></span>"}
var C=":host{all:initial;display:inline-block;max-width:100%}.c{box-sizing:border-box;font:13px/1.25 'Instrument Sans',system-ui,-apple-system,'Segoe UI',Roboto,Arial,sans-serif;background:var(--bg);border:1px solid var(--ln);border-radius:10px;color:var(--ink);max-width:100%;text-align:left;font-variant-numeric:tabular-nums}"+
".s{width:300px;height:116px;padding:11px 16px 8px;display:block}.p{width:240px;height:48px;padding:0 12px;display:flex;gap:10px;align-items:center;white-space:nowrap}"+
".mk{fill:var(--mk);height:18px;width:26px;flex:none}.p .mk{height:22px;width:32px}.h{display:flex;align-items:center;gap:6px;height:20px;font-size:12.5px;font-weight:700}.h i{margin-left:auto;font-size:11px;font-weight:400;font-style:normal;color:var(--mu)}"+
".n{font-size:15.5px;font-weight:600;line-height:20px;margin-top:9px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.r{display:flex;align-items:center;justify-content:space-between;gap:8px;height:34px}"+
".sc b{font-size:28px;line-height:1;font-weight:700;letter-spacing:-.4px}.sc small{font-size:13px;color:var(--mu);font-weight:500;margin-left:2px}.p .sc b{font-size:15px}.p .sc small{font-size:11px;margin:0}"+
".st{position:relative;display:inline-block;line-height:0}.st span{display:inline-flex;white-space:nowrap}.st svg{width:19.5px;height:17px}.p .st svg{width:15.5px;height:13px}"+
".o svg{fill:var(--off)}.f{position:absolute;left:0;top:0;overflow:hidden}.f svg{fill:var(--ac);flex:none}.v{font-size:10.5px;line-height:14px;color:var(--mu)}.p .v{font-size:10px;line-height:13px}.p .r{justify-content:flex-start;gap:10px;height:20px}"+
"@media (prefers-color-scheme:dark){.au{"+V("dark")+"}}";
function R(a,f){var t=a.getAttribute("data-theme"),z=a.getAttribute("data-size")=="compact",s=f.s,
v=(z?"PropAnalyse \u00b7 ":"PA Score \u00b7 ")+"Verified "+E(f.vd)+(f.x?" \u00b7 re-check due":""),
sc='<span class="sc"><b>'+s.toFixed(1)+"</b><small>/10</small></span>",
h=z?'<div class="c p">'+M+'<div><div class="r">'+sc+st(s)+'</div><div class="v">'+v+"</div></div></div>"
:'<div class="c s"><div class="h">'+M+"PropAnalyse<i>"+E(f.c)+'</i></div><div class="n">'+E(f.n)+'</div><div class="r">'+sc+st(s)+'</div><div class="v">'+v+"</div></div>",
w=d.createElement("span");while(a.firstChild)w.appendChild(a.firstChild);
var r=w.attachShadow({mode:"open"});r.innerHTML="<style>.c{"+V(t=="dark"?"dark":"light")+"}"+C+"</style>"+h.replace('class="c ','class="c '+(t=="auto"?"au ":""));
a.appendChild(w);a.style.textDecoration="none";a.style.display="inline-block";a.style.maxWidth="100%";
a.setAttribute("aria-label",f.n+" on PropAnalyse: PA Score "+s.toFixed(1)+"/10, verified "+f.vd);a.setAttribute("data-pa-done","1")}
function go(){var L=d.querySelectorAll("a.propanalyse-badge:not([data-pa-done])");if(!L.length)return;
P=P||fetch(A+"/badge/badges.json",{credentials:"omit"}).then(function(r){return r.json()});
P.then(function(j){for(var i=0;i<L.length;i++){var a=L[i],m=/\/firms\/([^\/?#]+)/.exec(a.getAttribute("href")||""),f=m&&j.firms[m[1]];if(f&&!a.hasAttribute("data-pa-done"))R(a,f)}})["catch"](function(){})}
window.PropAnalyseBadge={render:go};d.readyState=="loading"?d.addEventListener("DOMContentLoaded",go):go()})();
