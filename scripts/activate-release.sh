#!/usr/bin/env bash
set -euo pipefail
release=${RELEASE_DIR:?Set RELEASE_DIR to the candidate release}
backup=/home/claude/onlumis-site/backups/onlumis.service.before-$(basename "$release")
cd "$release"
# Exercise authenticated rendering in the real standalone preview before switching traffic.
curl --fail --silent --max-time 15 http://127.0.0.1:3100/ > /dev/null
TEST_ENV_FILE=/home/claude/onlumis-site/shared/.env TEST_BASE_URL=http://127.0.0.1:3100 node tests/access-check.mjs
if ! test -f "$backup"; then sudo cp /etc/systemd/system/onlumis.service "$backup"; fi
sudo tee /etc/systemd/system/onlumis.service > /dev/null <<UNIT
[Unit]
Description=OnLumisAI Website and protected Demo-Studio
After=network.target

[Service]
Type=simple
User=claude
Group=claude
WorkingDirectory=$release/.next/standalone
EnvironmentFile=/home/claude/onlumis-site/shared/.env
Environment=PORT=3000
Environment=HOSTNAME=0.0.0.0
Environment=NODE_ENV=production
ExecStart=/usr/bin/node $release/.next/standalone/server.js
Restart=on-failure
RestartSec=3
NoNewPrivileges=true
PrivateTmp=true
UMask=0027

[Install]
WantedBy=multi-user.target
UNIT
sudo systemctl daemon-reload
sudo systemctl restart onlumis
for attempt in {1..20}; do
 if curl --fail --silent --max-time 3 http://127.0.0.1:3000/ -o /home/claude/onlumis-site/backups/activation-health.html && grep -q 'Ihre Firma weiß viel' /home/claude/onlumis-site/backups/activation-health.html; then
  if TEST_ENV_FILE=/home/claude/onlumis-site/shared/.env TEST_BASE_URL=http://127.0.0.1:3000 node tests/access-check.mjs; then
   echo 'New website is active; authenticated library, media and OG checks passed.'
   sudo systemctl stop onlumis-preview
   exit 0
  fi
  break
 fi
 sleep 1
done
sudo cp "$backup" /etc/systemd/system/onlumis.service
sudo systemctl daemon-reload
sudo systemctl restart onlumis
echo 'Activation failed; original service restored.' >&2
exit 1
