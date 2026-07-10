#!/usr/bin/env bash
# OnLumis-Restore (AP 6.2): stellt ein Backup aus backup.sh wieder her.
#
#   ./restore.sh /var/backups/onlumis/20260710-020000
#
# ACHTUNG: überschreibt den aktuellen Datenbestand. Der Stack (außer Postgres)
# wird während des Restores gestoppt.
set -euo pipefail

SOURCE="${1:?Nutzung: ./restore.sh <backup-verzeichnis>}"
PLATFORM_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
COMPOSE="docker compose --project-directory $PLATFORM_DIR"

[ -f "$SOURCE/postgres.sql.gz" ] || { echo "FEHLER: $SOURCE/postgres.sql.gz fehlt"; exit 1; }

echo "1/4 Anwendungs-Dienste stoppen (Postgres bleibt oben) ..."
$COMPOSE stop api ingestion webapp keycloak proxy 2>/dev/null || true

echo "2/4 Datenbanken einspielen (drop + recreate) ..."
$COMPOSE exec -T postgres psql -U onlumis -d postgres -v ON_ERROR_STOP=0 \
  -c "DROP DATABASE IF EXISTS onlumis WITH (FORCE);" \
  -c "DROP DATABASE IF EXISTS keycloak WITH (FORCE);"
gunzip -c "$SOURCE/postgres.sql.gz" | $COMPOSE exec -T postgres psql -U onlumis -d postgres

echo "3/4 Uploads-Volume ..."
if [ -f "$SOURCE/uploads.tgz" ]; then
  docker run --rm -v onlumis_uploads:/data -v "$SOURCE":/backup:ro alpine \
    sh -c "rm -rf /data/* && tar xzf /backup/uploads.tgz -C /data"
fi
if [ -f "$SOURCE/adapters.tgz" ]; then
  tar xzf "$SOURCE/adapters.tgz" -C "$PLATFORM_DIR/finetune"
fi

echo "4/4 Stack wieder starten ..."
$COMPOSE up -d

echo "OK: Restore aus $SOURCE abgeschlossen. Bitte Smoke-Test laufen lassen"
echo "    (RUNBOOK.md, Abschnitt 'Smoke-Checks')."
