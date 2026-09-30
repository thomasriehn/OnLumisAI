#!/usr/bin/env bash
set -euo pipefail
release=/home/claude/onlumis-site/releases/20260930-redesign
backup=/home/claude/onlumis-site/backups/onlumis.service.before-redesign
# Run only after the preview and direct-file access checks have passed.
curl --fail --silent --max-time 15 http://127.0.0.1:3100/ > /dev/null
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
  echo 'New website is active and its homepage passed the health check.'
  sudo systemctl stop onlumis-preview
  exit 0
 fi
 sleep 1
done
sudo cp "$backup" /etc/systemd/system/onlumis.service
sudo systemctl daemon-reload
sudo systemctl restart onlumis
echo 'Activation failed; original service restored.' >&2
exit 1
