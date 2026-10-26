#!/bin/sh
# Render scripts/og.html -> src/og.png (1200x630). Needs Google Chrome.
cd "$(dirname "$0")/.." || exit 1
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
"$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --window-size=1200,630 \
  --screenshot="$PWD/src/og.png" "file://$PWD/scripts/og.html" && echo "wrote src/og.png"
