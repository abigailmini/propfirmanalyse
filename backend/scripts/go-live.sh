#!/bin/sh
# One-command switch: verify the Worker answers with 302s, then rebuild the live site with TRACK=1.
# Usage: backend/scripts/go-live.sh            (rollback: backend/scripts/go-live.sh off)
set -eu
REPO=abigailmini/propfirmanalyse
GO=${GO_URL:-https://go.propanalyse.com}
if [ "${1:-}" = "off" ]; then
  gh variable delete TRACK -R "$REPO" || true
  gh workflow run pages.yml -R "$REPO"; echo "Tracking OFF, site rebuilding."; exit 0
fi
# HEAD requests are bot-filtered by the Worker, so this check is never counted as a click.
loc=$(curl -sI "$GO/ftmo?src=/go-live-check" | awk 'tolower($1)=="location:"{print $2}' | tr -d '\r')
code=$(curl -sI -o /dev/null -w '%{http_code}' "$GO/ftmo")
case "$code:$loc" in 302:https://*ftmo.com*) echo "OK: $GO/ftmo -> $loc" ;; *) echo "ABORT: $GO/ftmo returned $code $loc (Worker not live yet)"; exit 1 ;; esac
[ "$(curl -s "$GO/health" | grep -c '"ok":true')" = 1 ] || { echo "ABORT: /health not ok"; exit 1; }
gh variable set TRACK --body 1 -R "$REPO"
[ "$GO" = "https://go.propanalyse.com" ] || gh variable set GO_URL --body "$GO" -R "$REPO"
gh workflow run pages.yml -R "$REPO"
echo "Tracking ON: Pages is rebuilding with TRACK=1 (about 1-2 min). Dashboard: $GO/admin"
