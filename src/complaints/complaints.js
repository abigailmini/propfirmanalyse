/* PropAnalyse complaint form: builds a prefilled email or GitHub issue. Nothing is sent to or stored by PropAnalyse's site. */
(function(){var $=function(s){return document.querySelector(s)};var F=$("#cpform");if(!F)return;
var zh=F.dataset.lang=="zh",g=function(i){var el=$("#"+i);return el?(el.value||"").trim():""};
var p=new URLSearchParams(location.search).get("firm");if(p){var o=F.querySelector('#cp-firm option[value="'+p.replace(/[^a-z0-9-]/g,"")+'"]');if(o)o.selected=true}
function lab(id){var el=$("#"+id);if(!el)return"";var s=el.selectedIndex!=null&&el.options?el.options[el.selectedIndex]:null;return s?s.dataset.en||s.textContent:""}
function body(pub){var L=["Firm: "+lab("cp-firm")+(g("cp-firm")?" ("+g("cp-firm")+")":""),"Issue type: "+lab("cp-type"),"Date of the problem: "+(g("cp-date")||"-"),
pub?"Trader email: (sent privately by email, not in this public issue)":"Trader email: "+g("cp-email"),pub?"Account / order ID: (sent privately)":"Account / order ID: "+(g("cp-acct")||"-"),
"","What happened:",g("cp-desc")||"-","","Evidence links (screenshots, emails, tx hashes):",g("cp-ev")||"-","","I confirm this is my own account and the facts are true to my knowledge.","Submitted via "+location.origin+location.pathname];return L.join("\n")}
function sub(){return"[Complaint] "+(lab("cp-firm")||"Firm")+": "+lab("cp-type")}
function upd(){$("#cp-mail").href="mailto:"+F.dataset.to+"?subject="+encodeURIComponent(sub())+"&body="+encodeURIComponent(body(false));
$("#cp-gh").href=F.dataset.gh+"?labels=complaint&title="+encodeURIComponent(sub())+"&body="+encodeURIComponent(body(true))}
function ok(ev,pub){var miss=[];["cp-firm","cp-type","cp-desc"].concat(pub?[]:["cp-email"]).forEach(function(i){var el=$("#"+i);var bad=!g(i)||(i=="cp-email"&&!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(g(i)));el.setAttribute("aria-invalid",bad?"true":"false");if(bad)miss.push(el)});
var c=$("#cp-ok");if(c&&!c.checked){miss.push(c)}var m=$("#cp-msg");if(miss.length){ev.preventDefault();m.textContent=zh?"请填写标记的必填项并勾选确认。":"Please fill in the highlighted required fields and tick the confirmation.";m.hidden=false;miss[0].focus();return}m.hidden=true;upd()}
F.addEventListener("input",upd);F.addEventListener("change",upd);$("#cp-mail").addEventListener("click",function(e){ok(e,false)});$("#cp-gh").addEventListener("click",function(e){ok(e,true)});upd()})();
