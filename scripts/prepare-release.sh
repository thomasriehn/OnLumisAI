#!/usr/bin/env bash
set -euo pipefail
release=${RELEASE_DIR:?Set RELEASE_DIR to the candidate release}
shared=/home/claude/onlumis-site/shared
cd "$release"
test -f .next/standalone/server.js
for font in OnLumisLogoStrong.ttf OnLumisLogoLight.ttf; do
 test -s ".next/standalone/src/assets/fonts/$font" || { echo "Standalone font missing: $font" >&2; exit 1; }
done
test -s .next/standalone/node_modules/next/dist/compiled/@vercel/og/Geist-Regular.ttf
mkdir -p .next/standalone/.next/static
cp -a .next/static/. .next/standalone/.next/static/
cp -a public .next/standalone/
cp -a "$shared/media/." .next/standalone/public/media/
sudo systemd-run --unit=onlumis-preview --property=User=claude --property=Group=claude --property=NoNewPrivileges=true --property="EnvironmentFile=$shared/.env" --working-directory="$release/.next/standalone" --setenv=PORT=3100 --setenv=HOSTNAME=127.0.0.1 /usr/bin/node "$release/.next/standalone/server.js"
