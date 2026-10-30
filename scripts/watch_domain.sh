#!/bin/zsh
# Poll until propanalyse.com points at GitHub Pages, cert is issued, then enforce HTTPS. Max ~8h.
R=abigailmini/propfirmanalyse
for i in {1..240}; do
  A=$(dig +short @ns49.domaincontrol.com propanalyse.com A | sort | tr '\n' ' ')
  if [[ "$A" == *185.199.10* ]]; then
    gh api -X PUT repos/$R/pages -f cname=propanalyse.com >/dev/null 2>&1  # nudge verification/cert
    for j in {1..60}; do
      S=$(gh api repos/$R/pages --jq '.https_certificate.state // "none"')
      if [[ "$S" == "approved" || "$S" == "issued" ]]; then
        gh api -X PUT repos/$R/pages -F https_enforced=true >/dev/null 2>&1
        C=$(curl -s -o /dev/null -w "%{http_code}" https://propanalyse.com/)
        echo "DONE dns=[$A] cert=$S https_enforced=$(gh api repos/$R/pages --jq .https_enforced) live_https=$C"; exit 0
      fi
      sleep 120
    done
    echo "DNS_OK_CERT_PENDING dns=[$A] cert=$S"; exit 2
  fi
  sleep 120
done
echo "TIMEOUT dns still [$A]"; exit 1
