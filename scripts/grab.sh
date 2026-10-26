#!/bin/zsh
# usage: grab.sh <label> <outname> <url> [<outname> <url> ...]  — dumps page innerText to data/scrape/<outname>.txt
L=$1; shift
D=~/.openclaw/workspace-samantha/propfirmanalyse/data/scrape; mkdir -p $D
openclaw browser open about:blank --label $L >/dev/null 2>&1
while [ $# -gt 1 ]; do
  openclaw browser navigate "$2" --target-id $L >/dev/null 2>&1; sleep 9
  openclaw browser evaluate --target-id $L --fn 'return location.href+"\n"+document.title+"\n"+document.body.innerText.slice(0,40000)' > $D/$1.txt 2>&1
  echo "$1 $(wc -c < $D/$1.txt)"; shift 2
done
