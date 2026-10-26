#!/bin/zsh
# usage: recon.sh <name> <url>
cd ~/.openclaw/workspace-samantha/propfirmanalyse/docs/recon
openclaw browser navigate "$2" --target-id pfm >/dev/null 2>&1
sleep 8
openclaw browser evaluate --target-id pfm --fn '
window.scrollTo(0,document.body.scrollHeight);
const q=(s)=>[...document.querySelectorAll(s)];
const t=(e)=>(e.innerText||"").trim().replace(/\s+/g," ").slice(0,90);
return JSON.stringify({
 title:document.title, url:location.href,
 meta:(document.querySelector("meta[name=description]")||{}).content,
 h:q("h1,h2,h3").map(e=>e.tagName+": "+t(e)).slice(0,80),
 th:q("th,[role=columnheader]").map(t).filter(Boolean).slice(0,60),
 buttons:[...new Set(q("button").map(t).filter(x=>x&&x.length<40))].slice(0,120),
 links:[...new Set(q("a[href]").map(a=>a.getAttribute("href")).filter(h=>h&&h.startsWith("/")||h.includes("propfirmmatch.com")))].slice(0,250),
 ld:q("script[type=\"application/ld+json\"]").map(s=>{try{const j=JSON.parse(s.textContent);return [].concat(j).map(x=>x["@type"]).join(",")}catch(e){return "err"}}),
 footer:t(document.querySelector("footer")||document.body).slice(-0)? (document.querySelector("footer")?document.querySelector("footer").innerText.replace(/\s+/g," ").slice(0,2500):""):"",
 bodyLen:document.body.innerText.length,
 body:document.body.innerText.replace(/\n{2,}/g,"\n").slice(0,6000)
});' > "$1.json" 2>&1
wc -c "$1.json"
