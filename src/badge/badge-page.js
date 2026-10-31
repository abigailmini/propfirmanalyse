/* PropAnalyse badge builder, copy buttons, for-firms form (2026-10-31). No tracking. */
(function(){var d=document,$=function(s,r){return(r||d).querySelector(s)};
d.addEventListener("click",function(ev){var b=ev.target.closest(".bcopy");if(!b)return;var c=d.getElementById(b.dataset.target);if(!c)return;
var t=c.textContent,s=b.querySelector("span"),done=function(){if(!b.dataset.o)b.dataset.o=s.textContent;s.textContent=b.dataset.done||"Copied";b.classList.add("ok");clearTimeout(b._t);b._t=setTimeout(function(){s.textContent=b.dataset.o;b.classList.remove("ok")},1600)};
if(navigator.clipboard&&window.isSecureContext)navigator.clipboard.writeText(t).then(done,function(){sel(c);done()});else{sel(c);try{d.execCommand("copy")}catch(e){}done()}});
function sel(c){var r=d.createRange();r.selectNodeContents(c);var s=getSelection();s.removeAllRanges();s.addRange(r)}
var B=$("#bbuild");if(B){var A=B.dataset.abs,BASE=B.dataset.base,F=window.PA_BADGES||{},L=window.PA_L||{},f=$("#b-firm"),code=$("#b-code"),lab=$("#b-code-l"),img=$("#b-prev"),pa=$("#b-prev-a"),stage=$("#b-stage"),
W={standard:[300,116],compact:[240,48]},
q=new URLSearchParams(location.search);if(q.get("firm")&&F[q.get("firm")])f.value=q.get("firm");
["theme","size","kind"].forEach(function(k){var v=q.get(k),r=v&&B.querySelector('input[name='+k+'][value="'+v+'"]');if(r)r.checked=true});
function val(n){var r=B.querySelector("input[name="+n+"]:checked");return r?r.value:""}
function esc(s){return s.replace(/&/g,"&amp;").replace(/"/g,"&quot;").replace(/</g,"&lt;")}
function upd(push){var s=f.value,x=F[s],t=val("theme"),z=val("size"),k=val("kind"),wh=W[z],name=x[0],alt=name+" on PropAnalyse: PA Score "+x[1].toFixed(1)+"/10",
file=s+(z=="compact"?"-compact":"")+(t=="light"?"":"-"+t)+".svg",href=A+"/firms/"+s+"/?ref=badge";
img.src=BASE+"/badge/"+file;img.width=wh[0];img.height=wh[1];img.alt=alt;pa.href=BASE+"/firms/"+s+"/";
if(t=="auto")stage.dataset.bg=matchMedia("(prefers-color-scheme:dark)").matches?"d":"l";else stage.dataset.bg=val("bg");
code.textContent=k=="js"?'<a class="propanalyse-badge" data-theme="'+t+'" data-size="'+z+'" href="'+href+'">'+esc(name)+' on PropAnalyse</a>\n<script async src="'+A+'/badge/widget.js"></'+'script>'
:'<a href="'+href+'" title="'+esc(name)+' on PropAnalyse"><img src="'+A+"/badge/"+file+'" width="'+wh[0]+'" height="'+wh[1]+'" alt="'+esc(alt)+'" loading="lazy" style="border:0;max-width:100%;height:auto"></a>';
if(lab)lab.textContent=k=="js"?L.code_js:L.code_html;
if(push){var u=new URL(location.href);u.searchParams.set("firm",s);["theme","size","kind"].forEach(function(n){var v=val(n),dflt={theme:"light",size:"standard",kind:"html"}[n];v==dflt?u.searchParams.delete(n):u.searchParams.set(n,v)});history.replaceState(null,"",u)}}
B.addEventListener("change",function(ev){if(ev.target.name=="bg"){stage.dataset.bg=val("bg");return}upd(true)});upd(false)}
var FF=$("#ffform");if(FF){var g=function(i){return($("#"+i).value||"").trim()};
function msg(){var t=g("ff-type"),fm=g("ff-firm")||"(firm)",sub="["+t+"] "+fm,body="Request: "+t+"\nFirm: "+fm+"\nWhat is wrong or missing: "+g("ff-field")+"\nCorrect value: "+g("ff-value")+"\nSource URL: "+g("ff-src")+"\nNotes: "+g("ff-notes")+"\n";
$("#ff-mail").href="mailto:"+FF.dataset.to+"?subject="+encodeURIComponent(sub)+"&body="+encodeURIComponent(body);
$("#ff-gh").href=FF.dataset.gh+"?title="+encodeURIComponent(sub)+"&body="+encodeURIComponent(body)}
FF.addEventListener("input",msg);FF.addEventListener("change",msg);msg()}})();
